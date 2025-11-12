# GIF MCP 服务器

一个使用 Python + FastMCP 构建的 GIF 工具服务器，提供：

- **元数据查询**：读取 GIF 帧数、帧时长、总时长、循环方式等关键信息。
- **帧分割导出**：将动画拆成多张静态图，可自定义输出目录、文件前缀及图片格式。

## 环境要求

- Python 3.10 及以上
- [uv](https://github.com/astral-sh/uv) 或 pip（推荐使用 uv 以保持与项目其余部分一致）

## 安装与运行

```bash
cd python/GifMCP
uv sync               # 安装依赖
uv run gif-mcp        # 以 stdio 方式启动 MCP 服务器
```

若使用其他虚拟环境管理工具，保证安装 `mcp` 与 `Pillow` 即可。

## 可用工具

### `get_gif_metadata`
- `file_path`：待分析的 GIF 路径。
- 返回值：帧数、每帧时长、总时长（毫秒/秒）、循环方式、像素尺寸、是否带透明通道等。

### `split_gif_frames`
- `file_path`：GIF 路径。
- `output_dir`（可选）：帧导出目录，默认与 GIF 同级的 `<文件名>_frames`。
- `filename_prefix`（可选）：导出文件名前缀，默认 `frame`。
- `image_format`（可选）：输出格式，默认 `PNG`，支持 `PNG/WEBP/JPEG/TIFF/BMP`。
- `keep_transparency`（可选）：是否保留透明通道，默认 `True`。
- 返回值：输出目录、帧数量以及生成的文件清单。

## 开发提示

- 所有工具都通过 `mcp.server.fastmcp.FastMCP` 以 stdio 传输方式暴露。
- 文件路径参数会自动展开 `~` 并进行存在性检查，错误会以异常形式回传给 MCP 客户端。
- 若需要扩展更多 GIF 处理能力，可在 `gif_mcp/server.py` 中新增工具后重新运行 `uv run gif-mcp`。
