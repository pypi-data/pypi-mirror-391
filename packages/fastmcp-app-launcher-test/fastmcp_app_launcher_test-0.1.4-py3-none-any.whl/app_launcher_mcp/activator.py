"""跨平台应用激活逻辑 - 简化版（避免重复启动）"""

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
    """使用 win32 API 激活托盘/后台应用"""

    def __init__(self) -> None:
        self.steps: list[str] = []

    def activate(self, app: AppInfo) -> Dict[str, Any]:
        """主激活逻辑"""
        self.steps.clear()
        
        if not HAS_WIN32:
            self.steps.append("pywin32 未安装，回退到直接启动")
            launched = self.launch_process(app.path)
            return self._result(launched, "pywin32 不可用，已直接启动应用")

        # 获取进程名
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
            else:
                self.steps.append("通过标题也未找到窗口")

        # 2. 如果找到窗口，尝试激活
        if hwnd:
            self.steps.append(f"检测到 {app.name} 已运行 (hwnd={hwnd})")
            
            # 获取窗口状态
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_iconic = win32gui.IsIconic(hwnd)
            title = win32gui.GetWindowText(hwnd)
            self.steps.append(f"窗口状态: 标题='{title}', 可见={is_visible}, 最小化={is_iconic}")
            
            # 尝试温和激活
            if self.gentle_activate(hwnd):
                return self._result(True, f"成功激活 {app.name}")
            
            # 温和激活失败（可能在托盘），尝试 Shell start 命令
            self.steps.append("温和激活失败，尝试使用 Shell start 命令唤起")
            if self.shell_start(app.path):
                self.steps.append("Shell start 命令执行成功")
                time.sleep(1.0)  # 等待应用响应
                # 再次检查窗口是否变为可见
                if win32gui.IsWindowVisible(hwnd):
                    self.steps.append("窗口已变为可见")
                    self.gentle_activate(hwnd)
                    return self._result(True, f"通过 Shell start 成功唤起 {app.name}")
                return self._result(True, f"已发送唤起命令到 {app.name}")
            
            # 所有方法都失败
            self.steps.append("所有激活方法均失败")
            return self._result(True, f"{app.name} 已在运行（请手动点击托盘图标）")
        
        # 3. 窗口未找到，启动新实例
        self.steps.append(f"未检测到 {app.name} 进程，准备启动")
        self.steps.append(f"启动路径: {app.path}")
        
        launched = self.launch_process(app.path)
        if not launched:
            self.steps.append("launch_process 返回失败")
            return self._result(False, "无法启动应用")
        
        self.steps.append("launch_process 返回成功，等待窗口出现")
        
        # 等待新进程的窗口出现
        if self.wait_for_window(process_name, timeout=5.0):
            self.steps.append("检测到新窗口")
            hwnd = self.find_window_by_process(process_name)
            if hwnd:
                self.steps.append(f"找到新窗口 hwnd={hwnd}，尝试置前")
                self.gentle_activate(hwnd)
            return self._result(True, f"已启动 {app.name}")
        else:
            self.steps.append("等待超时，未检测到窗口（应用可能正在启动）")
            return self._result(True, f"已启动 {app.name}（窗口未出现）")

    def gentle_activate(self, hwnd: int) -> bool:
        """温和激活窗口"""
        try:
            self.steps.append("开始温和激活")
            
            # 获取窗口状态
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_iconic = win32gui.IsIconic(hwnd)
            
            # 1. 恢复最小化窗口
            if is_iconic:
                self.steps.append("窗口已最小化，正在恢复")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)
            elif not is_visible:
                # 窗口不可见且未最小化 = 托盘隐藏
                self.steps.append("窗口在托盘中（不可见且未最小化）")
                self.steps.append("托盘应用无法通过 API 强制显示，需要用户手动点击")
                return False  # 返回失败，避免崩溃
            
            # 2. 置前（只对可见或已恢复的窗口）
            try:
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.1)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
                
                # 验证
                fg_hwnd = win32gui.GetForegroundWindow()
                if fg_hwnd == hwnd:
                    self.steps.append("温和激活成功（已获得焦点）")
                    return True
                else:
                    self.steps.append("温和激活完成（但未获得焦点）")
                    return True
            except Exception as e:
                self.steps.append(f"置前失败: {e}")
                return False
                
        except Exception as exc:
            self.steps.append(f"温和激活失败: {exc}")
            return False

    @staticmethod
    def find_window_by_title(app_name: str):
        """通过窗口标题查找"""
        if not HAS_WIN32:
            return None
            
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
        
        try:
            win32gui.EnumWindows(callback, None)
        except Exception:
            return None
        
        if hwnds:
            hwnds.sort(key=lambda x: x[1], reverse=True)
            return hwnds[0][0]
        return None

    @staticmethod
    def find_window_by_process(process_name: str):
        """查找进程对应的窗口"""
        if not HAS_WIN32:
            return None
            
        visible_hwnds: list[tuple[int, str, int]] = []
        hidden_hwnds: list[tuple[int, str, int]] = []
        target = process_name.lower().replace(".exe", "")
        aliases = PROCESS_ALIASES.get(target, set())
        candidates = {target, *aliases}
        
        # 黑名单
        IGNORE_TITLES = {
            "缩略图", "thumbnail", "popup", "tooltip", "menu", "context",
            "qmaiservice", "qqexternal", "txguiservice", "qqservice", "qqprotect",
            "service", "helper", "daemon", "watcher", "guard", "update", "updater",
            "launcher", "crash", "reporter"
        }

        def callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if not title or len(title) < 2:
                return True
            
            # 过滤服务窗口
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
                    
                    # 区分可见和隐藏
                    if win32gui.IsWindowVisible(hwnd):
                        visible_hwnds.append((hwnd, title, style))
                    else:
                        hidden_hwnds.append((hwnd, title, style))
                except Exception:
                    pass
            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception:
            return None
        
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
    def shell_start(app_path: str) -> bool:
        """使用 Windows Shell start 命令启动/唤起应用"""
        try:
            LOGGER.info(f"使用 Shell start 命令: {app_path}")
            
            # 使用 start "" "path" 命令
            # 这个命令可以唤起托盘中的应用
            command = f'start "" "{app_path}"'
            
            # 使用 shell=True 让 Windows 处理 start 命令
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            LOGGER.info("Shell start 命令执行成功")
            return True
        except Exception as exc:
            LOGGER.error(f"Shell start 失败: {exc}")
            return False

    @staticmethod
    def launch_process(app_path: str) -> bool:
        """启动应用进程"""
        try:
            if not os.path.exists(app_path):
                LOGGER.error(f"应用路径不存在: {app_path}")
                return False
            
            LOGGER.info(f"正在启动应用: {app_path}")
            
            # 使用 os.startfile（Windows 最安全的方式）
            if os.path.splitext(app_path)[1].lower() in ['.lnk', '.exe']:
                os.startfile(app_path)  # type: ignore[attr-defined]
                LOGGER.info("使用 os.startfile 启动成功")
                return True
            
            # 其他情况使用 subprocess
            subprocess.Popen(
                [app_path],
                shell=False,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                start_new_session=True
            )
            LOGGER.info("使用 subprocess.Popen 启动成功")
            return True
        except Exception as exc:
            LOGGER.error(f"启动应用失败: {type(exc).__name__}: {exc}")
            return False

    def _result(self, success: bool, message: str) -> Dict[str, Any]:
        """返回结果"""
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
