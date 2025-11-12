"""跨平台应用激活逻辑 - 重构版（避免重复启动和激进操作）"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from .apps import AppInfo

LOGGER = logging.getLogger(__name__)
SYSTEM = platform.system().lower()

PROCESS_ALIASES = {
    "qq": {"qq", "qqprotect", "qqsclaunch", "qqsclauncher", "qqexternal", "txguiservice"},
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
        """主激活逻辑 - 改进的托盘应用处理"""
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

        # 1. 查找窗口（多种方式）
        self.steps.append(f"查找进程: {process_name}")
        hwnd = self.find_window_by_process(process_name)
        
        if not hwnd:
            self.steps.append("通过进程名未找到窗口，尝试通过标题查找")
            hwnd = self.find_window_by_title(app.name)
            if hwnd:
                self.steps.append(f"通过窗口标题找到窗口 (hwnd={hwnd})")

        # 2. 分析应用状态并处理
        if hwnd:
            self.steps.append(f"检测到 {process_name} 进程已运行 (hwnd={hwnd})")
            
            # 检查窗口状态
            window_state = self._check_window_state(hwnd)
            self.steps.append(f"窗口状态: {window_state}")
            
            # 根据状态采取不同策略
            if window_state == "正常":
                # 温和激活
                if self.gentle_activate(hwnd):
                    return self._result(True, "成功激活已运行的应用")
            elif window_state == "托盘隐藏":
                # 托盘隐藏的特殊处理
                if app.relaunch_when_tray_hidden:
                    self.steps.append("检测到托盘隐藏，尝试重新启动")
                    if self._relaunch_tray_app(app, process_name):
                        return self._result(True, "已重新启动托盘隐藏的应用")
                else:
                    # 尝试温和恢复
                    if self._restore_from_tray(hwnd):
                        return self._result(True, "已从托盘恢复应用")
            
            # 通用兜底：尝试Shell重新打开
            self.steps.append("尝试通过Shell重新打开")
            if self._shell_reopen(app.path):
                return self._result(True, "通过Shell重新打开成功")
            
            return self._result(True, f"{app.name} 已在运行，但无法激活（可能需要手动操作）")
        
        # 3. 未找到窗口，启动新实例
        self.steps.append(f"未检测到 {process_name} 进程，准备启动")
        self.steps.append(f"启动路径: {app.path}")
        
        launched = self.launch_process(app.path)
        if launched:
            self.steps.append("launch_process 返回成功，等待窗口出现")
            
            # 等待新进程的窗口出现
            if self.wait_for_window(process_name, timeout=8.0):  # 增加超时时间
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
            
            # Shell 回退机制
            if app.shell_fallback_on_fail:
                self.steps.append("尝试Shell回退机制")
                if self._shell_fallback(app.path):
                    return self._result(True, "通过Shell回退成功启动应用")
                else:
                    self.steps.append("Shell回退也失败")
            
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
            
            # 3. 温和置前（改进版）
            try:
                # 先尝试 BringWindowToTop
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.1)
                
                # 使用更可靠的方式设置前台窗口
                current_hwnd = win32gui.GetForegroundWindow()
                if current_hwnd != hwnd:
                    # 获取当前线程和窗口线程
                    current_thread_id = win32process.GetCurrentThreadId()
                    window_thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
                    
                    if current_thread_id != window_thread_id:
                        # 临时附加输入线程
                        win32process.AttachThreadInput(window_thread_id, current_thread_id, True)
                        try:
                            win32gui.SetForegroundWindow(hwnd)
                        finally:
                            win32process.AttachThreadInput(window_thread_id, current_thread_id, False)
                    else:
                        win32gui.SetForegroundWindow(hwnd)
                
                time.sleep(0.2)
                
                # 验证是否成功
                if win32gui.GetForegroundWindow() == hwnd:
                    self.steps.append("温和激活成功（已获得焦点）")
                    return True
                else:
                    self.steps.append("温和激活完成（窗口已显示但未获得焦点）")
                    return True  # 窗口已显示，算部分成功
            except Exception as e:
                self.steps.append(f"置前失败: {e}")
                return False
                
        except Exception as exc:
            self.steps.append(f"温和激活失败: {exc}")
            return False

    @staticmethod
    def find_window_by_title(app_name: str):
        """通过窗口标题查找窗口（改进版，支持模糊匹配）"""
        hwnds: list[tuple[int, int]] = []
        search_terms = app_name.lower().split()
        
        # QQ特殊处理
        if "qq" in app_name.lower():
            search_terms.extend(["qq", "腾讯qq", "tencent"])
        
        def callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if not title or len(title) < 2:  # 跳过空标题和过短标题
                return True
            
            title_lower = title.lower()
            score = 0
            
            # 精确匹配得分最高
            if app_name.lower() in title_lower:
                score += 50
            
            # 关键词匹配
            for term in search_terms:
                if term in title_lower:
                    score += 10
            
            # 窗口可见性加分
            if win32gui.IsWindowVisible(hwnd):
                score += 5
            
            # 有标题栏加分
            try:
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                if style & win32con.WS_CAPTION:
                    score += 3
            except Exception:
                pass
            
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
        
        # 扩展黑名单 - QQ相关服务窗口
        IGNORE_TITLES = {
            "缩略图", "thumbnail", "popup", "tooltip", "menu", "context",
            "qmaiservice", "qqexternal", "txguiservice", "qqservice", "qqprotect",
            "service", "helper", "daemon", "watcher", "guard", "update", "updater",
            "launcher", "crash", "reporter", "tip", "通知", "notify"
        }
        
        # Windows消息常量
        WM_CLOSE = 0x0010

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
        """安全启动应用进程（改进版）"""
        try:
            if not os.path.exists(app_path):
                LOGGER.error(f"应用路径不存在: {app_path}")
                return False
            
            LOGGER.info(f"正在启动应用: {app_path}")
            
            # 对于快捷方式，先解析目标
            if app_path.lower().endswith('.lnk'):
                try:
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(app_path)
                    target_path = shortcut.Targetpath
                    if target_path and os.path.exists(target_path):
                        app_path = target_path
                        LOGGER.info(f"解析快捷方式目标: {app_path}")
                except Exception as e:
                    LOGGER.warning(f"解析快捷方式失败: {e}")
            
            # 对于可执行文件，os.startfile() 最安全
            if os.path.splitext(app_path)[1].lower() == '.exe':
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

    def _check_window_state(self, hwnd: int) -> str:
        """检查窗口状态：正常、最小化、隐藏、托盘隐藏"""
        try:
            if win32gui.IsIconic(hwnd):
                return "最小化"
            
            if not win32gui.IsWindowVisible(hwnd):
                # 进一步判断是否可能是托盘隐藏
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                
                # 托盘窗口通常有 WS_EX_TOOLWINDOW 样式或没有标题栏
                if (ex_style & win32con.WS_EX_TOOLWINDOW) or not (style & win32con.WS_CAPTION):
                    return "托盘隐藏"
                else:
                    return "隐藏"
            
            return "正常"
        except Exception:
            return "未知"

    def _restore_from_tray(self, hwnd: int) -> bool:
        """尝试从托盘恢复窗口"""
        try:
            self.steps.append("尝试从托盘恢复")
            
            # 1. 先显示窗口
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            time.sleep(0.3)
            
            # 2. 恢复正常窗口样式
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            # 移除工具窗口样式
            if ex_style & win32con.WS_EX_TOOLWINDOW:
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style & ~win32con.WS_EX_TOOLWINDOW)
            
            # 确保有标题栏
            if not (style & win32con.WS_CAPTION):
                win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style | win32con.WS_CAPTION)
            
            # 3. 尝试激活
            return self.gentle_activate(hwnd)
            
        except Exception as e:
            self.steps.append(f"托盘恢复失败: {e}")
            return False

    def _shell_reopen(self, app_path: str) -> bool:
        """通过Shell重新打开（用于已运行但无法激活的情况）"""
        try:
            self.steps.append("通过Shell重新打开应用")
            os.startfile(app_path)  # type: ignore[attr-defined]
            time.sleep(1)  # 给应用一点时间响应
            return True
        except Exception as e:
            self.steps.append(f"Shell重新打开失败: {e}")
            return False

    def _relaunch_tray_app(self, app: AppInfo, process_name: str) -> bool:
        """安全重新启动托盘应用（非强制）"""
        try:
            self.steps.append("请求应用正常退出")
            if self._graceful_exit(process_name):
                time.sleep(2)  # 等待应用正常退出
                self.steps.append("重新启动应用")
                return self.launch_process(app.path)
            else:
                self.steps.append("应用拒绝退出，放弃重新启动")
                return False
        except Exception as e:
            self.steps.append(f"托盘重新启动失败: {e}")
            return False

    def _shell_fallback(self, app_path: str) -> bool:
        """Shell回退机制"""
        try:
            self.steps.append("使用Shell执行回退")
            os.startfile(app_path)  # type: ignore[attr-defined]
            return True
        except Exception as e:
            self.steps.append(f"Shell回退失败: {e}")
            return False

    @staticmethod
    def _graceful_exit(process_name: str) -> bool:
        """优雅请求应用退出（非强制）"""
        try:
            import subprocess
            # 首先尝试正常关闭（不带/F参数）
            result = subprocess.run(
                ["taskkill", "/IM", process_name],  # 不带 /F 参数
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True
            else:
                # 正常关闭失败，尝试发送WM_CLOSE消息
                return self._send_close_message(process_name)
                
        except Exception:
            return False

    @staticmethod
    def _send_close_message(process_name: str) -> bool:
        """向窗口发送关闭消息"""
        try:
            if not HAS_WIN32:
                return False
                
            # 查找进程的主窗口
            found = False
            def callback(hwnd, _):
                nonlocal found
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    handle = win32api.OpenProcess(
                        win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                        False, pid
                    )
                    exe_name = win32process.GetModuleFileNameEx(handle, 0).lower()
                    win32api.CloseHandle(handle)
                    
                    if process_name.lower() in exe_name.lower():
                        # 发送WM_CLOSE消息请求关闭
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        found = True
                except Exception:
                    pass
                return True
            
            win32gui.EnumWindows(callback, None)
            return found
            
        except Exception:
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


def debug_app_state(app_path: str) -> Dict[str, Any]:
    """调试应用状态（仅Windows）"""
    if SYSTEM != "windows" or not HAS_WIN32:
        return {"available": False, "message": "仅支持Windows系统且需要pywin32"}
    
    try:
        process_name = Path(app_path).stem + ".exe"
        activator = WindowsTrayActivator()
        
        # 查找窗口
        hwnd_by_process = activator.find_window_by_process(process_name)
        hwnd_by_title = activator.find_window_by_title(process_name.replace(".exe", ""))
        
        # 检查进程是否存在
        import psutil
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        result = {
            "available": True,
            "process_name": process_name,
            "window_by_process": hwnd_by_process,
            "window_by_title": hwnd_by_title,
            "running_processes": processes,
            "window_state": None
        }
        
        if hwnd_by_process:
            result["window_state"] = activator._check_window_state(hwnd_by_process)
        
        return result
        
    except Exception as e:
        return {"available": True, "error": str(e)}
