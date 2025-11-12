# 生成证件照 MCP 服务器

基于阿里云视觉智能开放平台（VIAPI）高清人体分割（SegmentHDBody）与人脸关键点检测（DetectFace），提供一个工具即可一键生成并裁剪标准证件照，支持白/蓝/红背景与常用尺寸（一寸、二寸）。

## ✨ 核心特性

- 🎯 单一工具：`make_id_photo` 完成生成 → 裁剪 → 保存全流程
- 🖼️ 背景替换：支持 `white` / `blue` / `red` 三种背景
 - 📐 规格支持：一寸（295×413）、二寸-标准（413×531）、二寸-大（413×579）
- 💾 自动保存：默认保存到桌面；可指定目录或文件路径
- ⚡ 同步返回：直接返回云端图片地址与本地保存路径，无需任务查询

## 🔑 配置阿里云 AccessKey

建议使用 RAM 用户的 AccessKey，并为其分配合适权限（如仅 `viapi-imageseg:*`）。请在运行环境设置以下环境变量（任一组即可）：

```bash
export ALI_ACCESS_KEY_ID="你的AccessKeyId"
export ALI_ACCESS_KEY_SECRET="你的AccessKeySecret"
```

或使用通用变量名：

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="你的AccessKeyId"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="你的AccessKeySecret"
```

Windows PowerShell：

```powershell
$env:ALI_ACCESS_KEY_ID = "你的AccessKeyId"
$env:ALI_ACCESS_KEY_SECRET = "你的AccessKeySecret"
$env:ALI_REGION = "cn-shanghai" # 可选
```

## 🚀 启动服务

直接运行模块：

```bash
python -m mcp_idcard_photo.server
```

## 🔧 在 MCP 客户端中配置

以 Claude Desktop / Cline / Kiro 为例：

```json
{
  "mcpServers": {
    "id-photo": {
      "command": "python",
    "args": ["-m", "mcp_idcard_photo.server"],
    "env": {
        "ALI_ACCESS_KEY_ID": "ak-xxxx",
        "ALI_ACCESS_KEY_SECRET": "sk-xxxx"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## 📖 使用指南

### 工具：`make_id_photo`

生成并保存标准证件照（同步）。流程：
1) 使用 `image_url + bg` 调用阿里云高清人体分割，得到透明前景人像；
2) 调用人脸关键点检测进行对齐与构图，按目标尺寸裁剪：默认二寸-标准（413×531），若传入 `spec` 则按规格；
3) 合成到指定背景色并保存到桌面或 `output_path` 指定位置；返回保存路径与元数据。

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `image_url` | string | ✅ | - | 输入图片地址，需公网可访问的 `http/https` 链接 |
| `output_path` | string | ❌ | 桌面 | 输出目录或最终文件路径；为目录时自动命名文件 |
| `bg` | enum | ❌ | `blue` | 背景色：`white`、`blue`、`red` |
| `spec` | enum | ❌ | - | 证件照规格：`一寸`、`二寸-标准`、`二寸-大` |

裁剪默认比例（推荐）：
- 头顶到画面上边距约 `12%`（`top_margin_ratio = 0.12`）
- 垂直裁剪高度约为主体包围盒的 `92%`（`expand_ratio = 0.92`）

#### 调用示例

- 使用默认蓝底与默认二寸标准尺寸并保存到桌面：

```
make_id_photo(image_url="https://example.com/portrait.jpg")
```

- 指定红底、指定输出目录并自定义尺寸：
```
make_id_photo(
  image_url="https://example.com/portrait.jpg",
  output_path="D:\\Output\\ID",
  bg="red",
  spec="一寸"
)
```

- 指定规格为一寸并直接保存到某个文件路径：

```
make_id_photo(
  image_url="https://example.com/a.png",
  output_path="D:\\Output\\my_id.png",
  spec="一寸"
)
```

#### 返回结果示例

```json
{
  "success": true,
  "file_path": "C:\\Users\\you\\Desktop\\id_photo_413x531_1730000000.png",
  "size_applied": "413x531",
  "bg": "blue",
  "spec": "二寸-标准",
  "source_images": ["https://dashscope-result-.../xxx.png?Expires=..."],
  "behavior_notice": "采用同步生成，结果已裁剪并保存到本地"
}
```

## ⚠️ 注意事项

1. 高清人体分割输入格式支持 JPG/JPEG/BMP/PNG（透明图），大小不超过 40 MB，分辨率 32×32 至 6000×6000，URL 不得包含中文
2. 建议使用 RAM 用户的 AccessKey 并授予细粒度权限，妥善保管 AccessKey，发现风险及时更换
3. 输入图片建议人像居中、正面、胸部以上；过暗或过曝会影响效果
4. 若主体与背景差异较弱导致掩膜不稳定，工具将自动回退为居中裁剪，仍保证得到目标尺寸成片

## 🛠️ 技术实现

- 使用阿里云 imageseg 2019-12-30 高清人体分割（SegmentHDBody Advance，文件流）与回退 URL 调用
- 使用阿里云 facebody 2019-12-30 人脸关键点（DetectFace Advance）获取 105 点进行对齐与裁剪
- 输出路径：优先 `output_path`；为空则默认桌面，目录不存在时自动创建
- 命名包含尺寸与时间戳，如：`id_photo_413x531_1730000000.png`

## 📚 相关文档

- 高清人体分割：阿里云视觉智能开放平台（SegmentHDBody）
- RAM 用户与权限配置：阿里云视觉智能开放平台权限策略
- Model Context Protocol (MCP)

## 📄 许可证

MIT License