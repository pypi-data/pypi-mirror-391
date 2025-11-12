#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成证件照 MCP 服务器（基于阿里云人体分割 + 人脸关键点）
功能：
- 提供一个工具：输入 `image_url`（必填，支持公网 URL 或本地路径），可选 `bg`、`spec`。
- 使用阿里云图像分割（imageseg 2019-12-30）获取透明前景图；
- 使用阿里云人脸（facebody 2019-12-30）获取 105 个关键点，进行人脸对齐与半身构图裁剪；
- 将前景合成到指定背景色，并按目标尺寸输出；
- 最终上传到 OSS 并返回文件 URL。
"""

import logging
import os
import time
import json
import tempfile
from typing import Literal, Tuple, List, Dict
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import uuid
import math
import hmac
import hashlib
import base64
from datetime import datetime
from urllib.parse import quote
import io

import cv2
import numpy as np
from mcp.server.fastmcp import FastMCP
from alibabacloud_imageseg20191230.client import Client as ImagesegClient
from alibabacloud_facebody20191230.client import Client as FacebodyClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_imageseg20191230 import models as imageseg_models
from alibabacloud_facebody20191230 import models as facebody_models
from alibabacloud_tea_util import models as util_models

# 配置日志
logging.basicConfig(
    level=logging.INFO if os.getenv("MCP_DEBUG") == "1" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建 FastMCP 服务器实例
mcp = FastMCP("证件照生成")

# 上传API（参考 typescript/文件上传下载/src/index.ts）
UPLOAD_API_URL = "https://www.mcpcn.cc/api/fileUploadAndDownload/uploadMcpFile"

# 为外部HTTP请求统一设置请求头，避免部分站点对默认Python UA返回403
DEFAULT_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0 Safari/537.36"
    ),
    "Accept": "*/*",
}


def _get_ali_credentials() -> Tuple[str, str]:
    """获取阿里云 AK/SK，支持多种环境变量名。
    优先顺序：
    - `ALI_ACCESS_KEY_ID` / `ALI_ACCESS_KEY_SECRET`
    - `ALIBABA_CLOUD_ACCESS_KEY_ID` / `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
    - `ACCESS_KEY_ID` / `ACCESS_KEY_SECRET`
    """
    ak = os.getenv("ALI_ACCESS_KEY_ID") or os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID") or os.getenv("ACCESS_KEY_ID")
    sk = os.getenv("ALI_ACCESS_KEY_SECRET") or os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET") or os.getenv("ACCESS_KEY_SECRET")
    # 清理可能的空格与包裹字符，避免签名计算因非法字符失败
    ak = (ak or "").strip().strip("`'\"")
    sk = (sk or "").strip().strip("`'\"")
    if not ak or not sk:
        raise ValueError("未配置阿里云 AK/SK。请设置环境变量 ALI_ACCESS_KEY_ID/ALI_ACCESS_KEY_SECRET。")
    return ak, sk


def _create_aliyun_clients(ak: str, sk: str) -> Tuple[ImagesegClient, FacebodyClient]:
    """使用阿里云官方 SDK 初始化 Imageseg 与 Facebody 客户端。

    - 读取 `ALI_REGION`，默认 `cn-shanghai`；
    - 通过 Tea OpenAPI 的 Config 设置 endpoint；
    - 返回两个 SDK 客户端实例。
    """
    region = os.getenv("ALI_REGION", "cn-shanghai").strip() or "cn-shanghai"
    seg_config = open_api_models.Config(access_key_id=ak, access_key_secret=sk)
    face_config = open_api_models.Config(access_key_id=ak, access_key_secret=sk)
    seg_config.endpoint = f"imageseg.{region}.aliyuncs.com"
    face_config.endpoint = f"facebody.{region}.aliyuncs.com"
    return ImagesegClient(seg_config), FacebodyClient(face_config)


def _spec_to_size(spec: str) -> Tuple[int, int]:
    """常用证件照规格映射为像素尺寸（px）
    - 一寸：295×413 px（25×35 mm @ 300dpi）
    - 二寸-标准：413×531 px（35×45 mm @ 300dpi）
    - 二寸-大：413×579 px（35×49 mm @ 300dpi）
    """
    mapping = {
        "一寸": (295, 413),
        "二寸-标准": (413, 531),
        "二寸-大": (413, 579),
    }
    if spec not in mapping:
        raise ValueError(f"不支持的规格：{spec}")
    return mapping[spec]


