"""FastMCP 服务器入口。"""

from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime
from typing import Any, Dict

from fastmcp import FastMCP

from .service import AppLauncherService


logger = logging.getLogger("app_launcher_mcp")


def setup_logging() -> str:
    """为 app_launcher_mcp 日志树配置处理器，不干扰宿主程序。"""

    log_dir = os.path.expanduser("~")
    log_file = os.path.join(log_dir, "mcp_app_launcher.log")

    if getattr(logger, "_fastmcp_launcher_configured", False):
        return log_file

    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler.setFormatter(stream_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    setattr(logger, "_fastmcp_launcher_configured", True)
    return log_file

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

    log_file = setup_logging()

    logger.info("=" * 80)
    logger.info(f"FastMCP 应用启动器服务器启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 80)

    global SERVICE
    SERVICE = AppLauncherService(auto_discover=not args.no_auto_discover)

    print("启动 FastMCP 应用启动器，Transport:", args.transport)
    print("可用工具: list_apps_tool, open_app_tool, reload_apps_tool, debug_app_tool")

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
