"""FastMCP 服务器入口。"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict

from fastmcp import FastMCP

from .service import AppLauncherService

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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="FastMCP 应用启动服务")
    parser.add_argument("--no-auto-discover", action="store_true", help="禁用默认的系统应用自动发现")
    parser.add_argument("--transport", default="stdio", help="MCP 传输层，默认 stdio")
    args = parser.parse_args(argv)

    global SERVICE
    SERVICE = AppLauncherService(auto_discover=not args.no_auto_discover)

    print("启动 FastMCP 应用启动器，Transport:", args.transport)
    print("可用工具: list_apps_tool, open_app_tool, reload_apps_tool")

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
