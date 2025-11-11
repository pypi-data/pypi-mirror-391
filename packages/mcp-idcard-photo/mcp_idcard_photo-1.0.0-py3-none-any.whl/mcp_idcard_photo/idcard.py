import argparse
import math
import cv2

from typing import List

import numpy as np
from alibabacloud_imageseg20191230.client import Client as imageseg20191230Client
from alibabacloud_facebody20191230.client import Client as facebody20191230Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_facebody20191230 import models as facebody_20191230_models
from alibabacloud_imageseg20191230 import models as imageseg_20191230_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from viapi.fileutils import FileUtils

import urllib.request


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> (imageseg20191230Client, facebody20191230Client):
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        seg_config = open_api_models.Config(
            # 您的 AccessKey ID,
            access_key_id=access_key_id,
            # 您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        face_config = open_api_models.Config(
            # 您的 AccessKey ID,
            access_key_id=access_key_id,
            # 您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        seg_config.endpoint = f'imageseg.cn-shanghai.aliyuncs.com'
        face_config.endpoint = f'facebody.cn-shanghai.aliyuncs.com'
        return (imageseg20191230Client(seg_config), facebody20191230Client(face_config))

def id_pohto_demo(
        args: List[str],
) -> None:
    assert (args is not None and len(args.param) > 2), "parameters wrong, use -h for details!"
    [sc_file, color, of_file] = [i for i in args.param]

    # set id photo size
    size = [295, 413]

    # client init
    seg_client, face_client = Sample.create_client(args.access_key_id, args.access_key_secret)

    # generation source image url
    input_url = generate_url(sc_file, args.access_key_id, args.access_key_secret)

    # init segment_body_request
    segment_body_request = imageseg_20191230_models.SegmentBodyRequest(
        image_url=input_url
    )

    # init detect_face_request
    detect_face_request = facebody_20191230_models.DetectFaceRequest(
        image_url=input_url
    )
    runtime = util_models.RuntimeOptions()
    try:
        # 通过人脸SDK获取人脸105关键点信息
        face_result = face_client.detect_face_with_options(detect_face_request, runtime)
        landmarks = face_result.body.data.landmarks
        landmarks = np.array(landmarks)

        # 通过分割SDK获取分割png图
        seg_result = seg_client.segment_body_with_options(segment_body_request, runtime)
        print(seg_result.body.data.image_url)
        rqt = urllib.request.urlopen(seg_result.body.data.image_url)
        seg_img = np.asarray(bytearray(rqt.read()), dtype="uint8")
        seg_img = cv2.imdecode(seg_img, cv2.IMREAD_UNCHANGED)

        # 根据人脸关键点进行人脸对齐，返回旋转后图像、面部中心点、旋转角度、旋转后新的landmarks值
        rotated_img, eye_center, angle, landmarks = align_face(seg_img, landmarks)

        # 输入旋转后图片、预期的证件照分辨率、landmarks、背景色，返回半身像结果
        png_img = corp_halfbody(rotated_img, landmarks, size)

        # 证件照背景色替换
        colors = {'red': (0, 0, 255, 255), 'blue': (255, 0, 0, 255), 'white': (255, 255, 255, 255)}
        if type(color) is str:
            color = colors[color]
        rst_img = np.zeros((size[1], size[0], 3)) + color[0:3]
        rst_img = image_merge_background(png_img[:, :, 0:3], png_img, rst_img)

        # 保存结果到本地
        cv2.imwrite(of_file, rst_img)
    except Exception as error:
        print(error.message)
        # 如有需要，请打印 error
        UtilClient.assert_as_string(error.message)

def align_face(image_array, landmarks):
    """ align faces according to eyes position
    :param image_array: numpy array of a single image
    :param landmarks: dict of landmarks for facial parts as keys and tuple of coordinates as values
    :return:
    rotated_img:  numpy array of aligned image
    eye_center: tuple of coordinates for eye center
    angle: degrees of rotation
    """
    landmarks = np.resize(landmarks, (105, 2))

    # get list landmarks of left and right eye
    left_eye = landmarks[24:39]
    right_eye = landmarks[40:55]
    left_eye_center = np.mean(left_eye, axis=0).astype("int32")
    right_eye_center = np.mean(right_eye, axis=0).astype("int32")
    dy = right_eye_center[1] - left_eye_center[1]
    dx = right_eye_center[0] - left_eye_center[0]
    angle = math.atan2(dy, dx) * 180. / math.pi
    # calculate the center of 2 eyes
    eye_center = (int(left_eye_center[0] + right_eye_center[0]) // 2,
                  int(left_eye_center[1] + right_eye_center[1]) // 2)
    # at the eye_center, rotate the image by the angle
    rotate_matrix = cv2.getRotationMatrix2D(eye_center, angle, scale=1)
    rotated_img = cv2.warpAffine(image_array, rotate_matrix, (image_array.shape[1], image_array.shape[0]))

    rotated_landmarks = []
    for landmark in landmarks:
        rotated_landmark = rotate(origin=eye_center, point=landmark, angle=angle, row=image_array.shape[0])
        rotated_landmarks.append(rotated_landmark)
    return rotated_img, eye_center, angle, rotated_landmarks

def rotate(origin, point, angle, row):
    """ rotate coordinates in image coordinate system
    :param origin: tuple of coordinates,the rotation center
    :param point: tuple of coordinates, points to rotate
    :param angle: degrees of rotation
    :param row: row size of the image
    :return: rotated coordinates of point
    """
    x1, y1 = point
    x2, y2 = origin
    y1 = row - y1
    y2 = row - y2
    angle = math.radians(angle)
    x = x2 + math.cos(angle) * (x1 - x2) - math.sin(angle) * (y1 - y2)
    y = y2 + math.sin(angle) * (x1 - x2) + math.cos(angle) * (y1 - y2)
    y = row - y
    return int(x), int(y)

def corp_halfbody(image_array, landmarks, size):
    """ crop face according to eye,mouth and chin position
    :param image_array: numpy array of a single image
    :param size: single int value, size for w and h after crop
    :param landmarks: dict of landmarks for facial parts as keys and tuple of coordinates as values
    :return:
    cropped_img: numpy array of cropped image
    left, top: left and top coordinates of cropping
    """

    crop_size = [0, 0, size[1], size[0]]

    scal = size[1] / 4 / abs(landmarks[98][1] - landmarks[56][1])
    image = cv2.resize(image_array, np.multiply((image_array.shape[0:2])[::-1], scal).astype(int))
    landmarks = np.multiply(np.array(landmarks), scal)

    x_center = landmarks[98][0]
    crop_size[0:2] = [x_center - size[0] / 2, x_center + size[0] / 2]

    y_center = (landmarks[98][1] + landmarks[56][1]) / 2
    crop_size[2:4] = [y_center - size[1] / 2, y_center + size[1] / 2]

    left, right, top, bottom = [round(i) for i in crop_size]
    left = max(0, left)
    top = max(0, top)
    right = min(image.shape[1], right)
    bottom = min(image.shape[0], bottom)

    cropped_img = image[top:bottom, left:right]

    left, right, top, bottom = [round(i) for i in crop_size]
    bottom = size[1]
    top = size[1] - cropped_img.shape[0]
    left = -min(0, left)
    right = min(cropped_img.shape[1] + left, size[0])


    png_img = np.zeros((size[1], size[0], 4))
    png_img[top:bottom, left:right] = cropped_img[:, :]
    return png_img

def image_merge_background(sc_image, png_image, bg_image):
    """ merge foreground to background image
    :param sc_image: numpy array of the source image
    :param png_image: numpy array of the segmented result with same size of sc_image
    :param bg_image: numpy array of the background image with same size of sc_image
    :return:
    rst_image: numpy array of merged image
    """
    assert (sc_image is not None and png_image is not None and bg_image is not None), "read image input error!"
    h, w, c = sc_image.shape

    # keep sc_image, png_image and bg_image same size
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

    # merge background
    sc_image = sc_image.astype(float)
    bg_image = bg_image.astype(float)
    rst_image = (sc_image - bg_image) * mask + bg_image
    rst_image = np.clip(rst_image, 0, 255)
    return rst_image

# see https://help.aliyun.com/document_detail/155645.html for more detail
def generate_url(image_path, access_key_id, access_key_secret):
    file_utils = FileUtils(access_key_id, access_key_secret)
    oss_url = file_utils.get_oss_url(image_path, "jpeg", True)
    return oss_url

def define_options():
    parser = argparse.ArgumentParser(description='Human segmentation examples.')
    parser.add_argument('-i', '--access_key_id', default="", help="oss access key id")
    parser.add_argument('-s', '--access_key_secret', default="", help="access key secret")
    parser.add_argument('-p', '--param', nargs=3
                            , default=['./data/source.jpeg', 'red', 'result.jpg']
                            , type=str
                            , help=('source_image_path background_color[red blue white] result_path'))
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = define_options()
    id_pohto_demo(args)
