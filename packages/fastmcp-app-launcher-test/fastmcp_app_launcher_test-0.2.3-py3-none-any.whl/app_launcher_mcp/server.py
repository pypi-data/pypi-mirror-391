"""FastMCP 服务器入口。"""

from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime
from typing import Any, Dict

from fastmcp import FastMCP

from .service import AppLauncherService

# 配置日志 - 同时输出到控制台和文件
log_dir = os.path.expanduser("~/Desktop")
log_file = os.path.join(log_dir, "mcp_app_launcher.log")

# 配置根日志记录器，确保所有子模块的日志都能被捕获
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# 清除现有的处理器（避免重复）
root_logger.handlers.clear()

# 文件处理器（追加模式）
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# 控制台处理器
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter('[%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_formatter)

# 添加处理器到根记录器
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

# 获取当前模块的记录器用于启动信息
logger = logging.getLogger("app_launcher_mcp")

# 记录启动信息
logger.info("="*80)
logger.info(f"FastMCP 应用启动器服务器启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"日志文件: {log_file}")
logger.info("="*80)

os.environ.setdefault("FASTMCP_LOG_LEVEL", "INFO")

mcp = FastMCP("FastMCP 应用启动器")
SERVICE: AppLauncherService | None = None


def require_service() -> AppLauncherService:
    if SERVICE is None:
        raise RuntimeError("服务尚未初始化，请先调用 main()")
    return SERVICE


@mcp.tool()
async def list_apps_tool() -> Dict[str, Any]:
    """列出所有可用的应用程序。"""

    service = require_service()
    apps = service.list_apps()
    return {"count": len(apps), "apps": apps}


@mcp.tool()
async def open_app_tool(app_name: str, reload_before: bool = False) -> Dict[str, Any]:
    """根据名称或关键词打开应用。"""

    service = require_service()
    if reload_before:
        service.reload()
    return await service.open_app(app_name)


@mcp.tool()
async def reload_apps_tool() -> Dict[str, Any]:
    """手动重新加载配置。"""

    service = require_service()
    service.reload()
    apps = service.list_apps()
    return {"message": "已重新加载应用配置", "count": len(apps)}


@mcp.tool()
async def debug_app_tool(app_name: str) -> Dict[str, Any]:
    """调试应用状态（仅Windows）。"""
    
    service = require_service()
    return service.debug_app(app_name)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="FastMCP 应用启动服务")
    parser.add_argument("--no-auto-discover", action="store_true", help="禁用默认的系统应用自动发现")
    parser.add_argument("--transport", default="stdio", help="MCP 传输层，默认 stdio")
    args = parser.parse_args(argv)

    global SERVICE
    SERVICE = AppLauncherService(auto_discover=not args.no_auto_discover)

    print("启动 FastMCP 应用启动器，Transport:", args.transport)
    print("可用工具: list_apps_tool, open_app_tool, reload_apps_tool, debug_app_tool")

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
