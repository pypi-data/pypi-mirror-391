"""封装应用注册表与激活器的业务逻辑。"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from .activator import open_app as activate_app, debug_app_state
from .apps import AppRegistry, build_registry


class AppLauncherService:
    """管理应用配置并通过激活器打开应用。"""

    def __init__(self, auto_discover: bool = True) -> None:
        self.auto_discover = auto_discover
        self.registry: AppRegistry = build_registry(auto_discover=auto_discover)

    def reload(self) -> None:
        self.registry = build_registry(auto_discover=self.auto_discover)

    def list_apps(self) -> List[dict[str, Any]]:
        return self.registry.dump()

    def debug_app(self, app_name: str) -> Dict[str, Any]:
        """调试应用状态"""
        app = self.registry.find(app_name)
        if not app:
            raise ValueError(f"未找到匹配的应用: {app_name}")
        
        return debug_app_state(app.path)

    async def open_app(self, query: str) -> Dict[str, Any]:
        app = self.registry.find(query)
        if not app:
            raise ValueError(f"未找到匹配的应用: {query}")

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, activate_app, app)
        payload = {
            "query": query,
            "app": {
                "name": app.name,
                "path": app.path,
                "keywords": app.keywords,
                "hotkey": app.hotkey,
            },
            "execution": result,
        }

        if not result.get("success"):
            raise RuntimeError(f"打开应用失败: {result.get('message')}")
        return payload