def _parse_size_str(size: str) -> Tuple[int, int]:
    """解析像素尺寸字符串，支持格式："宽*高"、"宽x高"（大小写均可）。
    例如："295*413" 或 "295x413" -> (295, 413)
    """
    s = size.strip().lower().replace("×", "x")
    if "*" in s:
        parts = s.split("*")
    elif "x" in s:
        parts = s.split("x")
    else:
        raise ValueError("size 格式不正确，应为 '宽*高' 或 '宽x高'，例如 '295*413'")
    if len(parts) != 2:
        raise ValueError("size 解析失败，应包含两个数值：宽与高")
    try:
        w = int(parts[0].strip())
        h = int(parts[1].strip())
    except Exception:
        raise ValueError("size 中包含非整数数值，请使用如 '295*413' 的格式")
    if w <= 0 or h <= 0:
        raise ValueError("size 的宽高必须为正整数")
    return (w, h)


def _bg_to_bgr(bg: str) -> Tuple[int, int, int, int]:
    """背景色到 OpenCV BGR(A) 的映射（沿用 idcard.py 的取值）。"""
    bg = bg.lower()
    colors = {
        # 输入为 RGB：white(255,255,255), blue(0,85,170), red(220,0,0)
        # OpenCV 需使用 BGR 顺序
        "white": (255, 255, 255, 255),          # RGB(255,255,255) -> BGR(255,255,255)
        "blue": (170, 85, 0, 255),              # RGB(0,85,170)   -> BGR(170,85,0)
        "red": (0, 0, 220, 255),                # RGB(220,0,0)    -> BGR(0,0,220)
    }
    if bg not in colors:
        raise ValueError(f"不支持的背景色：{bg}")
    return colors[bg]


