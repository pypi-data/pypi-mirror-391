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

        process_name = Path(app.path).stem + ".exe"

        if app.hotkey and self.send_hotkey(app.hotkey):
            self.steps.append(f"已发送热键 {app.hotkey}")
            if self.wait_for_window(process_name):
                return self._result(True, "通过热键激活窗口成功")

        hwnd = self.find_window_by_process(process_name)
        if hwnd and self.bring_window_to_front(hwnd):
            return self._result(True, "检测到运行中的窗口并置前")

        if self.activate_with_pywinauto(process_name, app.name):
            return self._result(True, "通过 pywinauto 激活窗口")

        launched = self.launch_process(app.path)
        if launched:
            return self._result(True, "未检测到已运行实例，已重新启动应用")

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
    def find_window_by_process(process_name: str):
        hwnds: list[int] = []
        target = process_name.lower()
        aliases = PROCESS_ALIASES.get(target, set())
        candidates = {target, *aliases}

        def callback(hwnd, _):
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

            if any(candidate in exe_name for candidate in candidates):
                hwnds.append(hwnd)
            return True

        win32gui.EnumWindows(callback, None)
        return hwnds[0] if hwnds else None

    @staticmethod
    def bring_window_to_front(hwnd: int) -> bool:
        attached = False
        fg_thread = target_thread = 0
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            fg_hwnd = win32gui.GetForegroundWindow()
            if fg_hwnd:
                fg_thread = win32process.GetWindowThreadProcessId(fg_hwnd)[0]
            target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]

            if fg_thread and fg_thread != target_thread:
                win32api.AttachThreadInput(fg_thread, target_thread, True)
                attached = True

            flags = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetFocus(hwnd)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, flags)
            return True
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("置顶窗口失败: %s", exc)
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
