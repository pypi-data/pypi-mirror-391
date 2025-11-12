"""GIF 工具 MCP 服务器。"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from PIL import Image, ImageSequence

# 将日志发送到 stderr，避免干扰 MCP stdio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP("gif-tools")

DEFAULT_FRAME_DURATION_MS = 100
SUPPORTED_FORMATS = {
    "PNG": "png",
    "WEBP": "webp",
    "JPEG": "jpg",
    "JPG": "jpg",
    "TIFF": "tiff",
    "BMP": "bmp",
}


def _normalize_path(file_path: str) -> Path:
    """将任意路径字符串转换成可用的 Path 并做存在性检查。"""
    path = Path(file_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")
    if not path.is_file():
        raise IsADirectoryError(f"路径不是文件：{path}")
    return path


def _ensure_directory(target_dir: str | None, source_file: Path) -> Path:
    """根据用户输入或 GIF 文件位置确定输出目录。"""
    if target_dir:
        dir_path = Path(target_dir).expanduser()
    else:
        dir_path = source_file.with_name(f"{source_file.stem}_frames")
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def _collect_frame_durations(image: Image.Image) -> list[int]:
    """遍历 GIF 并返回每帧时长（毫秒）。"""
    durations: list[int] = []
    base_duration = int(image.info.get("duration", DEFAULT_FRAME_DURATION_MS) or DEFAULT_FRAME_DURATION_MS)
    for frame in ImageSequence.Iterator(image):
        duration = int(frame.info.get("duration", base_duration) or base_duration)
        if duration <= 0:
            duration = DEFAULT_FRAME_DURATION_MS
        durations.append(duration)

    if not durations:
        durations.append(base_duration)
    return durations


def _playback_mode(loop_value: int) -> str:
    """根据 loop 参数给出易懂的播放模式描述。"""
    if loop_value == 0:
        return "infinite_loop"
    if loop_value == 1:
        return "single_play"
    return "finite_loop"


@mcp.tool()
async def get_gif_metadata(file_path: str) -> dict[str, Any]:
    """读取 GIF 元数据，包含帧时长、循环次数与像素信息。"""
    gif_path = _normalize_path(file_path)

    with Image.open(gif_path) as image:
        if image.format != "GIF":
            raise ValueError(f"文件不是 GIF：{gif_path}")

        frame_durations = _collect_frame_durations(image)
        total_duration_ms = sum(frame_durations)
        loop_raw = int(image.info.get("loop", 1))
        playback = _playback_mode(loop_raw)

        metadata = {
            "file_path": str(gif_path),
            "file_size_bytes": gif_path.stat().st_size,
            "frame_count": getattr(image, "n_frames", len(frame_durations)),
            "frame_durations_ms": frame_durations,
            "total_duration_ms": total_duration_ms,
            "total_duration_seconds": round(total_duration_ms / 1000, 3),
            "loop_count_raw": loop_raw,
            "playback_mode": playback,
            "size": {"width": image.width, "height": image.height},
            "color_mode": image.mode,
            "has_transparency": "transparency" in image.info or image.mode in {"RGBA", "LA", "P"},
        }

    logger.info("读取 GIF 元数据完成：%s", gif_path)
    return metadata


@mcp.tool()
async def split_gif_frames(
    file_path: str,
    output_dir: str | None = None,
    filename_prefix: str = "frame",
    image_format: str = "PNG",
    keep_transparency: bool = True,
) -> dict[str, Any]:
    """将 GIF 拆分为多张静态图片并返回输出清单。"""
    gif_path = _normalize_path(file_path)
    out_dir = _ensure_directory(output_dir, gif_path)

    format_upper = image_format.upper()
    extension = SUPPORTED_FORMATS.get(format_upper, format_upper.lower())

    saved_files: list[str] = []

    with Image.open(gif_path) as image:
        if image.format != "GIF":
            raise ValueError(f"文件不是 GIF：{gif_path}")

        for index, frame in enumerate(ImageSequence.Iterator(image)):
            frame_copy = frame.copy()
            mode = "RGBA" if keep_transparency else "RGB"
            converted = frame_copy.convert(mode)
            filename = f"{filename_prefix}_{index:03d}.{extension}"
            destination = out_dir / filename
            converted.save(destination, format=format_upper)
            saved_files.append(str(destination))

    logger.info("已导出 %d 帧到 %s", len(saved_files), out_dir)
    return {
        "output_dir": str(out_dir),
        "frame_count": len(saved_files),
        "image_format": format_upper,
        "files": saved_files,
    }


def main() -> None:
    """启动 GIF MCP 服务器（stdio 模式）。"""
    logger.info("启动 GIF MCP 服务器 (stdio transport)")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