def _align_face(image_array: np.ndarray, landmarks: np.ndarray):
    """根据双眼位置进行人脸对齐，返回旋转后图像与新的关键点。"""
    landmarks = np.resize(landmarks, (105, 2))

    left_eye = landmarks[24:39]
    right_eye = landmarks[40:55]
    left_eye_center = np.mean(left_eye, axis=0).astype("int32")
    right_eye_center = np.mean(right_eye, axis=0).astype("int32")
    dy = right_eye_center[1] - left_eye_center[1]
    dx = right_eye_center[0] - left_eye_center[0]
    angle = math.atan2(dy, dx) * 180.0 / math.pi
    eye_center = (int(left_eye_center[0] + right_eye_center[0]) // 2, int(left_eye_center[1] + right_eye_center[1]) // 2)
    rotate_matrix = cv2.getRotationMatrix2D(eye_center, angle, scale=1)
    rotated_img = cv2.warpAffine(image_array, rotate_matrix, (image_array.shape[1], image_array.shape[0]))

    def _rotate(origin, point, angle_deg, row):
        x1, y1 = point
        x2, y2 = origin
        y1 = row - y1
        y2 = row - y2
        angle_rad = math.radians(angle_deg)
        x = x2 + math.cos(angle_rad) * (x1 - x2) - math.sin(angle_rad) * (y1 - y2)
        y = y2 + math.sin(angle_rad) * (x1 - x2) + math.cos(angle_rad) * (y1 - y2)
        y = row - y
        return int(x), int(y)

    rotated_landmarks = []
    for landmark in landmarks:
        rotated_landmark = _rotate(origin=eye_center, point=landmark, angle_deg=angle, row=image_array.shape[0])
        rotated_landmarks.append(rotated_landmark)
    return rotated_img, eye_center, angle, rotated_landmarks


def _corp_halfbody(image_array: np.ndarray, landmarks: List[Tuple[int, int]], size: Tuple[int, int]) -> np.ndarray:
    """根据关键点裁剪半身并生成 RGBA 结果（参考 idcard.py）。"""
    width, height = size
    crop_size = [0, 0, height, width]

    landmarks_np = np.array(landmarks)
    scal = height / 4 / abs(landmarks_np[98][1] - landmarks_np[56][1])
    image = cv2.resize(image_array, np.multiply((image_array.shape[0:2])[::-1], scal).astype(int))
    landmarks_np = np.multiply(landmarks_np, scal)

    x_center = int(landmarks_np[98][0])
    crop_size[0:2] = [x_center - width / 2, x_center + width / 2]

    y_center = (landmarks_np[98][1] + landmarks_np[56][1]) / 2
    crop_size[2:4] = [y_center - height / 2, y_center + height / 2]

    # 计算实际裁剪区域并从缩放后图像裁剪
    left_i, right_i, top_i, bottom_i = [round(i) for i in crop_size]
    left_i = max(0, left_i)
    top_i = max(0, top_i)
    right_i = min(image.shape[1], right_i)
    bottom_i = min(image.shape[0], bottom_i)

    cropped_img = image[top_i:bottom_i, left_i:right_i]

    # 若裁剪结果为空，回退为居中填充逻辑
    if cropped_img.size == 0:
        cropped_img = np.zeros((min(height, image.shape[0]), min(width, image.shape[1]), image.shape[2]), dtype=image.dtype)

    # 目标画布放置位置（顶部对齐到底部，水平按原逻辑向右偏移）
    # 原逻辑：bottom = height; top = height - cropped_img.shape[0]
    dest_top = max(0, height - cropped_img.shape[0])
    # 原逻辑：left = -min(0, left)
    dest_left = max(0, -min(0, left_i))

    # 计算可放置宽高，避免切片与源宽高不一致导致广播失败
    place_w = max(0, min(cropped_img.shape[1], width - dest_left))
    place_h = max(0, min(cropped_img.shape[0], height - dest_top))

    # 仅当 place_w/place_h 为正时进行合成
    png_img = np.zeros((height, width, 4), dtype=image.dtype)
    if place_w > 0 and place_h > 0:
        png_img[dest_top:dest_top + place_h, dest_left:dest_left + place_w] = cropped_img[:place_h, :place_w]

    return png_img


def _image_merge_background(sc_image: np.ndarray, png_image: np.ndarray, bg_image: np.ndarray) -> np.ndarray:
    """将前景合成到背景图（参考 idcard.py）。"""
    assert (sc_image is not None and png_image is not None and bg_image is not None), "read image input error!"
    h, w, c = sc_image.shape

    viapi_image = cv2.resize(png_image, (w, h))
    bg_image = cv2.resize(bg_image, (w, h))
    if len(viapi_image.shape) == 2:
        mask = viapi_image[:, :, np.newaxis]
    elif viapi_image.shape[2] == 4:
        mask = viapi_image[:, :, 3:4]
    elif viapi_image.shape[2] == 3:
        mask = viapi_image[:, :, 0:1]
    else:
        raise Exception("invalid image mask!")
    mask = mask / 255.0

    sc_image = sc_image.astype(float)
    bg_image = bg_image.astype(float)
    rst_image = (sc_image - bg_image) * mask + bg_image
    rst_image = np.clip(rst_image, 0, 255)
    return rst_image.astype(np.uint8)


def _ensure_http_image_url(image_or_path: str) -> str:
    """确保输入为可公网访问的URL。

    - 若输入为本地路径：上传到 OSS，返回可访问URL；
    - 若输入为 http/https：主动下载到本地并重传到 OSS，规避防盗链/UA限制导致的403。
    """
    # 清理首尾反引号/引号，避免URL被包裹导致解析/下载失败
    s = _clean_url(image_or_path or "")
    if s.lower().startswith("http://") or s.lower().startswith("https://"):
        # 远程URL：先下载到本地，再上传到OSS以提升可访问性
        try:
            temp_path = _download_image_to_temp(s)
            try:
                return _upload_file_to_oss(temp_path)
            finally:
                try:
                    if os.path.isfile(temp_path):
                        os.remove(temp_path)
                except Exception:
                    logger.warning(f"删除临时下载文件失败: {temp_path}")
        except Exception as e:
            raise RuntimeError(f"输入图片URL下载失败或被限制访问(防盗链/403)：{e}")
    # 本地文件：上传到OSS
    if not os.path.isfile(s):
        raise ValueError(f"本地图片不存在：{s}")
    return _upload_file_to_oss(s)


def _resolve_image_to_local_file(image_or_path: str) -> str:
    """将输入的本地路径或远程URL统一解析为本地文件路径。

    - 远程URL：下载到临时文件并返回路径（调用方需负责删除临时文件）；
    - 本地路径：校验存在后返回路径。
    """
    # 清理首尾反引号/引号，避免URL被包裹导致下载失败
    s = _clean_url(image_or_path or "")
    if s.lower().startswith("http://") or s.lower().startswith("https://"):
        return _download_image_to_temp(s)
    if not os.path.isfile(s):
        raise ValueError(f"本地图片不存在：{s}")
    return s


def _utc_iso8601() -> str:
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def _percent_encode(s: str) -> str:
    """符合阿里云RPC签名的编码：空格->%20，*->%2A，~保留。"""
    res = quote(str(s), safe='-_.~')
    return res.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')


def _sign_rpc_request(params: Dict[str, str], access_key_secret: str, method: str = 'GET') -> str:
    """生成阿里云RPC风格签名字符串。"""
    sorted_params = sorted((k, params[k]) for k in params.keys())
    canonicalized = '&'.join(f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in sorted_params)
    string_to_sign = f"{method}&%2F&{_percent_encode(canonicalized)}"
    key = (access_key_secret + '&').encode('utf-8')
    h = hmac.new(key, string_to_sign.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(h.digest()).decode('utf-8')
    return _percent_encode(signature)


def _build_signed_url(endpoint: str, action: str, image_url: str, access_key_id: str, access_key_secret: str, version: str = '2019-12-30') -> str:
    region = os.getenv("ALI_REGION", "cn-shanghai")
    params = {
        'Format': 'JSON',
        'AccessKeyId': access_key_id,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid4()),
        'Timestamp': _utc_iso8601(),
        'RegionId': region,
        'Action': action,
        'Version': version,
        'ImageURL': image_url,
    }
    signature = _sign_rpc_request(params, access_key_secret, method='GET')
    query = '&'.join(f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in params.items()) + f"&Signature={signature}"
    return endpoint.rstrip('/') + '/?' + query


def _rpc_call(endpoint: str, action: str, extra_params: Dict[str, str], access_key_id: str, access_key_secret: str, version: str = '2019-12-30', method: str = 'POST') -> bytes:
    """以RPC协议调用阿里云接口，支持POST方式。

    返回响应原始字节。
    """
    region = os.getenv("ALI_REGION", "cn-shanghai")
    base_params: Dict[str, str] = {
        'Format': 'JSON',
        'AccessKeyId': access_key_id,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid4()),
        'Timestamp': _utc_iso8601(),
        'RegionId': region,
        'Action': action,
        'Version': version,
    }
    params = {**base_params, **extra_params}
    # 计算签名与本地 string-to-sign，用于遇到签名不匹配时的排查
    sorted_params = sorted((k, params[k]) for k in params.keys())
    canonicalized = '&'.join(f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in sorted_params)
    local_string_to_sign = f"{method}&%2F&{_percent_encode(canonicalized)}"
    key = (access_key_secret + '&').encode('utf-8')
    h = hmac.new(key, local_string_to_sign.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(h.digest()).decode('utf-8')
    # 注意：不要在此对签名做百分号编码，交给 urlencode 统一编码。
    params_with_sig = {**params, 'Signature': signature}

    if method.upper() == 'GET':
        query = '&'.join(f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in params_with_sig.items())
        url = endpoint.rstrip('/') + '/?' + query
        req = Request(url, headers=DEFAULT_HTTP_HEADERS)
        return urlopen(req, timeout=30).read()
    else:
        # POST x-www-form-urlencoded
        body_str = '&'.join(f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in params_with_sig.items())
        body_bytes = body_str.encode('utf-8')
        headers = {**DEFAULT_HTTP_HEADERS, 'Content-Type': 'application/x-www-form-urlencoded'}
        req = Request(endpoint.rstrip('/') + '/', data=body_bytes, headers=headers, method='POST')
        try:
            return urlopen(req, timeout=30).read()
        except HTTPError as e:
            # 追加本地计算的 string-to-sign 与部分参数，便于快速定位签名不匹配的原因
            try:
                body = e.read().decode('utf-8', 'ignore')
            except Exception:
                body = ''
            # 屏蔽敏感信息，仅显示 AccessKeyId 的部分前后段以协助定位
            ak_mask = access_key_id[:4] + '...' + access_key_id[-4:] if len(access_key_id) > 8 else access_key_id
            raise RuntimeError(
                f"阿里云RPC调用失败: HTTP {e.code}: {body or e.reason}; "
                f"local_string_to_sign={local_string_to_sign}; ak={ak_mask}; region={region}; action={action}"
            )


def _segment_body_http(image_url: str, ak: str, sk: str) -> str:
    seg_client, _ = _create_aliyun_clients(ak, sk)
    runtime = util_models.RuntimeOptions()
    temp_path = None
    try:
        s = _clean_url(image_url or "")
        req = imageseg_models.SegmentHDBodyAdvanceRequest()
        if s.lower().startswith("http://") or s.lower().startswith("https://"):
            try:
                r = Request(s, headers=DEFAULT_HTTP_HEADERS)
                raw = urlopen(r, timeout=30).read()
                arr = np.frombuffer(raw, dtype="uint8")
                if cv2.imdecode(arr, cv2.IMREAD_UNCHANGED) is None:
                    raise RuntimeError("下载的内容不是有效图片")
                bio = io.BytesIO(raw)
                for field in [
                    'image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject'
                ]:
                    try:
                        setattr(req, field, bio)
                    except Exception:
                        pass
                res = seg_client.segment_hdbody_advance(req, runtime)
            except Exception:
                temp_path = _download_image_to_temp(s)
                with open(temp_path, 'rb') as f:
                    for field in [
                        'image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject'
                    ]:
                        try:
                            setattr(req, field, f)
                        except Exception:
                            pass
                    res = seg_client.segment_hdbody_advance(req, runtime)
        else:
            if not os.path.isfile(s):
                raise ValueError(f"本地图片不存在：{s}")
            with open(s, 'rb') as f:
                for field in [
                    'image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject'
                ]:
                    try:
                        setattr(req, field, f)
                    except Exception:
                        pass
                res = seg_client.segment_hdbody_advance(req, runtime)
        body = res.body
        data = getattr(body, 'data', None) or {}
        result_url = getattr(data, 'image_url', None) or getattr(data, 'ImageURL', None)
        if not result_url and isinstance(body, dict):
            d = body.get('Data') or body.get('data') or {}
            result_url = d.get('ImageURL') or d.get('image_url')
        if not result_url:
            raise RuntimeError(f"人体分割未返回图片URL: {body}")
        return result_url
    except Exception as e:
        msg = str(e)
        if ("MissingImageURL" in msg) or ("ImageURL is mandatory" in msg):
            try:
                http_url = _ensure_http_image_url(image_url)
                req2 = imageseg_models.SegmentHDBodyRequest(image_url=http_url)
                res2 = seg_client.segment_hdbody_with_options(req2, runtime)
                body2 = res2.body
                data2 = getattr(body2, 'data', None) or {}
                result_url2 = getattr(data2, 'image_url', None) or getattr(data2, 'ImageURL', None)
                if not result_url2 and isinstance(body2, dict):
                    d2 = body2.get('Data') or body2.get('data') or {}
                    result_url2 = d2.get('ImageURL') or d2.get('image_url')
                if not result_url2:
                    raise RuntimeError(f"人体分割未返回图片URL(回退URL)：{body2}")
                return result_url2
            except Exception as e2:
                raise RuntimeError(f"阿里云SegmentHDBody SDK 回退(URL)仍失败: {e2}")
        raise RuntimeError(f"阿里云SegmentBody SDK Advance调用失败: {e}")
    finally:
        try:
            if temp_path and os.path.isfile(temp_path):
                os.remove(temp_path)
        except Exception:
            logger.warning(f"删除临时下载文件失败: {temp_path}")


def _detect_face_http(image_url: str, ak: str, sk: str) -> List[Tuple[int, int]]:
    # 使用官方 SDK Advance 调用人脸关键点（以文件流传入，避免URL域名限制）
    _, face_client = _create_aliyun_clients(ak, sk)
    runtime = util_models.RuntimeOptions()
    temp_path = None
    try:
        # 优先使用 Advance（文件流）方式：远程URL用BytesIO，本地路径直接文件流
        s = _clean_url(image_url or "")
        req = facebody_models.DetectFaceAdvanceRequest()
        if s.lower().startswith("http://") or s.lower().startswith("https://"):
            try:
                r = Request(s, headers=DEFAULT_HTTP_HEADERS)
                raw = urlopen(r, timeout=30).read()
                arr = np.frombuffer(raw, dtype="uint8")
                if cv2.imdecode(arr, cv2.IMREAD_UNCHANGED) is None:
                    raise RuntimeError("下载的内容不是有效图片")
                bio = io.BytesIO(raw)
                for field in [
                    'image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject'
                ]:
                    try:
                        setattr(req, field, bio)
                    except Exception:
                        pass
                res = face_client.detect_face_advance(req, runtime)
            except Exception:
                # 远程直连失败时，回退为先下载到本地临时文件再走文件流
                temp_path = _download_image_to_temp(s)
                with open(temp_path, 'rb') as f:
                    for field in [
                        'image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject'
                    ]:
                        try:
                            setattr(req, field, f)
                        except Exception:
                            pass
                    res = face_client.detect_face_advance(req, runtime)
        else:
            if not os.path.isfile(s):
                raise ValueError(f"本地图片不存在：{s}")
            with open(s, 'rb') as f:
                for field in [
                    'image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject'
                ]:
                    try:
                        setattr(req, field, f)
                    except Exception:
                        pass
                res = face_client.detect_face_advance(req, runtime)
        body = res.body
        data = getattr(body, 'data', None) or {}
        landmarks = getattr(data, 'landmarks', None) or getattr(data, 'Landmarks', None)
        if not landmarks and isinstance(body, dict):
            d = body.get('Data') or body.get('data') or {}
            landmarks = d.get('Landmarks') or d.get('landmarks')
        if not landmarks:
            raise RuntimeError(f"人脸关键点未返回Landmarks: {body}")
        arr = np.array(landmarks, dtype=float)
        arr = np.resize(arr, (105, 2))
        return [(int(x), int(y)) for x, y in arr]
    except Exception as e:
        # 如果 Advance 失败且提示缺少 ImageURL，则回退为标准 URL 调用
        msg = str(e)
        if ("MissingImageURL" in msg) or ("ImageURL is mandatory" in msg):
            try:
                http_url = _ensure_http_image_url(image_url)
                req2 = facebody_models.DetectFaceRequest(image_url=http_url)
                res2 = face_client.detect_face_with_options(req2, runtime)
                body2 = res2.body
                data2 = getattr(body2, 'data', None) or {}
                landmarks2 = getattr(data2, 'landmarks', None) or getattr(data2, 'Landmarks', None)
                if not landmarks2 and isinstance(body2, dict):
                    d2 = body2.get('Data') or body2.get('data') or {}
                    landmarks2 = d2.get('Landmarks') or d2.get('landmarks')
                if not landmarks2:
                    raise RuntimeError(f"人脸关键点未返回Landmarks(回退URL)：{body2}")
                arr2 = np.array(landmarks2, dtype=float)
                arr2 = np.resize(arr2, (105, 2))
                return [(int(x), int(y)) for x, y in arr2]
            except Exception as e2:
                raise RuntimeError(f"阿里云DetectFace SDK 回退(URL)仍失败: {e2}")
        # 其他错误保持原始异常信息
        raise RuntimeError(f"阿里云DetectFace SDK Advance调用失败: {e}")
    finally:
        try:
            if temp_path and os.path.isfile(temp_path):
                os.remove(temp_path)
        except Exception:
            logger.warning(f"删除临时下载文件失败: {temp_path}")



def _retouch_skin_image(image_array: np.ndarray, ak: str, sk: str) -> np.ndarray:
    _, buf = cv2.imencode('.png', image_array)
    bio = io.BytesIO(buf.tobytes())
    _, face_client = _create_aliyun_clients(ak, sk)
    runtime = util_models.RuntimeOptions()
    try:
        req = facebody_models.RetouchSkinAdvanceRequest()
        for field in ['image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject']:
            try:
                setattr(req, field, bio)
            except Exception:
                pass
        res = face_client.retouch_skin_advance(req, runtime)
        body = res.body
        data = getattr(body, 'data', None) or {}
        result_url = getattr(data, 'image_url', None) or getattr(data, 'ImageURL', None)
        if not result_url and isinstance(body, dict):
            d = body.get('Data') or body.get('data') or {}
            result_url = d.get('ImageURL') or d.get('image_url')
        if not result_url:
            raise RuntimeError("智能美肤未返回图片URL")
    except Exception:
        temp_path = os.path.join(tempfile.gettempdir(), f"retouch_{uuid.uuid4().hex}.png")
        with open(temp_path, 'wb') as f:
            f.write(bio.getbuffer())
        try:
            http_url = _upload_file_to_oss(temp_path)
            req2 = facebody_models.RetouchSkinRequest(image_url=http_url)
            res2 = face_client.retouch_skin_with_options(req2, runtime)
            body2 = res2.body
            data2 = getattr(body2, 'data', None) or {}
            result_url = getattr(data2, 'image_url', None) or getattr(data2, 'ImageURL', None)
            if not result_url and isinstance(body2, dict):
                d2 = body2.get('Data') or body2.get('data') or {}
                result_url = d2.get('ImageURL') or d2.get('image_url')
            if not result_url:
                raise RuntimeError("智能美肤未返回图片URL(回退)")
        finally:
            try:
                if os.path.isfile(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
    r = urlopen(Request(result_url, headers=DEFAULT_HTTP_HEADERS))
    arr = np.asarray(bytearray(r.read()), dtype='uint8')
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise RuntimeError("智能美肤下载结果不是有效图片")
    return img


def _liquify_face_image(image_array: np.ndarray, ak: str, sk: str) -> np.ndarray:
    _, buf = cv2.imencode('.png', image_array)
    bio = io.BytesIO(buf.tobytes())
    _, face_client = _create_aliyun_clients(ak, sk)
    runtime = util_models.RuntimeOptions()
    try:
        req = facebody_models.LiquifyFaceAdvanceRequest()
        for field in ['image_url_object', 'imageURLObject', 'ImageURLObject', 'image_urlobject']:
            try:
                setattr(req, field, bio)
            except Exception:
                pass
        res = face_client.liquify_face_advance(req, runtime)
        body = res.body
        data = getattr(body, 'data', None) or {}
        result_url = getattr(data, 'image_url', None) or getattr(data, 'ImageURL', None)
        if not result_url and isinstance(body, dict):
            d = body.get('Data') or body.get('data') or {}
            result_url = d.get('ImageURL') or d.get('image_url')
        if not result_url:
            raise RuntimeError("智能瘦脸未返回图片URL")
    except Exception:
        temp_path = os.path.join(tempfile.gettempdir(), f"liquify_{uuid.uuid4().hex}.png")
        with open(temp_path, 'wb') as f:
            f.write(bio.getbuffer())
        try:
            http_url = _upload_file_to_oss(temp_path)
            req2 = facebody_models.LiquifyFaceRequest(image_url=http_url)
            res2 = face_client.liquify_face_with_options(req2, runtime)
            body2 = res2.body
            data2 = getattr(body2, 'data', None) or {}
            result_url = getattr(data2, 'image_url', None) or getattr(data2, 'ImageURL', None)
            if not result_url and isinstance(body2, dict):
                d2 = body2.get('Data') or body2.get('data') or {}
                result_url = d2.get('ImageURL') or d2.get('image_url')
            if not result_url:
                raise RuntimeError("智能瘦脸未返回图片URL(回退)")
        finally:
            try:
                if os.path.isfile(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
    r = urlopen(Request(result_url, headers=DEFAULT_HTTP_HEADERS))
    arr = np.asarray(bytearray(r.read()), dtype='uint8')
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise RuntimeError("智能瘦脸下载结果不是有效图片")
    return img


def _clean_url(s: str) -> str:
    """移除首尾的反引号/引号与空白，避免URL被包裹。"""
    try:
        t = (s or "").strip()
        while t and t[0] in "`'\"":
            t = t[1:].strip()
        while t and t[-1] in "`'\"":
            t = t[:-1].strip()
        return t
    except Exception:
        return s


def _guess_mime_type_from_ext(ext: str) -> str:
    """根据扩展名猜测 MIME 类型（仅覆盖图片常见类型）。"""
    e = (ext or "").lower()
    if e in (".jpg", ".jpeg"):
        return "image/jpeg"
    if e == ".png":
        return "image/png"
    if e == ".gif":
        return "image/gif"
    if e == ".webp":
        return "image/webp"
    if e in (".bmp"):
        return "image/bmp"
    if e in (".tiff", ".tif"):
        return "image/tiff"
    return "application/octet-stream"


def _download_image_to_temp(url: str) -> str:
    """下载远程图片到本地临时文件，返回文件路径。

    使用带UA的请求避免常见的403限制；同时做基本的图片有效性校验。
    """
    url = _clean_url(url)
    # 根据URL猜扩展名
    try:
        path_part = url.split('#', 1)[0].split('?', 1)[0]
        _, ext = os.path.splitext(path_part)
        allowed = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif"}
        if ext.lower() not in allowed:
            ext = ".jpg"
    except Exception:
        ext = ".jpg"

    req = Request(url, headers=DEFAULT_HTTP_HEADERS)
    raw = urlopen(req, timeout=30).read()

    temp_path = os.path.join(tempfile.gettempdir(), f"download_{uuid.uuid4().hex}{ext}")
    with open(temp_path, "wb") as f:
        f.write(raw)

    # 验证内容是否为图片
    arr = np.frombuffer(raw, dtype="uint8")
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise RuntimeError("下载的内容不是有效图片")

    return temp_path


def _upload_file_to_oss(file_path: str) -> str:
    """将本地文件以 multipart/form-data 上传到 OSS，返回URL。

    成功：返回可访问的文件URL。
    失败：抛出 RuntimeError。
    """
    try:
        if not os.path.isfile(file_path):
            raise RuntimeError(f"待上传文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        content_type = _guess_mime_type_from_ext(ext)

        with open(file_path, "rb") as f:
            data = f.read()
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"

        # 构建 multipart/form-data
        preamble = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
        closing = f"\r\n--{boundary}--\r\n".encode("utf-8")
        body = preamble + data + closing

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }
        req = Request(UPLOAD_API_URL, data=body, headers=headers, method="POST")
        raw = urlopen(req, timeout=30).read()
        resp = json.loads(raw.decode("utf-8"))

        if isinstance(resp, dict) and resp.get("code") == 0:
            url = ((resp.get("data") or {}).get("url"))
            if url:
                return url
            raise RuntimeError("上传成功但未返回URL")
        # 非0视为失败
        msg = resp.get("msg") if isinstance(resp, dict) else str(resp)
        raise RuntimeError(f"上传失败: {msg}")
    except Exception as e:
        raise RuntimeError(f"上传到OSS失败: {e}")


@mcp.tool()
def make_id_photo(
    image_url: str,
    bg: Literal["white", "blue", "red"] = "blue",
    spec: Literal["一寸", "二寸-标准", "二寸-大"] | None = None,
) -> dict:
    """
    生成并保存证件照

    流程：
    1) 使用阿里云图像分割与人脸关键点，生成透明前景并对齐；
    2) 按证件照构图裁剪——默认二寸-标准（413×531），若传入 `spec` 则按规格；
    3) 合成到指定背景色，保存临时文件并上传，返回 URL。

    参数：
    - `image_url`（必填）：公网可访问的人像图片 URL。
    - `bg`（可选）：背景色 white/blue/red，默认 blue。
    - `spec`（可选）：一寸/二寸-标准/二寸-大。

    返回：
    - `success`: 是否成功
    - `file_url`: 上传后的文件 URL（为兼容旧字段，`file_path` 同为 URL）
    - `size_applied`: 实际应用的目标尺寸（如 `413x531`）
    - `bg`: 背景色
    - `source_images`: 从模型返回中解析出的图片 URL 或 data URL 列表
    - `behavior_notice`: 说明为同步生成
    """
    # 获取 AK/SK
    ak, sk = _get_ali_credentials()

    # 清理可能包裹的反引号或引号
    image_url = _clean_url(image_url)

    # 目标尺寸解析，默认二寸-标准
    try:
        target_size = _spec_to_size(spec) if spec else _spec_to_size("二寸-标准")
        size_label = f"{target_size[0]}x{target_size[1]}"
    except Exception as e:
        raise ValueError(f"目标规格解析失败: {e}")

    # 背景色（BGR）
    try:
        color = _bg_to_bgr(bg)
    except Exception as e:
        raise ValueError(str(e))

    # 准备调用：远程 URL 直接使用；本地路径上传以便返回可访问 URL
    if image_url.lower().startswith("http://") or image_url.lower().startswith("https://"):
        input_url = image_url
    else:
        if not os.path.isfile(image_url):
            raise ValueError(f"本地图片不存在：{image_url}")
        input_url = _upload_file_to_oss(image_url)

    try:
        # 人脸关键点
        landmarks = _detect_face_http(input_url, ak, sk)
        landmarks_np = np.array(landmarks)

        # 人体分割
        seg_img_url = _segment_body_http(input_url, ak, sk)
        rqt = urlopen(Request(seg_img_url, headers=DEFAULT_HTTP_HEADERS))
        seg_img = np.asarray(bytearray(rqt.read()), dtype="uint8")
        seg_img = cv2.imdecode(seg_img, cv2.IMREAD_UNCHANGED)

        # 对齐与裁剪
        rotated_img, eye_center, angle, landmarks_rot = _align_face(seg_img, landmarks_np)
        png_img = _corp_halfbody(rotated_img, landmarks_rot, (target_size[0], target_size[1]))

        # 背景合成
        rst_img_bg = np.zeros((target_size[1], target_size[0], 3)) + np.array(color[0:3])
        rst_img = _image_merge_background(png_img[:, :, 0:3], png_img, rst_img_bg)
        rst_img = _retouch_skin_image(rst_img, ak, sk)
        rst_img = _liquify_face_image(rst_img, ak, sk)
    except Exception as error:
        raise RuntimeError(f"证件照生成失败: {error}")

    # 保存到临时目录（PNG）
    ts = int(time.time())
    default_name = f"id_photo_{size_label}_{ts}.png"
    file_path = os.path.join(tempfile.gettempdir(), default_name)
    try:
        # OpenCV 保存
        ok = cv2.imwrite(file_path, rst_img)
        if not ok:
            raise RuntimeError("OpenCV 保存失败")
        if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
            raise RuntimeError("保存文件失败：未创建或文件大小为0")
    except Exception as e:
        raise RuntimeError(f"保存文件失败: {e}；请检查临时目录是否可写: {file_path}")

    # 上传到 OSS
    try:
        uploaded_url = _upload_file_to_oss(file_path)
    except Exception as e:
        # 上传失败，不删除本地文件，便于排查和保留结果
        raise RuntimeError(f"上传到OSS失败: {e}")

    # 上传成功后删除本地文件
    try:
        os.remove(file_path)
    except Exception:
        # 删除失败不影响结果，仅记录日志
        logger.warning(f"删除本地文件失败: {file_path}")

    result = {
        "success": True,
        "file_path": uploaded_url,
        "file_url": uploaded_url,
        "size_applied": size_label,
        "bg": bg,
        "spec": spec if spec else "二寸-标准",
        "source_images": [input_url],
        "postprocess": ["retouch_skin", "liquify_face"],
    }
    return result




def main():
    """主函数入口"""
    logger.info("启动证件照生成 MCP 服务器...")
    mcp.run()


if __name__ == "__main__":
    main()
