"""跨平台应用激活逻辑。"""

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
    try:  # pragma: no cover - Windows 才能导入
        import win32api  # type: ignore
        import win32con  # type: ignore
        import win32gui  # type: ignore
        import win32process  # type: ignore
        HAS_WIN32 = True
    except Exception:  # pragma: no cover
        HAS_WIN32 = False

    try:  # pragma: no cover
        from pywinauto import Application  # type: ignore

        HAS_PYWINAUTO = True
    except Exception:  # pragma: no cover
        HAS_PYWINAUTO = False
else:  # 非 Windows 平台无需这些依赖
    HAS_WIN32 = False
    HAS_PYWINAUTO = False


class WindowsTrayActivator:
    """使用 win32 API 激活托盘/后台应用。"""

    def __init__(self) -> None:
        self.steps: list[str] = []

    def activate(self, app: AppInfo) -> Dict[str, Any]:  # pragma: no cover - Windows 特有
        self.steps.clear()
        if not HAS_WIN32:
            self.steps.append("pywin32 未安装，回退到直接启动")
            launched = self.launch_process(app.path)
            return self._result(launched, "pywin32 不可用，已直接启动应用")

        name_l = (app.name or "").lower()
        path_l = (app.path or "").lower()

        # 处理 .lnk 快捷方式，提取实际的进程名
        if app.path.lower().endswith(".lnk"):
            # 对于快捷方式，尝试从应用名称推断进程名
            # 移除常见的后缀和空格
            clean_name = app.name.replace(" ", "").replace("-", "")
            process_name = clean_name + ".exe"
            self.steps.append(f"快捷方式推断进程名: {process_name}")
        else:
            process_name = Path(app.path).stem + ".exe"

        # 1. 先检查进程是否已经在运行
        self.steps.append(f"查找进程: {process_name}")
        hwnd = self.find_window_by_process(process_name)
        
        # 1.1 如果通过进程名找不到，尝试通过应用名称查找窗口标题
        if not hwnd:
            self.steps.append(f"通过进程名未找到窗口，尝试通过标题查找")
            hwnd = self.find_window_by_title(app.name)
            if hwnd:
                self.steps.append(f"通过窗口标题找到窗口 (hwnd={hwnd})")
            else:
                self.steps.append(f"通过标题也未找到窗口")
        
        if hwnd:
            self.steps.append(f"检测到 {process_name} 进程已运行 (hwnd={hwnd})")
            
            # 1.1 如果有热键，先尝试热键激活
            if app.hotkey and self.send_hotkey(app.hotkey):
                self.steps.append(f"已发送热键 {app.hotkey}")
                time.sleep(0.3)  # 给热键一点时间生效
                if self.bring_window_to_front(hwnd):
                    return self._result(True, "通过热键激活已运行的窗口")
            
            # 1.2 检查窗口是否可见，判断是否为托盘应用
            is_visible = win32gui.IsWindowVisible(hwnd)
            title = win32gui.GetWindowText(hwnd)
            
            if not is_visible:
                # 窗口不可见，很可能是托盘应用
                is_iconic = win32gui.IsIconic(hwnd)
                self.steps.append(f"检测到托盘应用: '{title}' (可见={is_visible}, 最小化={is_iconic})")
                
                if is_iconic:
                    # 最小化到托盘，可以尝试恢复
                    self.steps.append("窗口已最小化，尝试恢复")
                    tray_result = self.activate_tray_app(hwnd)
                    if tray_result:
                        return self._result(True, "成功恢复最小化窗口")
                    else:
                        self.steps.append("恢复失败")
                else:
                    # 完全隐藏的托盘应用，使用温和激活
                    self.steps.append(f"{app.name} 正在系统托盘中运行（不可见）")
                    
                    # 尝试温和激活（不重复启动）
                    if self.gentle_activate(hwnd):
                        return self._result(True, "已尝试温和激活托盘应用")
                    
                    # 温和激活失败，提示用户手动操作
                    self.steps.append("温和激活失败，提示用户手动点击托盘图标")
                    return self._result(True, f"{app.name} 已在系统托盘运行（请手动点击托盘图标打开）")
            
            # 1.3 尝试标准的窗口置前
            self.steps.append(f"尝试置前窗口 hwnd={hwnd}")
            bring_result = self.bring_window_to_front(hwnd)
            if bring_result:
                return self._result(True, "检测到运行中的窗口并置前")
            else:
                self.steps.append(f"高级置前失败，尝试简单方法")
                # 尝试更简单的激活方法
                if self.simple_activate(hwnd):
                    return self._result(True, "通过简单方法激活窗口")
                self.steps.append(f"简单方法也失败，尝试 pywinauto")
            
            # 1.3 尝试 pywinauto
            if self.activate_with_pywinauto(process_name, app.name):
                return self._result(True, "通过 pywinauto 激活窗口")
            
            # 1.4 最后尝试：模拟点击任务栏（如果窗口在任务栏）
            self.steps.append("尝试最后的激活方法")
            if self.activate_by_alt_tab(hwnd):
                return self._result(True, "通过模拟切换激活窗口")

            # 1.5 进程存在但无法激活：可选兜底，通过 Shell 再次打开一次
            try_shell_fallback = (
                bool(getattr(app, "shell_fallback_on_fail", False))
                or path_l.endswith(".lnk")
                or any(key in name_l for key in ("qq", "wechat", "weixin", "tim", "钉钉"))
                or any(key in path_l for key in ("qq", "wechat", "weixin", "tim", "dingtalk"))
            )

            if try_shell_fallback:
                self.steps.append("激活失败，尝试 Shell 兜底唤起")
                try:
                    if self.shell_start(app.path):
                        # 等待可能的主窗体出现
                        if self.wait_for_window(process_name, timeout=5.0):
                            hwnd3 = self.find_window_by_process(process_name)
                            if hwnd3 and (self.bring_window_to_front(hwnd3) or self.simple_activate(hwnd3) or self.activate_by_alt_tab(hwnd3)):
                                return self._result(True, "通过 Shell 兜底唤起并置前")
                        else:
                            self.steps.append("Shell 兜底后未检测到新窗口")
                except Exception as e:
                    self.steps.append(f"Shell 兜底失败: {e}")

            # 1.6 仍无法激活，返回部分成功（不再尝试启动新进程）
            self.steps.append("所有激活方法均失败，但进程确实在运行")
            return self._result(True, f"{app.name} 已在运行（无法激活窗口，可能需要手动切换）")
        
        # 2. 进程未运行，尝试启动新实例
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
                    self.bring_window_to_front(hwnd)
                return self._result(True, "已启动新应用实例")
            else:
                self.steps.append("等待超时，未检测到窗口（应用可能正在启动）")
            return self._result(True, "已启动应用（未检测到窗口）")
        else:
            self.steps.append("launch_process 返回失败")
            return self._result(False, "无法启动应用")

    # --- win32 helpers -------------------------------------------------
    @staticmethod
    def send_hotkey(hotkey: str) -> bool:
        try:
            keys = [k.strip() for k in hotkey.split("+") if k.strip()]
            modifiers = []
            key_code = None
            for key in keys:
                upper = key.lower()
                if upper == "ctrl":
                    modifiers.append(win32con.VK_CONTROL)
                elif upper == "alt":
                    modifiers.append(win32con.VK_MENU)
                elif upper == "shift":
                    modifiers.append(win32con.VK_SHIFT)
                else:
                    key_code = upper
            if not key_code:
                return False

            for mod in modifiers:
                win32api.keybd_event(mod, 0, 0, 0)

            vk = ord(key_code.upper())
            win32api.keybd_event(vk, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
            for mod in reversed(modifiers):
                win32api.keybd_event(mod, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("发送热键失败: %s", exc)
            return False

    @staticmethod
    def find_window_by_title(app_name: str):
        """通过窗口标题查找窗口（备用方法）。"""
        hwnds: list[tuple[int, int]] = []  # (hwnd, score)
        search_terms = app_name.lower().split()
        
        def callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return True
            
            title_lower = title.lower()
            # 计算匹配分数
            score = 0
            for term in search_terms:
                if term in title_lower:
                    score += 1
            
            if score > 0:
                hwnds.append((hwnd, score))
            return True
        
        win32gui.EnumWindows(callback, None)
        
        if hwnds:
            # 返回匹配度最高的窗口
            hwnds.sort(key=lambda x: x[1], reverse=True)
            return hwnds[0][0]
        return None

    @staticmethod
    def find_window_by_process(process_name: str):
        """查找进程对应的窗口句柄，优先返回可见的主窗口。"""
        visible_hwnds: list[tuple[int, str, int]] = []  # (hwnd, title, style)
        hidden_hwnds: list[tuple[int, str, int]] = []
        target = process_name.lower().replace(".exe", "")
        aliases = PROCESS_ALIASES.get(target, set())
        candidates = {target, *aliases}
        
        # 需要过滤的窗口标题关键词（扩展黑名单）
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
            
            # 跳过明显不是主窗口的标题
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
                # 获取窗口样式，判断是否为主窗口
                try:
                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    
                    # 过滤掉工具窗口和消息窗口
                    is_tool_window = bool(ex_style & win32con.WS_EX_TOOLWINDOW)
                    if is_tool_window:
                        return True  # 跳过工具窗口
                    
                    # 必须有标题栏（主窗口特征）
                    has_caption = bool(style & win32con.WS_CAPTION)
                    if not has_caption:
                        return True  # 跳过没有标题栏的窗口
                    
                    # 区分可见和隐藏窗口
                    if win32gui.IsWindowVisible(hwnd):
                        visible_hwnds.append((hwnd, title, style))
                    else:
                        hidden_hwnds.append((hwnd, title, style))
                except Exception:
                    pass  # 忽略无法获取样式的窗口
            return True

        win32gui.EnumWindows(callback, None)
        
        # 优先选择有 WS_CAPTION 样式的窗口（通常是主窗口）
        def is_main_window(item):
            hwnd, title, style = item
            has_caption = bool(style & win32con.WS_CAPTION)
            has_sysmenu = bool(style & win32con.WS_SYSMENU)
            # 标题不能为空或太短
            has_good_title = len(title) > 0 and len(title) < 100
            return has_caption and has_sysmenu and has_good_title
        
        def score_window(item):
            """给窗口打分，分数越高越可能是主窗口"""
            hwnd, title, style = item
            score = 0
            
            # 有标题栏和系统菜单（主窗口特征）
            if bool(style & win32con.WS_CAPTION):
                score += 10
            if bool(style & win32con.WS_SYSMENU):
                score += 10
            
            # 有最小化按钮（主窗口特征）
            if bool(style & win32con.WS_MINIMIZEBOX):
                score += 8
            
            # 有最大化按钮（主窗口特征）
            if bool(style & win32con.WS_MAXIMIZEBOX):
                score += 8
            
            # 标题长度合理（不是空的，也不是很长的服务名）
            if 1 <= len(title) <= 50:
                score += 5
            
            # 标题中包含应用名（如 "QQ"）
            title_lower = title.lower()
            if target in title_lower:
                score += 30  # 提高权重
            
            # 标题就是应用名（完全匹配）
            if title_lower == target or title == target.upper():
                score += 50  # 最高权重
            
            # 不是服务窗口
            if not any(ignore in title_lower for ignore in IGNORE_TITLES):
                score += 15
            else:
                score -= 50  # 服务窗口大幅降分
            
            # 可见窗口优先（但不是决定性因素）
            if item in visible_hwnds:
                score += 5
            
            return score
        
        # 对所有窗口打分，优先返回分数最高的
        all_windows = visible_hwnds + hidden_hwnds
        if all_windows:
            all_windows.sort(key=score_window, reverse=True)
            
            # 记录找到的窗口信息（调试用）
            if len(all_windows) > 1:
                top_windows = all_windows[:3]
                window_info = ", ".join([f"'{w[1]}'({score_window(w)}分)" for w in top_windows])
                LOGGER.debug(f"找到 {len(all_windows)} 个窗口，前3名: {window_info}")
            
            best_window = all_windows[0]
            return best_window[0]
        
        return None

    def gentle_activate(self, hwnd: int) -> bool:
        """温和激活窗口，不打断应用自身逻辑"""
        try:
            self.steps.append("尝试温和激活")
            
            # 1. 只恢复最小化状态
            if win32gui.IsIconic(hwnd):
                self.steps.append("恢复最小化窗口")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)  # 给应用恢复时间
            
            # 2. 显示窗口（但不强制置顶）
            if not win32gui.IsWindowVisible(hwnd):
                self.steps.append("显示隐藏窗口")
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.3)
            
            # 3. 轻量级置前（不使用 AttachThreadInput）
            try:
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.1)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)  # 给应用时间处理
                self.steps.append("温和激活完成")
                return True
            except Exception as e:
                self.steps.append(f"置前失败（但窗口已显示）: {e}")
                return True  # 窗口已显示，算部分成功
                
        except Exception as exc:
            self.steps.append(f"温和激活失败: {exc}")
            return False

    def activate_tray_app(self, hwnd: int) -> bool:
        """专门处理托盘应用的激活（不使用热键）。"""
        try:
            self.steps.append("尝试托盘应用激活方法")
            
            # 1. 确保窗口存在且有效
            if not win32gui.IsWindow(hwnd):
                self.steps.append("窗口句柄无效")
                return False
            
            # 2. 获取窗口信息
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_iconic = win32gui.IsIconic(hwnd)
            title = win32gui.GetWindowText(hwnd)
            
            # 3. 检查窗口样式，确保是可以显示的 UI 窗口
            try:
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                
                # 检查是否是工具窗口或消息窗口（不应该显示）
                is_tool_window = bool(ex_style & win32con.WS_EX_TOOLWINDOW)
                has_caption = bool(style & win32con.WS_CAPTION)
                
                if is_tool_window or not has_caption:
                    self.steps.append(f"窗口类型不适合激活: 工具窗口={is_tool_window}, 无标题栏={not has_caption}")
                    return False
                    
            except Exception as e:
                self.steps.append(f"无法获取窗口样式: {e}")
                return False
            
            self.steps.append(f"托盘窗口: '{title}', 可见={is_visible}, 最小化={is_iconic}")
            
            # 4. 判断窗口状态，决定是否可以安全显示
            if is_iconic:
                # 最小化状态，可以安全恢复
                try:
                    self.steps.append("恢复最小化窗口")
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.2)
                except Exception as e:
                    self.steps.append(f"恢复窗口失败: {e}")
                    return False
            elif not is_visible:
                # 窗口不可见且不是最小化 = 托盘应用
                # 不要强制显示！这会导致某些应用崩溃
                self.steps.append("窗口在托盘中（不可见且未最小化）")
                self.steps.append("托盘应用无法通过 ShowWindow 激活，需要用户手动点击托盘图标")
                return False  # 返回失败，让调用者知道无法激活
            
            # 5. 使用 ctypes 绕过前台窗口限制
            try:
                import ctypes
                # 允许设置前台窗口
                ctypes.windll.user32.AllowSetForegroundWindow(-1)
                time.sleep(0.05)
                
                # 使用 SetWindowPos 置顶
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_SHOWWINDOW = 0x0040
                HWND_TOP = 0
                
                ctypes.windll.user32.SetWindowPos(
                    hwnd, HWND_TOP, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
                )
                time.sleep(0.05)
                
                # 设为前台窗口
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                
                # 验证是否成功
                fg_hwnd = win32gui.GetForegroundWindow()
                if fg_hwnd == hwnd:
                    self.steps.append("托盘应用激活成功（已获得焦点）")
                    return True
                else:
                    self.steps.append("托盘应用已显示（但未获得焦点），尝试进一步置前")
                    # 继续尝试更强的置前方法，若仍失败则返回 False 让上层走后备策略
                    try:
                        if self.bring_window_to_front(hwnd):
                            # 再次确认是否真的成为前台
                            if win32gui.GetForegroundWindow() == hwnd:
                                self.steps.append("进一步置前成功（已获得焦点）")
                                return True
                    except Exception as _:
                        pass
                    try:
                        if self.simple_activate(hwnd):
                            if win32gui.GetForegroundWindow() == hwnd:
                                self.steps.append("简单方法置前成功（已获得焦点）")
                                return True
                    except Exception as _:
                        pass
                    try:
                        if self.activate_by_alt_tab(hwnd):
                            if win32gui.GetForegroundWindow() == hwnd:
                                self.steps.append("Alt+Tab 辅助置前成功（已获得焦点）")
                                return True
                    except Exception as _:
                        pass
                    self.steps.append("仍未获得焦点，交由上层继续后备方法")
                    return False
                    
            except Exception as e:
                self.steps.append(f"ctypes 激活失败: {e}")
            
            # 6. 备用方法：BringWindowToTop
            try:
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.05)
                # 验证是否成为前台
                if win32gui.GetForegroundWindow() == hwnd:
                    self.steps.append("使用 BringWindowToTop 激活（已获得焦点）")
                    return True
                else:
                    self.steps.append("BringWindowToTop 执行，但未获得焦点")
            except Exception as e:
                self.steps.append(f"BringWindowToTop 失败: {e}")
            
            return False
            
        except Exception as exc:
            self.steps.append(f"托盘应用激活失败: {exc}")
            return False

    def activate_by_alt_tab(self, hwnd: int) -> bool:
        """通过模拟 Alt+Tab 激活窗口（终极备用方案）。"""
        try:
            self.steps.append("尝试通过键盘模拟激活")
            
            # 先确保窗口可见
            if not win32gui.IsWindowVisible(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            
            # 模拟 Alt 键按下
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            time.sleep(0.05)
            
            # 尝试直接激活
            try:
                win32gui.SetForegroundWindow(hwnd)
                # 验证是否激活成功
                if win32gui.GetForegroundWindow() == hwnd:
                    self.steps.append("Alt 键辅助激活成功（已获得焦点）")
                    return True
                else:
                    self.steps.append("Alt 键辅助执行，但未获得焦点")
            finally:
                # 释放 Alt 键
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            
        except Exception as exc:
            self.steps.append(f"键盘模拟激活失败: {exc}")
            return False

    def simple_activate(self, hwnd: int) -> bool:
        """使用最简单的方法激活窗口（备用方案）。"""
        try:
            self.steps.append("尝试简单激活方法")
            
            # 方法1：先确保窗口可见
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            
            # 方法2：使用 ctypes 直接调用，绕过某些限制
            try:
                import ctypes
                # 允许设置前台窗口（需要管理员权限或特殊条件）
                ctypes.windll.user32.AllowSetForegroundWindow(-1)  # ASFW_ANY
                time.sleep(0.05)
            except Exception:
                pass
            
            # 方法3：使用 SetForegroundWindow
            try:
                win32gui.SetForegroundWindow(hwnd)
                # 验证是否成功
                if win32gui.GetForegroundWindow() == hwnd:
                    self.steps.append("SetForegroundWindow 成功（已获得焦点）")
                    return True
                else:
                    self.steps.append("SetForegroundWindow 执行，但未获得焦点")
            except Exception as e1:
                self.steps.append(f"SetForegroundWindow 失败: {e1}")
            
            # 方法4：使用 BringWindowToTop
            try:
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.1)
                # 再次尝试 SetForegroundWindow
                win32gui.SetForegroundWindow(hwnd)
                if win32gui.GetForegroundWindow() == hwnd:
                    self.steps.append("BringWindowToTop + SetForegroundWindow 成功（已获得焦点）")
                    return True
                self.steps.append("BringWindowToTop 执行，但未获得焦点")
            except Exception as e2:
                self.steps.append(f"BringWindowToTop 失败: {e2}")
            
            # 方法5：使用 SwitchToThisWindow（最激进的方法）
            try:
                win32gui.SwitchToThisWindow(hwnd, True)
                if win32gui.GetForegroundWindow() == hwnd:
                    self.steps.append("SwitchToThisWindow 成功（已获得焦点）")
                    return True
                else:
                    self.steps.append("SwitchToThisWindow 执行，但未获得焦点")
            except Exception as e3:
                self.steps.append(f"SwitchToThisWindow 失败: {e3}")
            
            return False
        except Exception as exc:
            self.steps.append(f"简单激活失败: {exc}")
            return False

    def bring_window_to_front(self, hwnd: int) -> bool:
        """将窗口置前，处理最小化、隐藏等各种状态。"""
        attached = False
        fg_thread = target_thread = 0
        
        try:
            # 获取窗口信息用于调试
            title = win32gui.GetWindowText(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_iconic = win32gui.IsIconic(hwnd)
            self.steps.append(f"窗口状态: 标题='{title}', 可见={is_visible}, 最小化={is_iconic}")
            
            # 1. 处理最小化窗口
            if is_iconic:
                self.steps.append("窗口已最小化，正在恢复")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.15)
            
            # 2. 处理隐藏窗口（托盘应用）
            if not is_visible:
                self.steps.append("窗口不可见（托盘应用），尝试显示")
                # 先尝试恢复窗口
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.1)
                    # 再显示窗口
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    time.sleep(0.1)
                    # 确保窗口正常显示
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
                    time.sleep(0.15)
                except Exception as _:
                    pass

            # 3. 线程输入附加（绕过 Windows 激活限制）
            fg_hwnd = win32gui.GetForegroundWindow()
            if fg_hwnd:
                fg_thread = win32process.GetWindowThreadProcessId(fg_hwnd)[0]
            target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]

            if fg_thread and fg_thread != target_thread:
                self.steps.append(f"附加线程输入: fg={fg_thread}, target={target_thread}")
                try:
                    # 注意：AttachThreadInput 在 win32process 模块，不是 win32api
                    import ctypes
                    ctypes.windll.user32.AttachThreadInput(fg_thread, target_thread, True)
                    attached = True
                except Exception as e:
                    self.steps.append(f"线程附加失败: {e}")

            # 4. 多重置顶操作
            flags = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
            
            # 先设为最顶层
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)
            time.sleep(0.05)
            
            # 设为前台窗口
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            
            # 尝试设置焦点（可能失败，但不影响整体）
            try:
                win32gui.SetFocus(hwnd)
            except Exception:
                pass
            
            # 取消永久置顶
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, flags)
            
            # 最终校验是否真的成为前台
            fg_hwnd = win32gui.GetForegroundWindow()
            if fg_hwnd == hwnd:
                self.steps.append("窗口置前操作完成（已获得焦点）")
                return True
            else:
                self.steps.append("窗口已显示但未获得焦点")
                return False
            
        except Exception as exc:
            error_msg = f"置顶窗口失败 (hwnd={hwnd}): {type(exc).__name__}: {exc}"
            LOGGER.warning(error_msg)
            self.steps.append(error_msg)
            return False
        finally:
            if attached:
                try:
                    import ctypes
                    ctypes.windll.user32.AttachThreadInput(fg_thread, target_thread, False)
                except Exception:
                    pass

    @staticmethod
    def activate_with_pywinauto(process_name: str, app_name: str) -> bool:
        if not HAS_PYWINAUTO:
            return False
        try:
            app = Application().connect(path=process_name)
            windows = app.windows()
            if windows:
                windows[0].set_focus()
                LOGGER.info("通过 pywinauto 激活 %s", app_name)
                return True
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("pywinauto 激活失败: %s", exc)
        return False

    @staticmethod
    def wait_for_window(process_name: str, timeout: float = 1.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            hwnd = WindowsTrayActivator.find_window_by_process(process_name)
            if hwnd:
                return True
            time.sleep(0.1)
        return False

    @staticmethod
    def shell_start(app_path: str) -> bool:
        """
        安全启动应用，避免进程状态冲突。
        使用 DETACHED_PROCESS 确保进程独立运行。
        """
        try:
            LOGGER.info(f"安全启动应用: {app_path}")
            
            # 对于快捷方式和可执行文件，os.startfile() 最安全
            if os.path.splitext(app_path)[1].lower() in ['.lnk', '.exe']:
                os.startfile(app_path)  # type: ignore[attr-defined]
                return True
            
            # 其他情况使用 DETACHED_PROCESS
            subprocess.Popen(
                [app_path],
                shell=False,  # 更安全
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                start_new_session=True  # Python 3.7+
            )
            return True
        except Exception as exc:
            LOGGER.warning(f"安全启动失败: {exc}")
            return False

    @staticmethod
    def launch_process(app_path: str) -> bool:
        """启动应用进程"""
        try:
            # 检查文件是否存在
            if not os.path.exists(app_path):
                LOGGER.error(f"应用路径不存在: {app_path}")
                return False
            
            LOGGER.info(f"正在启动应用: {app_path}")
            
            if os.path.splitext(app_path)[1].lower() == ".lnk":
                # 快捷方式，使用 os.startfile
                LOGGER.info("使用 os.startfile 启动快捷方式")
                os.startfile(app_path)  # type: ignore[attr-defined]
            else:
                # 可执行文件，使用 subprocess
                LOGGER.info("使用 subprocess.Popen 启动可执行文件")
                subprocess.Popen([app_path], shell=False)
            
            LOGGER.info("启动命令已执行")
            return True
        except Exception as exc:
            LOGGER.error(f"启动应用失败: {type(exc).__name__}: {exc}")
            return False

    @staticmethod
    def shell_start(app_path: str) -> bool:
        """通过 start 命令拉起 Windows Shell（等效于 TS 版本）。"""
        try:
            # 与 TS 实现保持一致：start "" "<path>"，使用 shell=True 交给 cmd 处理
            escaped_path = app_path.replace("\"", "\\\"")
            command = f'start "" "{escaped_path}"'
            subprocess.Popen(command, shell=True)  # type: ignore[arg-type]
            return True
        except Exception as exc:  # pragma: no cover
            LOGGER.error(f"Shell start 失败: {type(exc).__name__}: {exc}")
            return False

    def _result(self, success: bool, message: str) -> Dict[str, Any]:
        # 记录详细日志用于调试
        LOGGER.info(f"激活结果: {message}")
        LOGGER.debug(f"操作步骤:\n" + "\n".join(f"  {i+1}. {step}" for i, step in enumerate(self.steps)))
        
        return {
            "success": success,
            "message": message,
            "steps": list(self.steps),
        }


def open_app(app: AppInfo) -> Dict[str, Any]:
    """根据平台打开应用。"""

    if SYSTEM == "windows":
        activator = WindowsTrayActivator()
        return activator.activate(app)

    if SYSTEM == "darwin":
        subprocess.run(["open", app.path], check=True)
        return {"success": True, "message": f"已通过 open 启动 {app.name}", "steps": []}

    subprocess.Popen([app.path], shell=False)
    return {"success": True, "message": f"已执行 {app.path}", "steps": []}
