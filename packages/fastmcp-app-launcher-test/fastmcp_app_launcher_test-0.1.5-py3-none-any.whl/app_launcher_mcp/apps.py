"""应用配置加载与搜索逻辑。"""

from __future__ import annotations

import json
import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_CONFIG_PATHS = (
    Path.home() / ".mcp-apps.json",
    Path.cwd() / "mcp-apps.json",
    Path.home() / ".config" / "mcp-apps" / "config.json",
)

AUTO_DISCOVER_LIMIT = int(os.environ.get("MCP_AUTO_DISCOVER_LIMIT", "200"))


def _paths_from_env(env_name: str, defaults: Sequence[str]) -> tuple[Path, ...]:
    raw = os.environ.get(env_name)
    entries = raw.split(os.pathsep) if raw else defaults
    resolved: list[Path] = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        resolved.append(Path(entry).expanduser())
    return tuple(resolved)

DEFAULT_WINDOWS_APPS = (
    {
        "name": "QQ",
        "paths": [
            "C:/Program Files/Tencent/QQ/Bin/QQ.exe",
            "C:/Program Files (x86)/Tencent/QQ/Bin/QQ.exe",
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Tencent", "QQ", "Bin", "QQ.exe"),
        ],
        "keywords": ["qq", "tencent", "腾讯"],
        "hotkey": "Ctrl+Alt+Z",
        "relaunch_when_tray_hidden": False,  # 默认关闭，避免数据丢失风险
        "shell_fallback_on_fail": True,
    },
    {
        "name": "微信",
        "paths": [
            "C:/Program Files/Tencent/WeChat/WeChat.exe",
            "C:/Program Files (x86)/Tencent/WeChat/WeChat.exe",
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Tencent", "WeChat", "WeChat.exe"),
        ],
        "keywords": ["微信", "wechat", "weixin"],
        "hotkey": "Ctrl+Alt+W",
    },
    {
        "name": "Visual Studio Code",
        "paths": [
            "C:/Program Files/Microsoft VS Code/Code.exe",
            "C:/Users/Public/scoop/apps/vscode/current/code.exe",
        ],
        "keywords": ["vscode", "code", "编辑器"],
    },
)

DEFAULT_MAC_APPS = (
    {
        "name": "WeChat",
        "path": "/Applications/WeChat.app",
        "keywords": ["wechat", "微信"],
    },
    {
        "name": "Safari",
        "path": "/Applications/Safari.app",
        "keywords": ["safari", "browser", "浏览器"],
    },
    {
        "name": "iTerm",
        "path": "/Applications/iTerm.app",
        "keywords": ["terminal", "iterm"],
    },
)

MAC_APPLICATION_DIRS = _paths_from_env(
    "MCP_MAC_APP_DIRS",
    [
        "/Applications",
        "/Applications/Utilities",
        "/System/Applications",
        "~/Applications",
    ],
)

