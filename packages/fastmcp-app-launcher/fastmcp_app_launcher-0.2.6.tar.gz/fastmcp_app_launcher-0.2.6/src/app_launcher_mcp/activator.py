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
        hwnd = self.find_window_by_process(process_name)
        
        # 1.1 如果通过进程名找不到，尝试通过应用名称查找窗口标题
        if not hwnd:
            self.steps.append(f"通过进程名 {process_name} 未找到，尝试通过窗口标题查找")
            hwnd = self.find_window_by_title(app.name)
            if hwnd:
                self.steps.append(f"通过窗口标题找到窗口 (hwnd={hwnd})")
        
        if hwnd:
            self.steps.append(f"检测到 {process_name} 进程已运行 (hwnd={hwnd})")
            
            # 1.1 如果有热键，先尝试热键激活
            if app.hotkey and self.send_hotkey(app.hotkey):
                self.steps.append(f"已发送热键 {app.hotkey}")
                time.sleep(0.3)  # 给热键一点时间生效
                if self.bring_window_to_front(hwnd):
                    return self._result(True, "通过热键激活已运行的窗口")
            
            # 1.2 直接尝试置前窗口
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
            
            # 1.5 进程存在但无法激活，返回部分成功（不启动新进程！）
            self.steps.append("所有激活方法均失败，但进程确实在运行")
            return self._result(True, f"{app.name} 已在运行（无法激活窗口，可能需要手动切换）")
        
        # 2. 进程未运行，尝试启动新实例
        self.steps.append(f"未检测到 {process_name} 进程")
        launched = self.launch_process(app.path)
        if launched:
            self.steps.append("已启动新进程")
            # 等待新进程的窗口出现
            if self.wait_for_window(process_name, timeout=3.0):
                hwnd = self.find_window_by_process(process_name)
                if hwnd:
                    self.bring_window_to_front(hwnd)
                return self._result(True, "已启动新应用实例")
            return self._result(True, "已启动应用（未检测到窗口）")

        return self._result(False, "无法激活或启动应用")

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
        visible_hwnds: list[int] = []
        hidden_hwnds: list[int] = []
        target = process_name.lower().replace(".exe", "")
        aliases = PROCESS_ALIASES.get(target, set())
        candidates = {target, *aliases}

        def callback(hwnd, _):
            # 跳过没有标题的窗口（通常是子窗口或工具窗口）
            if not win32gui.GetWindowText(hwnd):
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
                # 区分可见和隐藏窗口
                if win32gui.IsWindowVisible(hwnd):
                    visible_hwnds.append(hwnd)
                else:
                    hidden_hwnds.append(hwnd)
            return True

        win32gui.EnumWindows(callback, None)
        
        # 优先返回可见窗口，如果没有可见窗口则返回隐藏窗口（托盘应用）
        if visible_hwnds:
            return visible_hwnds[0]
        elif hidden_hwnds:
            return hidden_hwnds[0]
        return None

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
                self.steps.append("Alt 键辅助激活成功")
                return True
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
            
            # 方法1：直接显示并激活
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            
            # 方法2：使用 SetForegroundWindow
            try:
                win32gui.SetForegroundWindow(hwnd)
                self.steps.append("SetForegroundWindow 成功")
                return True
            except Exception as e1:
                self.steps.append(f"SetForegroundWindow 失败: {e1}")
            
            # 方法3：使用 BringWindowToTop
            try:
                win32gui.BringWindowToTop(hwnd)
                self.steps.append("BringWindowToTop 成功")
                return True
            except Exception as e2:
                self.steps.append(f"BringWindowToTop 失败: {e2}")
            
            # 方法4：使用 SwitchToThisWindow（最激进的方法）
            try:
                win32gui.SwitchToThisWindow(hwnd, True)
                self.steps.append("SwitchToThisWindow 成功")
                return True
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
                self.steps.append("窗口不可见，正在显示")
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.15)

            # 3. 线程输入附加（绕过 Windows 激活限制）
            fg_hwnd = win32gui.GetForegroundWindow()
            if fg_hwnd:
                fg_thread = win32process.GetWindowThreadProcessId(fg_hwnd)[0]
            target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]

            if fg_thread and fg_thread != target_thread:
                self.steps.append(f"附加线程输入: fg={fg_thread}, target={target_thread}")
                win32api.AttachThreadInput(fg_thread, target_thread, True)
                attached = True

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
            
            self.steps.append("窗口置前操作完成")
            return True
            
        except Exception as exc:
            error_msg = f"置顶窗口失败 (hwnd={hwnd}): {type(exc).__name__}: {exc}"
            LOGGER.warning(error_msg)
            self.steps.append(error_msg)
            return False
        finally:
            if attached:
                try:
                    win32api.AttachThreadInput(fg_thread, target_thread, False)
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
    def launch_process(app_path: str) -> bool:
        try:
            if os.path.splitext(app_path)[1].lower() == ".lnk":
                os.startfile(app_path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen([app_path], shell=False)
            return True
        except Exception as exc:
            LOGGER.warning("启动应用失败: %s", exc)
            return False

    def _result(self, success: bool, message: str) -> Dict[str, Any]:
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
