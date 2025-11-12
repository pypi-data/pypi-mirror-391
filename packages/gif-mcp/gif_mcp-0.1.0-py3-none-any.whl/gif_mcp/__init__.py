"""GIF 工具 MCP 包。"""

from .server import main, mcp, get_gif_metadata, split_gif_frames

__all__ = [
    "main",
    "mcp",
    "get_gif_metadata",
    "split_gif_frames",
]
