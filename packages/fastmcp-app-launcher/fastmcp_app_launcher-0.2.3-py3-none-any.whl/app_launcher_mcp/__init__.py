"""FastMCP 应用启动 MCP 服务。"""

from importlib import metadata

from .server import main

try:  # pragma: no cover
    __version__ = metadata.version("fastmcp-app-launcher")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["main", "__version__"]
