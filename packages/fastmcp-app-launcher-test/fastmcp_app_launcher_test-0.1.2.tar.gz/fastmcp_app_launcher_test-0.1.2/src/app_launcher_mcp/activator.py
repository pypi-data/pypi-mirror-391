"""跨平台应用激活逻辑 - 重构版（避免重复启动和激进操作）"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

from .apps import AppInfo

LOGGER = logging.getLogger(__name__)
SYSTEM = platform.system().lower()

PROCESS_ALIASES = {
    "qq": {"qq", "qqprotect", "qqsclaunch", "qqsclauncher", "qqbrowser"},
    "wechat": {"wechat", "weixin", "wechatapp"},
    "tim": {"tim"},
    "dingtalk": {"dingtalk", "钉钉"},
}

if SYSTEM == "windows":
    try:
        import win32api  # type: ignore
        import win32con  # type: ignore
        import win32gui  # type: ignore
        import win32process  # type: ignore
        HAS_WIN32 = True
    except Exception:
        HAS_WIN32 = False
else:
    HAS_WIN32 = False


class WindowsTrayActivator:
    """使用 win32 API 激活托盘/后台应用 - 简化版"""

    def __init__(self) -> None:
        self.steps: list[str] = []

    def activate(self, app: AppInfo) -> Dict[str, Any]:
        """主激活逻辑 - 简化流程，避免重复启动"""
        self.steps.clear()
        
        if not HAS_WIN32:
            self.steps.append("pywin32 未安装，回退到直接启动")
            launched = self.launch_process(app.path)
            return self._result(launched, "pywin32 不可用，已直接启动应用")

        # 处理快捷方式的进程名
        if app.path.lower().endswith(".lnk"):
            clean_name = app.name.replace(" ", "").replace("-", "")
            process_name = clean_name + ".exe"
            self.steps.append(f"快捷方式推断进程名: {process_name}")
        else:
            process_name = Path(app.path).stem + ".exe"

        # 1. 查找窗口
        self.steps.append(f"查找进程: {process_name}")
        hwnd = self.find_window_by_process(process_name)
        
        if not hwnd:
            self.steps.append("通过进程名未找到窗口，尝试通过标题查找")
            hwnd = self.find_window_by_title(app.name)
            if hwnd:
                self.steps.append(f"通过窗口标题找到窗口 (hwnd={hwnd})")

        # 2. 如果找到窗口，尝试激活（不重复启动！）
        if hwnd:
            self.steps.append(f"检测到 {process_name} 进程已运行 (hwnd={hwnd})")
            
            # 温和激活
            if self.gentle_activate(hwnd):
                return self._result(True, "成功激活已运行的应用")
            
            # 激活失败，但应用确实在运行
            self.steps.append("温和激活失败，应用可能在托盘中")
            return self._result(True, f"{app.name} 已在运行（请手动点击托盘图标打开）")
        
        # 3. 窗口未找到，启动新实例（仅此一次！）
        self.steps.append(f"未检测到 {process_name} 进程，准备启动")
        self.steps.append(f"启动路径: {app.path}")
        
        launched = self.launch_process(app.path)
        if launched:
            self.steps.append("launch_process 返回成功，等待窗口出现")
            
            # 等待新进程的窗口出现
            if self.wait_for_window(process_name, timeout=5.0):
                self.steps.append("检测到新窗口")
                hwnd = self.find_window_by_process(process_name)
                if hwnd:
                    self.steps.append(f"找到新窗口 hwnd={hwnd}，尝试置前")
                    self.gentle_activate(hwnd)
                return self._result(True, "已启动新应用实例")
            else:
                self.steps.append("等待超时，未检测到窗口（应用可能正在启动）")
            return self._result(True, "已启动应用（未检测到窗口）")
        else:
            self.steps.append("launch_process 返回失败")
            return self._result(False, "无法启动应用")

    def gentle_activate(self, hwnd: int) -> bool:
        """温和激活窗口，不打断应用自身逻辑"""
        try:
            self.steps.append("尝试温和激活")
            
            # 1. 恢复最小化
            if win32gui.IsIconic(hwnd):
                self.steps.append("恢复最小化窗口")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)
            
            # 2. 显示隐藏窗口
            if not win32gui.IsWindowVisible(hwnd):
                self.steps.append("显示隐藏窗口")
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.3)
            
            # 3. 温和置前（不使用 AttachThreadInput）
            try:
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.1)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
                
                # 验证是否成功
                if win32gui.GetForegroundWindow() == hwnd:
                    self.steps.append("温和激活成功（已获得焦点）")
                    return True
                else:
                    self.steps.append("温和激活完成（但未获得焦点）")
                    return True  # 窗口已显示，算部分成功
            except Exception as e:
                self.steps.append(f"置前失败: {e}")
                return False
                
        except Exception as exc:
            self.steps.append(f"温和激活失败: {exc}")
            return False

    @staticmethod
    def find_window_by_title(app_name: str):
        """通过窗口标题查找窗口（备用方法）"""
        hwnds: list[tuple[int, int]] = []
        search_terms = app_name.lower().split()
        
        def callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return True
            
            title_lower = title.lower()
            score = sum(1 for term in search_terms if term in title_lower)
            
            if score > 0:
                hwnds.append((hwnd, score))
            return True
        
        win32gui.EnumWindows(callback, None)
        
        if hwnds:
            hwnds.sort(key=lambda x: x[1], reverse=True)
            return hwnds[0][0]
        return None

    @staticmethod
    def find_window_by_process(process_name: str):
        """查找进程对应的窗口句柄 - 严格过滤"""
        visible_hwnds: list[tuple[int, str, int]] = []
        hidden_hwnds: list[tuple[int, str, int]] = []
        target = process_name.lower().replace(".exe", "")
        aliases = PROCESS_ALIASES.get(target, set())
        candidates = {target, *aliases}
        
        # 扩展黑名单
        IGNORE_TITLES = {
            "缩略图", "thumbnail", "popup", "tooltip", "menu", "context",
            "qmaiservice", "qqexternal", "txguiservice", "qqservice", "qqprotect",
            "service", "helper", "daemon", "watcher", "guard", "update", "updater",
            "launcher", "crash", "reporter"
        }

        def callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            # 跳过没有标题或标题太短的窗口
            if not title or len(title) < 2:
                return True
            
            # 跳过服务窗口
            title_lower = title.lower()
            if any(ignore in title_lower for ignore in IGNORE_TITLES):
                return True
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    False,
                    pid,
                )
                exe_name = win32process.GetModuleFileNameEx(handle, 0).lower()
                win32api.CloseHandle(handle)
            except Exception:
                return True

            exe_basename = Path(exe_name).stem.lower()
            if exe_basename in candidates or any(candidate in exe_name for candidate in candidates):
                try:
                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    
                    # 过滤工具窗口
                    if ex_style & win32con.WS_EX_TOOLWINDOW:
                        return True
                    
                    # 必须有标题栏
                    if not (style & win32con.WS_CAPTION):
                        return True
                    
                    # 区分可见和隐藏窗口
                    if win32gui.IsWindowVisible(hwnd):
                        visible_hwnds.append((hwnd, title, style))
                    else:
                        hidden_hwnds.append((hwnd, title, style))
                except Exception:
                    pass
            return True

        win32gui.EnumWindows(callback, None)
        
        # 窗口评分
        def score_window(item):
            hwnd, title, style = item
            score = 0
            
            if bool(style & win32con.WS_CAPTION):
                score += 10
            if bool(style & win32con.WS_SYSMENU):
                score += 10
            if bool(style & win32con.WS_MINIMIZEBOX):
                score += 8
            if bool(style & win32con.WS_MAXIMIZEBOX):
                score += 8
            
            title_lower = title.lower()
            if target in title_lower:
                score += 30
            if title_lower == target or title == target.upper():
                score += 50
            
            if item in visible_hwnds:
                score += 5
            
            return score
        
        # 返回分数最高的窗口
        all_windows = visible_hwnds + hidden_hwnds
        if all_windows:
            all_windows.sort(key=score_window, reverse=True)
            return all_windows[0][0]
        
        return None

    @staticmethod
    def wait_for_window(process_name: str, timeout: float = 5.0) -> bool:
        """等待窗口出现"""
        end = time.time() + timeout
        while time.time() < end:
            hwnd = WindowsTrayActivator.find_window_by_process(process_name)
            if hwnd:
                return True
            time.sleep(0.2)
        return False

    @staticmethod
    def launch_process(app_path: str) -> bool:
        """安全启动应用进程"""
        try:
            if not os.path.exists(app_path):
                LOGGER.error(f"应用路径不存在: {app_path}")
                return False
            
            LOGGER.info(f"正在启动应用: {app_path}")
            
            # 对于快捷方式和可执行文件，os.startfile() 最安全
            if os.path.splitext(app_path)[1].lower() in ['.lnk', '.exe']:
                os.startfile(app_path)  # type: ignore[attr-defined]
                LOGGER.info("使用 os.startfile 启动")
                return True
            
            # 其他情况使用 DETACHED_PROCESS
            subprocess.Popen(
                [app_path],
                shell=False,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                start_new_session=True
            )
            LOGGER.info("使用 subprocess.Popen 启动")
            return True
        except Exception as exc:
            LOGGER.error(f"启动应用失败: {type(exc).__name__}: {exc}")
            return False

    def _result(self, success: bool, message: str) -> Dict[str, Any]:
        """返回结果并记录日志"""
        LOGGER.info(f"激活结果: {message}")
        LOGGER.debug(f"操作步骤:\n" + "\n".join(f"  {i+1}. {step}" for i, step in enumerate(self.steps)))
        
        return {
            "success": success,
            "message": message,
            "steps": list(self.steps),
        }


def open_app(app: AppInfo) -> Dict[str, Any]:
    """根据平台打开应用"""

    if SYSTEM == "windows":
        activator = WindowsTrayActivator()
        return activator.activate(app)

    if SYSTEM == "darwin":
        subprocess.run(["open", app.path], check=True)
        return {"success": True, "message": f"已通过 open 启动 {app.name}", "steps": []}

    subprocess.Popen([app.path], shell=False)
    return {"success": True, "message": f"已执行 {app.path}", "steps": []}