WINDOWS_SHORTCUT_DEFAULTS = [
    Path(os.environ.get("ProgramData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs",
]

WINDOWS_SHORTCUT_DIRS = tuple(
    Path(entry).expanduser()
    for entry in (
        os.environ.get("MCP_WINDOWS_SHORTCUT_DIRS").split(os.pathsep)
        if os.environ.get("MCP_WINDOWS_SHORTCUT_DIRS")
        else [
            str(path)
            for path in WINDOWS_SHORTCUT_DEFAULTS
            if path and str(path).strip() not in {"", "."}
        ]
    )
    if entry.strip()
)


@dataclass(slots=True)
class AppInfo:
    """单个应用的元数据。"""

    name: str
    path: str
    keywords: List[str] = field(default_factory=list)
    hotkey: str | None = None
    # 当检测到窗口隐藏在系统托盘且未最小化时，尝试通过 Shell 再次“打开”以唤起主窗体
    relaunch_when_tray_hidden: bool = False
    # 所有激活方法失败后，最后再通过 Shell 打开一次作为兜底
    shell_fallback_on_fail: bool = False

    def score(self, query: str) -> int:
        """为匹配打分，用于找到最优应用。"""

        q = query.lower().strip()
        if not q:
            return 0

        name = self.name.lower()
        score = 0
        if name == q:
            return 100
        if name.startswith(q):
            score = max(score, 90)
        if q in name:
            score = max(score, 70)

        for kw in self.keywords:
            k = kw.lower()
            if k == q:
                score = max(score, 80)
            elif k.startswith(q):
                score = max(score, 60)
            elif q in k:
                score = max(score, 40)

        return score


class AppRegistry:
    """应用注册表，负责搜索与序列化。"""

    def __init__(self, apps: Sequence[AppInfo] | None = None) -> None:
        self._apps: List[AppInfo] = []
        if apps:
            self.extend(apps)

    @property
    def apps(self) -> List[AppInfo]:
        return list(self._apps)

    def extend(self, apps: Sequence[AppInfo]) -> None:
        for app in apps:
            self.add(app)

    def add(self, app: AppInfo) -> None:
        if not app.name or not app.path:
            return
        lower = app.name.lower()
        if any(existing.name.lower() == lower or existing.path == app.path for existing in self._apps):
            return
        self._apps.append(app)

    def find(self, query: str) -> AppInfo | None:
        candidates = [
            (app, app.score(query))
            for app in self._apps
        ]
        candidates = [item for item in candidates if item[1] > 0]
        candidates.sort(key=lambda item: item[1], reverse=True)
        return candidates[0][0] if candidates else None

    def dump(self) -> List[dict]:
        return [
            {
                "name": app.name,
                "path": app.path,
                "keywords": app.keywords,
                "hotkey": app.hotkey,
                "relaunch_when_tray_hidden": app.relaunch_when_tray_hidden,
                "shell_fallback_on_fail": app.shell_fallback_on_fail,
            }
            for app in self._apps
        ]


def _clean_keywords(value: Iterable[str] | None) -> List[str]:
    if not value:
        return []
    return sorted({kw.strip() for kw in value if kw and kw.strip()})


def _keywords_from_name(name: str) -> List[str]:
    tokens = {name, name.lower()}
    normalized = name.replace("_", " ").replace("-", " ")
    tokens.update(part for part in normalized.split() if part)
    return _clean_keywords(tokens)


def _app_from_mapping(data: dict) -> AppInfo | None:
    name = str(data.get("name", "")).strip()
    path = str(data.get("path", "")).strip()
    if not name or not path:
        return None
    keywords = data.get("keywords", [])
    hotkey = data.get("hotkey")
    relaunch_when_tray_hidden = bool(data.get("relaunch_when_tray_hidden", False))
    shell_fallback_on_fail = bool(data.get("shell_fallback_on_fail", False))
    return AppInfo(
        name=name,
        path=path,
        keywords=_clean_keywords(keywords),
        hotkey=hotkey,
        relaunch_when_tray_hidden=relaunch_when_tray_hidden,
        shell_fallback_on_fail=shell_fallback_on_fail,
    )


def load_from_env(var: str = "MCP_APPS") -> List[AppInfo]:
    raw = os.environ.get(var)
    if not raw:
        return []

    raw = raw.strip()
    apps: List[AppInfo] = []
    try:
        if raw.startswith("["):
            parsed = json.loads(raw)
            for item in parsed:
                app = _app_from_mapping(item)
                if app:
                    apps.append(app)
        else:
            entries = [segment.strip() for segment in raw.split("|") if segment.strip()]
            for entry in entries:
                parts = [p.strip() for p in entry.split(";")]
                if len(parts) < 2:
                    continue
                name, app_path = parts[:2]
                keywords = parts[2].split(",") if len(parts) > 2 else []
                hotkey = parts[3] if len(parts) > 3 else None
                app = AppInfo(name=name, path=app_path, keywords=_clean_keywords(keywords), hotkey=hotkey)
                apps.append(app)
    except json.JSONDecodeError as exc:
        raise ValueError(f"无法解析环境变量 {var}: {exc}") from exc

    return apps


def load_from_config(paths: Sequence[Path] = DEFAULT_CONFIG_PATHS) -> List[AppInfo]:
    for path in paths:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"配置文件 {path} 解析失败: {exc}") from exc

        payload = data.get("apps", []) if isinstance(data, dict) else data
        apps = [_app_from_mapping(item) for item in payload]
        return [app for app in apps if app]
    return []


def _discover_windows_shortcuts(limit: int | None = None) -> List[AppInfo]:
    apps: List[AppInfo] = []
    max_items = limit or AUTO_DISCOVER_LIMIT
    for base in WINDOWS_SHORTCUT_DIRS:
        if not base or not base.exists():
            continue
        for shortcut in base.rglob("*.lnk"):
            name = shortcut.stem.strip()
            if not name:
                continue
            apps.append(AppInfo(name=name, path=str(shortcut), keywords=_keywords_from_name(name)))
            if len(apps) >= max_items:
                return apps
    return apps


def discover_windows_apps(limit: int | None = None) -> List[AppInfo]:
    if platform.system().lower() != "windows":
        return []

    max_items = limit or AUTO_DISCOVER_LIMIT
    discovered: List[AppInfo] = []
    for entry in DEFAULT_WINDOWS_APPS:
        if len(discovered) >= max_items:
            return discovered
        paths = entry.get("paths", [])
        if isinstance(paths, str):
            paths = [paths]
        for candidate in paths:
            if candidate and Path(candidate).exists():
                app = AppInfo(
                    name=entry["name"],
                    path=candidate,
                    keywords=_clean_keywords(entry.get("keywords")),
                    hotkey=entry.get("hotkey"),
                    relaunch_when_tray_hidden=bool(entry.get("relaunch_when_tray_hidden", False)),
                    shell_fallback_on_fail=bool(entry.get("shell_fallback_on_fail", False)),
                )
                discovered.append(app)
                break

    # Start Menu 快捷方式扫描
    remaining = max_items - len(discovered)
    if remaining > 0 and WINDOWS_SHORTCUT_DIRS:
        discovered.extend(_discover_windows_shortcuts(limit=remaining))
    return discovered


def discover_macos_apps(limit: int | None = None) -> List[AppInfo]:
    if platform.system().lower() != "darwin":
        return []

    max_items = limit or AUTO_DISCOVER_LIMIT
    apps: List[AppInfo] = []
    seen_paths: set[str] = set()

    def add_app(info: AppInfo) -> None:
        if info.path in seen_paths:
            return
        seen_paths.add(info.path)
        apps.append(info)

    # 先加入内置常用应用，保证最小可用集合
    for entry in DEFAULT_MAC_APPS:
        candidate = entry["path"]
        if Path(candidate).exists():
            add_app(
                AppInfo(
                    name=entry["name"],
                    path=candidate,
                    keywords=_clean_keywords(entry.get("keywords")),
                )
            )
            if len(apps) >= max_items:
                return apps

    # 遍历常见应用目录
    for base in MAC_APPLICATION_DIRS:
        if not base.exists():
            continue
        for app_dir in base.rglob("*.app"):
            if ".app/Contents/" in str(app_dir):
                continue
            if not app_dir.is_dir():
                continue
            add_app(
                AppInfo(
                    name=app_dir.stem,
                    path=str(app_dir),
                    keywords=_keywords_from_name(app_dir.stem),
                )
            )
            if len(apps) >= max_items:
                return apps
    return apps


def build_registry(auto_discover: bool = True) -> AppRegistry:
    registry = AppRegistry()
    registry.extend(load_from_config())
    registry.extend(load_from_env())

    if auto_discover:
        registry.extend(discover_windows_apps())
        registry.extend(discover_macos_apps())

    return registry
