"""跨平台应用激活逻辑 - 增强版（集成 AutoHotkey 支持）"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .apps import AppInfo

LOGGER = logging.getLogger(__name__)
SYSTEM = platform.system().lower()

PROCESS_ALIASES = {
    "qq": {"qq", "qqprotect", "qqsclaunch", "qqsclauncher", "qqbrowser"},
    "wechat": {"wechat", "weixin", "wechatapp"},
    "tim": {"tim"},
    "dingtalk": {"dingtalk", "钉钉"},
}

# 导入 Windows API
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


class WindowsActivator:
    """Windows 应用激活器 - 支持 Win32 API + AutoHotkey"""

    def __init__(self) -> None:
        self.steps: list[str] = []
        # 检测 AutoHotkey
        self.ahk_path = self._find_autohotkey()
        if self.ahk_path:
            LOGGER.info(f"检测到 AutoHotkey: {self.ahk_path}")
        else:
            LOGGER.info("未检测到 AutoHotkey，将使用纯 Win32 API")

    def _find_autohotkey(self) -> Optional[str]:
        """查找 AutoHotkey 可执行文件"""
        try:
            # 1. 检查系统 PATH
            ahk = shutil.which("autohotkey.exe")
            if ahk:
                return ahk
            
            # 2. 检查常见安装位置
            common_paths = [
                r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
                r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\AutoHotkey\AutoHotkey.exe"),
            ]
            
            for path in common_paths:
                try:
                    if os.path.exists(path):
                        return path
                except:
                    continue
            
            return None
        except Exception as e:
            LOGGER.warning(f"检测 AutoHotkey 时出错: {e}")
            return None

    def activate(self, app: AppInfo) -> Dict[str, Any]:
        """主激活逻辑 - 三层回退策略"""
        self.steps.clear()
        LOGGER.debug(f"========== 开始激活应用: {app.name} ==========")
        LOGGER.debug(f"应用路径: {app.path}")
        LOGGER.debug(f"AutoHotkey 可用: {self.ahk_path is not None}")
        
        if not HAS_WIN32:
            LOGGER.warning("pywin32 未安装")
            self.steps.append("pywin32 未安装，回退到直接启动")
            launched = self._launch_process(app.path)
            return self._result(launched, "pywin32 不可用，已直接启动应用")

        # 获取进程名
        process_name = self._get_process_name(app)
        LOGGER.debug(f"进程名: {process_name}")
        
        # 1. 查找窗口
        self.steps.append(f"查找进程: {process_name}")
        LOGGER.debug("开始查找窗口...")
        hwnd = self._find_window_by_process(process_name)
        LOGGER.debug(f"查找结果: hwnd={hwnd}")
        
        if not hwnd:
            self.steps.append("通过进程名未找到窗口，尝试通过标题查找")
            hwnd = self._find_window_by_title(app.name)
            if hwnd:
                self.steps.append(f"通过窗口标题找到窗口 (hwnd={hwnd})")

        # 2. 如果找到窗口，尝试激活
        if hwnd:
            return self._activate_existing_window(app, hwnd, process_name)
        
        # 3. 窗口未找到，启动新实例
        return self._launch_new_instance(app, process_name)

    def _activate_existing_window(
        self, app: AppInfo, hwnd: int, process_name: str
    ) -> Dict[str, Any]:
        """激活已存在的窗口"""
        LOGGER.debug(f"---------- 激活已存在的窗口 ----------")
        self.steps.append(f"检测到 {app.name} 已运行 (hwnd={hwnd})")
        
        # 获取窗口状态（添加异常保护）
        try:
            LOGGER.debug("获取窗口状态...")
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_iconic = win32gui.IsIconic(hwnd)
            title = win32gui.GetWindowText(hwnd)
            LOGGER.debug(f"窗口状态: 标题='{title}', 可见={is_visible}, 最小化={is_iconic}")
            self.steps.append(f"窗口状态: 标题='{title}', 可见={is_visible}, 最小化={is_iconic}")
        except Exception as e:
            LOGGER.error(f"获取窗口状态失败: {e}", exc_info=True)
            self.steps.append(f"获取窗口状态失败: {e}")
            # 假设窗口不可见
            is_visible = False
            is_iconic = False
        
        # 策略 1: 尝试 Win32 API 温和激活
        LOGGER.debug("策略 1: 尝试 Win32 API 温和激活")
        try:
            if self._gentle_activate(hwnd):
                LOGGER.info(f"Win32 API 激活成功: {app.name}")
                return self._result(True, f"成功激活 {app.name}")
            else:
                LOGGER.debug("Win32 API 激活失败")
        except Exception as e:
            LOGGER.error(f"温和激活异常: {e}", exc_info=True)
            self.steps.append(f"温和激活异常: {e}")
        
        # 策略 2: 如果温和激活失败且窗口不可见（可能在托盘），尝试 AutoHotkey
        if not is_visible and self.ahk_path:
            LOGGER.debug("策略 2: 尝试 AutoHotkey 激活")
            self.steps.append("窗口在托盘中，尝试使用 AutoHotkey 恢复")
            try:
                result = self._activate_with_autohotkey(app, process_name)
                if result['success']:
                    LOGGER.info(f"AutoHotkey 激活成功: {app.name}")
                    return result
                else:
                    LOGGER.debug(f"AutoHotkey 激活失败: {result.get('message')}")
                self.steps.extend(result.get('steps', []))
            except Exception as e:
                LOGGER.error(f"AutoHotkey 激活异常: {e}", exc_info=True)
                self.steps.append(f"AutoHotkey 激活异常: {e}")
        
        # 策略 3: 兜底 - 使用 Shell Start
        LOGGER.debug("策略 3: 尝试 Shell Start")
        self.steps.append("尝试使用 Shell start 命令唤起")
        try:
            if self._shell_start(app.path):
                self.steps.append("Shell start 命令执行成功，等待窗口响应")
                
                # 等待窗口变为可见
                for i in range(15):  # 3 秒
                    time.sleep(0.2)
                    try:
                        new_hwnd = self._find_window_by_process(process_name)
                        if new_hwnd:
                            try:
                                if win32gui.IsWindowVisible(new_hwnd):
                                    self.steps.append(f"窗口已变为可见 (hwnd={new_hwnd})")
                                    self._gentle_activate(new_hwnd)
                                    return self._result(True, f"通过 Shell start 成功唤起 {app.name}")
                            except:
                                # 窗口句柄可能失效
                                continue
                    except Exception as e:
                        self.steps.append(f"检查窗口时出错: {e}")
                        break
                
                return self._result(
                    True, 
                    f"已尝试唤起 {app.name}（应用可能在托盘中，请手动点击托盘图标）"
                )
        except Exception as e:
            self.steps.append(f"Shell start 异常: {e}")
        
        # 所有方法都失败
        return self._result(
            True, 
            f"{app.name} 已在运行但在系统托盘中，请手动点击托盘图标恢复窗口"
        )

    def _launch_new_instance(self, app: AppInfo, process_name: str) -> Dict[str, Any]:
        """启动新应用实例"""
        self.steps.append(f"未检测到 {app.name} 进程，准备启动")
        self.steps.append(f"启动路径: {app.path}")
        
        launched = self._launch_process(app.path)
        if not launched:
            self.steps.append("launch_process 返回失败")
            return self._result(False, "无法启动应用")
        
        self.steps.append("launch_process 返回成功，等待窗口出现")
        
        # 等待新进程的窗口出现
        if self._wait_for_window(process_name, timeout=5.0):
            self.steps.append("检测到新窗口")
            hwnd = self._find_window_by_process(process_name)
            if hwnd:
                self.steps.append(f"找到新窗口 hwnd={hwnd}，尝试置前")
                self._gentle_activate(hwnd)
            return self._result(True, f"已启动 {app.name}")
        else:
            self.steps.append("等待超时，未检测到窗口（应用可能正在启动）")
            return self._result(True, f"已启动 {app.name}（窗口未出现）")

    def _activate_with_autohotkey(
        self, app: AppInfo, process_name: str
    ) -> Dict[str, Any]:
        """使用 AutoHotkey 激活托盘应用"""
        if not self.ahk_path:
            return {'success': False, 'steps': ['AutoHotkey 不可用']}
        
        # 生成 AutoHotkey 脚本
        ahk_script = self._generate_ahk_script(app, process_name)
        
        try:
            # 执行 AutoHotkey 脚本
            result = subprocess.run(
                [self.ahk_path, "/ErrorStdOut", "*"],
                input=ahk_script.encode('utf-8'),
                capture_output=True,
                timeout=10,
                text=True
            )
            
            output = result.stdout.strip()
            
            if "SUCCESS" in output:
                return {
                    'success': True,
                    'message': f'通过 AutoHotkey 成功激活 {app.name}',
                    'steps': ['使用 AutoHotkey 脚本激活', output]
                }
            elif "ERROR" in output:
                return {
                    'success': False,
                    'message': f'AutoHotkey 激活失败',
                    'steps': ['AutoHotkey 输出:', output]
                }
            else:
                return {
                    'success': False,
                    'message': 'AutoHotkey 执行无明确结果',
                    'steps': ['AutoHotkey 输出:', output or '无输出']
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'AutoHotkey 执行超时',
                'steps': ['AutoHotkey 脚本执行超过 10 秒']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'AutoHotkey 执行异常: {e}',
                'steps': [str(e)]
            }

    def _generate_ahk_script(self, app: AppInfo, process_name: str) -> str:
        """生成 AutoHotkey 脚本"""
        # 移除 .exe 后缀
        process_base = process_name.replace('.exe', '')
        
        # 转义特殊字符
        app_path_escaped = app.path.replace('"', '""')
        
        return f'''
; AutoHotkey 窗口激活脚本
; 自动生成于 fastmcp-app-launcher

#NoEnv
#SingleInstance Force
SetTitleMatchMode, 2
DetectHiddenWindows, On
SetWinDelay, 10

; 查找窗口
winId := 0

; 方法 1: 通过应用名称查找
WinGet, winId, ID, {app.name}

; 方法 2: 如果没找到，通过进程名查找
if (winId = 0) {{
    WinGet, winId, ID, ahk_exe {process_name}
}}

; 如果找到窗口
if (winId > 0) {{
    ; 检查窗口状态
    WinGet, minMax, MinMax, ahk_id %winId%
    
    ; 如果最小化，恢复
    if (minMax = -1) {{
        WinRestore, ahk_id %winId%
        Sleep, 200
    }}
    
    ; 显示窗口（从托盘恢复）
    WinShow, ahk_id %winId%
    Sleep, 100
    
    ; 激活窗口
    WinActivate, ahk_id %winId%
    Sleep, 100
    
    ; 强制置顶技巧（临时置顶后取消）
    WinSet, AlwaysOnTop, On, ahk_id %winId%
    Sleep, 50
    WinSet, AlwaysOnTop, Off, ahk_id %winId%
    
    ; 再次激活确保获得焦点
    WinActivate, ahk_id %winId%
    Sleep, 100
    
    ; 验证窗口是否可见
    WinGet, isVisible, Visible, ahk_id %winId%
    if (isVisible) {{
        FileAppend, SUCCESS: 已激活窗口 %winId% (%isVisible%), *
    }} else {{
        FileAppend, WARNING: 窗口激活但未可见, *
    }}
}} else {{
    ; 窗口不存在，启动应用
    Run, "{app_path_escaped}"
    
    ; 等待窗口出现（最多 5 秒）
    WinWait, {app.name},, 5
    if (ErrorLevel = 0) {{
        WinActivate, {app.name}
        Sleep, 100
        WinSet, AlwaysOnTop, On, {app.name}
        Sleep, 50
        WinSet, AlwaysOnTop, Off, {app.name}
        FileAppend, SUCCESS: 已启动并激活应用, *
    }} else {{
        FileAppend, ERROR: 启动超时，窗口未出现, *
    }}
}}

ExitApp
'''

    def _get_process_name(self, app: AppInfo) -> str:
        """获取进程名"""
        if app.path.lower().endswith(".lnk"):
            clean_name = app.name.replace(" ", "").replace("-", "")
            process_name = clean_name + ".exe"
            self.steps.append(f"快捷方式推断进程名: {process_name}")
        else:
            process_name = Path(app.path).stem + ".exe"
        return process_name

    def _gentle_activate(self, hwnd: int) -> bool:
        """温和激活窗口（Win32 API）"""
        try:
            self.steps.append("开始温和激活")
            
            # 获取窗口状态（验证句柄有效性）
            try:
                is_visible = win32gui.IsWindowVisible(hwnd)
                is_iconic = win32gui.IsIconic(hwnd)
            except Exception as e:
                self.steps.append(f"窗口句柄无效或已失效: {e}")
                return False
            
            # 1. 恢复最小化窗口
            if is_iconic:
                self.steps.append("窗口已最小化，正在恢复")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)
            elif not is_visible:
                # 窗口不可见且未最小化 = 托盘隐藏
                self.steps.append("窗口在托盘中（不可见且未最小化）")
                
                # 尝试发送 WM_SYSCOMMAND 消息恢复窗口
                self.steps.append("尝试通过 WM_SYSCOMMAND 恢复托盘窗口")
                try:
                    win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
                    time.sleep(0.3)
                    
                    # 再次检查窗口状态
                    if win32gui.IsWindowVisible(hwnd):
                        self.steps.append("WM_SYSCOMMAND 恢复成功")
                        # 继续执行置前逻辑
                    else:
                        self.steps.append("WM_SYSCOMMAND 未生效，需要特殊处理")
                        return False
                except Exception as e:
                    self.steps.append(f"发送 WM_SYSCOMMAND 失败: {e}")
                    return False
            
            # 2. 置前窗口
            return self._bring_to_front(hwnd)
                
        except Exception as exc:
            self.steps.append(f"温和激活失败: {exc}")
            return False

    def _bring_to_front(self, hwnd: int) -> bool:
        """将窗口置前（多种方法组合）"""
        try:
            # 方法1: SetWindowPos 置顶技巧
            try:
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
                time.sleep(0.05)
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_NOTOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
                self.steps.append("使用 SetWindowPos 置顶成功")
            except Exception as e:
                self.steps.append(f"SetWindowPos 失败: {e}")
            
            time.sleep(0.1)
            
            # 方法2: AttachThreadInput 技巧
            try:
                fg_hwnd = win32gui.GetForegroundWindow()
                if fg_hwnd and fg_hwnd != hwnd:
                    fg_thread = win32process.GetWindowThreadProcessId(fg_hwnd)[0]
                    target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
                    
                    if fg_thread != target_thread:
                        import ctypes
                        ctypes.windll.user32.AttachThreadInput(fg_thread, target_thread, True)
                        win32gui.BringWindowToTop(hwnd)
                        win32gui.SetForegroundWindow(hwnd)
                        ctypes.windll.user32.AttachThreadInput(fg_thread, target_thread, False)
                        self.steps.append("使用 AttachThreadInput 获取焦点成功")
                    else:
                        win32gui.BringWindowToTop(hwnd)
                        win32gui.SetForegroundWindow(hwnd)
                        self.steps.append("直接设置焦点成功")
            except Exception as e:
                self.steps.append(f"AttachThreadInput 失败: {e}")
                try:
                    win32gui.BringWindowToTop(hwnd)
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    pass
            
            time.sleep(0.15)
            
            # 验证
            try:
                if win32gui.IsWindowVisible(hwnd):
                    fg_hwnd = win32gui.GetForegroundWindow()
                    if fg_hwnd == hwnd:
                        self.steps.append("窗口激活成功（已获得焦点）")
                    else:
                        self.steps.append("窗口已显示（但未获得焦点）")
                    return True
                else:
                    self.steps.append("窗口仍不可见")
                    return False
            except:
                return True  # 如果验证失败，假设成功
                
        except Exception as e:
            self.steps.append(f"置前失败: {e}")
            return False

    @staticmethod
    def _find_window_by_title(app_name: str):
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
    def _find_window_by_process(process_name: str):
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
    def _wait_for_window(process_name: str, timeout: float = 5.0) -> bool:
        """等待窗口出现"""
        end = time.time() + timeout
        while time.time() < end:
            hwnd = WindowsActivator._find_window_by_process(process_name)
            if hwnd:
                return True
            time.sleep(0.2)
        return False

    @staticmethod
    def _shell_start(app_path: str) -> bool:
        """使用 Shell start 命令启动应用"""
        try:
            command = f'cmd.exe /c start "" "{app_path}"'
            
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True
            )
            
            return True
        except Exception as exc:
            LOGGER.error(f"Shell start 失败: {exc}")
            return False

    @staticmethod
    def _launch_process(app_path: str) -> bool:
        """启动应用进程"""
        try:
            if not os.path.exists(app_path):
                LOGGER.error(f"应用路径不存在: {app_path}")
                return False
            
            # 使用 os.startfile（Windows 推荐方式）
            if os.path.splitext(app_path)[1].lower() in ['.lnk', '.exe']:
                os.startfile(app_path)  # type: ignore[attr-defined]
                return True
            
            # 其他情况使用 subprocess
            subprocess.Popen(
                [app_path],
                shell=False,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                start_new_session=True
            )
            return True
        except Exception as exc:
            LOGGER.error(f"启动应用失败: {exc}")
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
        activator = WindowsActivator()
        return activator.activate(app)

    if SYSTEM == "darwin":
        subprocess.run(["open", app.path], check=True)
        return {"success": True, "message": f"已通过 open 启动 {app.name}", "steps": []}

    subprocess.Popen([app.path], shell=False)
    return {"success": True, "message": f"已执行 {app.path}", "steps": []}
