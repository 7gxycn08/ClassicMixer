import os
import sys
import time
import ctypes
import win32api
import win32gui
import win32con
import subprocess
import win32process
import configparser
from ctypes import wintypes
from pynput import mouse
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSettings, Signal, QObject, QThread
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QApplication, QMessageBox


window_name = "volume mixer"
movable = None
flag = True
x_min,y_min = None,None
x_max,y_max = None,None
initial_flag = None
shortcut_thread = QThread()
shortcut_thread_running = True
cycle_script = rf"{os.getcwd()}\bin\CycleAudio.ps1"
current_device_txt = rf"{os.getcwd()}\bin\Current_Device.txt"
user_32 = ctypes.WinDLL("user32.dll")
hotkeys = {}
last_trigger = {}
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = win32con.SW_MINIMIZE
config = configparser.ConfigParser()
config.read("custom_size.ini")
KERNEL_32 = ctypes.WinDLL("kernel32.dll")
custom_width = int(config["WindowSize"]["width"])
if custom_width > 1500:
    custom_width = 1500

VK = {
    "CTRL": 0x11,
    "ALT": 0x12,
    "LEFT": 0x25,
    "RIGHT": 0x27,
    "UP": 0x26,
    "DOWN": 0x28,
    "INSERT": 0x2D,
}

class ProcessCheckEntry32(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', ctypes.c_long),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', wintypes.CHAR * 260),
    ]

def tray_icon():
    global movable, shortcut_thread

    def notify_audio_changed(device):
        classic_tray.showMessage(
            "",
            f"Output Device changed to: {device}",
            QSystemTrayIcon.MessageIcon.Information,
            1000  # duration in ms
        )

    def run_audio_cycling(cmd):
        subprocess.call(
            cmd,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    def cycle_audio_left():
        cmd = [
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",  # Allow running script
            "-File", cycle_script,
            "-Direction",
            "Prev"
        ]
        run_audio_cycling(cmd)

        with open(current_device_txt, "r") as file:
            device = file.read()

        notify_audio_changed(device)

    def cycle_audio_right():
        cmd = [
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",  # Allow running script
            "-File", cycle_script,
            "-Direction",
            "Next"
        ]

        run_audio_cycling(cmd)

        with open(current_device_txt, "r") as file:
            device = file.read()

        notify_audio_changed(device)

    def install_module():
        install_script = rf"{os.getcwd()}\bin\install.ps1"

        # Run the script
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", install_script],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    def is_module_installed(module_name):
        """
        Check if a PowerShell module is installed.
        Returns True if installed, False otherwise.
        """
        try:
            # Run PowerShell command to get the module
            result = subprocess.run(
                ["powershell", "-Command", f"Get-Module -ListAvailable -Name {module_name}"],
                capture_output=True,
                text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return bool(result.stdout.strip())  # If output is not empty, module exists
        except Exception as e:
            signals.error_signal.emit(f"Error installing module: {e}")
            return False


    def volume_control(hex_key_code):
        user_32.keybd_event(hex_key_code, 0, 0x1, 0)
        user_32.keybd_event(hex_key_code, 0, 0x2, 0)
        time.sleep(0.1)


    def mute():
        cmd = [
            "powershell.exe",
            "-command",
            "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
        ]
        run_audio_cycling(cmd)

    def register_hotkey(keys, callback):
        global hotkeys, last_trigger
        """Register a hotkey combo like ('CTRL','SHIFT','F12')"""
        combo = frozenset(VK[k] for k in keys)
        hotkeys[combo] = callback
        last_trigger[combo] = 0  # initialize last trigger time

    def shortcuts_listener(poll_interval=0.1, repeat_delay=0.1):
        global shortcut_thread_running
        register_hotkey(("CTRL", "ALT", "LEFT"), signals.cycle_left_signal.emit)
        register_hotkey(("CTRL", "ALT", "RIGHT"), signals.cycle_right_signal.emit)
        register_hotkey(("CTRL", "ALT", "UP"), signals.volume_up_signal.emit)
        register_hotkey(("CTRL", "ALT", "DOWN"), signals.volume_down_signal.emit)
        register_hotkey(("CTRL", "ALT", "INSERT"), signals.mute_signal.emit)

        while shortcut_thread_running:
            for combo, cb in hotkeys.items():
                if all(user_32.GetAsyncKeyState(vk) & 0x8000 for vk in combo):
                    now = time.time()
                    if now - last_trigger[combo] > repeat_delay:
                        last_trigger[combo] = now
                        cb()
            time.sleep(poll_interval)

    def close_tray_icon():
        global shortcut_thread_running
        shortcut_thread_running = False
        shortcut_thread.wait()
        classic_tray.hide()
        app.exit()
        sys.exit()

    def on_double_click(reason):
        global flag
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            launch_and_move_window()
            flag = True

    def on_click(x, y, _, pressed):
        global flag, movable,x_min,x_max,y_min,y_max
        if movable:
            flag = False
            return

        else:
            if pressed:
                x_min, x_max = min(x_min, x_max), max(x_min, x_max) # noqa
                y_min, y_max = min(y_min, y_max), max(y_min, y_max) # noqa
                if not (x_min <= x <= x_max and y_min <= y <= y_max):
                    subprocess.call('taskkill /im sndvol.exe /F', creationflags=0x08000000)  # noqa
                    flag = False


    def start_mouse_listener():
        global flag
        flag = True
        with mouse.Listener(on_click=on_click):
            while flag:
                time.sleep(1)
                continue

    def find_hwnd_by_pid(pid, timeout=5):
        hwnd_list = []

        def callback(hwnd, _):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                hwnd_list.append(hwnd)
            return True

        # Wait until window exists or timeout
        start = time.time()
        while time.time() - start < timeout:
            # noinspection PyBroadException
            try:
                hwnd_list.clear()
                hwnd_list.clear()
                win32gui.EnumWindows(callback, None)
                if hwnd_list:
                    break
            except Exception:
                time.sleep(0.1)
        return hwnd_list

    def move_window_bottom_right(hwnd, mon_info, process):
        """
        Moves the window with the given title to the bottom-right corner of its monitor.
        """
        if not hwnd:
            return False

        # Get window size
        placement = list(win32gui.GetWindowPlacement(hwnd))
        left, top, right, bottom = placement[4]
        width = right - left
        height = bottom - top

        # Get monitor containing the window
        mon_rect = mon_info['Work']  # Work area excludes taskbar: (left, top, right, bottom)

        # Calculate bottom-right position
        new_x = mon_rect[2] - width
        new_y = mon_rect[3] - height

        placement[4] = (
            new_x,
            new_y,
            new_x + width,
            new_y + height
        )

        win32gui.SetWindowPlacement(hwnd, tuple(placement))
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        # noinspection SpellCheckingInspection
        if custom_width != 0 and process == "sndvol":
            win32gui.SetWindowPos(
                hwnd,
                None,
                0,
                0,
                custom_width,
                0,
                win32con.SWP_NOMOVE | win32con.SWP_NOZORDER
            )
            # Actual rect after resize
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # Monitor work area
            mon_left, mon_top, mon_right, mon_bottom = mon_info['Work']

            new_x = left
            new_y = top

            # Push window back inside monitor without changing size
            if right > mon_right:
                new_x -= right - mon_right

            if bottom > mon_bottom:
                new_y -= bottom - mon_bottom

            if left < mon_left:
                new_x += mon_left - left

            if top < mon_top:
                new_y += mon_top - top
            # Move ONLY
            if new_x != left or new_y != top:
                win32gui.SetWindowPos(
                    hwnd,
                    None,
                    new_x,
                    new_y,
                    0,
                    0,
                    win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                )
        return True

    def is_process_running(process_name: str) -> bool:
        # Take a snapshot of all processes
        h_snapshot = KERNEL_32.CreateToolhelp32Snapshot(0x00000002, 0)
        if h_snapshot == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())

        entry = ProcessCheckEntry32()
        entry.dwSize = ctypes.sizeof(ProcessCheckEntry32)

        found = False
        if KERNEL_32.Process32First(h_snapshot, ctypes.byref(entry)):
            while True:
                exe_name = entry.szExeFile.decode(errors='ignore')
                if exe_name.lower() == process_name.lower():
                    found = True
                    break
                if not KERNEL_32.Process32Next(h_snapshot, ctypes.byref(entry)):
                    break

        KERNEL_32.CloseHandle(h_snapshot)
        return found

    def launch_and_move_window():
        global x_min, y_min, x_max, y_max
        # noinspection SpellCheckingInspection
        if is_process_running("sndvol.exe"):
            return
        #noinspection SpellCheckingInspection
        proc = subprocess.Popen("sndvol", startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
        hw_nds = find_hwnd_by_pid(proc.pid)
        title = ""
        for hwnd in hw_nds:
            title = win32gui.GetWindowText(hwnd)
        hwnd = win32gui.FindWindow(None, title)
        monitor = win32api.MonitorFromWindow(hwnd)
        mon_info = win32api.GetMonitorInfo(monitor)
        # noinspection SpellCheckingInspection
        moved = move_window_bottom_right(hwnd, mon_info, "sndvol")

        while not moved:
            # noinspection SpellCheckingInspection
            moved = move_window_bottom_right(hwnd, mon_info, "sndvol")
            time.sleep(0.1)

        while True:
            window = list(win32gui.GetWindowPlacement(hwnd))
            left, top, right, bottom = window[4]
            width = right - left
            height = bottom - top
            if window:
                x_min, y_min = left, top
                x_max, y_max = left + width, top + height
                if (x_min == 0 and y_min == 0) or (x_max == 0 and y_max == 0):
                    time.sleep(0.1)
                    continue
                move_thread.start()
                break
            else:
                time.sleep(0.1)


    def about_page():
        subprocess.Popen("start https://github.com/7gxycn08/ClassicMixer",
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def sound_output():
        # noinspection SpellCheckingInspection
        subprocess.Popen(r"C:\Windows\System32\mmsys.cpl",startupinfo=startupinfo,
                         creationflags=subprocess.CREATE_NO_WINDOW, shell=True)

        while True:
            hwnd = user_32.FindWindowW("#32770", "Sound")

            if hwnd and user_32.IsWindowVisible(hwnd):
                user_32.ShowWindow(hwnd, 11) # Force minimize
                break

        monitor = win32api.MonitorFromWindow(hwnd)
        mon_info = win32api.GetMonitorInfo(monitor)
        # noinspection SpellCheckingInspection
        move_window_bottom_right(hwnd, mon_info, "mmsys")

    def shortcut_box_clicked(checked):
        global initial_flag, shortcut_thread_running, shortcut_thread
        app_settings.setValue("Enable_Shortcuts", checked)
        try:
            if checked:
                if shortcut_thread is None or not shortcut_thread.isRunning():
                    shortcut_thread.run = shortcuts_listener
                    shortcut_thread.start()
                    shortcut_thread_running = True
            if not checked:
                shortcut_thread_running = False
                shortcut_thread.wait()
                shortcut_thread = QThread()
        except Exception as e:
            signals.error_signal.emit(f"Error in shortcut_box_clicked: {e}")

    def movable_box_trigger(checked):
        global movable
        app_settings.setValue("Movable_Window", checked)
        if movable_box.isChecked():
            movable = True
        else:
            movable = False

    def on_error_show_msg(message):
        warning_message_box = QMessageBox()
        warning_message_box.setWindowTitle("ClassicMixer Error")
        warning_message_box.setWindowIcon(QIcon(r"Dependency\Resources\sound.ico"))
        warning_message_box.setFixedSize(400, 200)
        warning_message_box.setIcon(QMessageBox.Icon.Critical)
        warning_message_box.setText(message)
        warning_message_box.exec()

    class Signals(QObject):
        cycle_left_signal = Signal()
        cycle_right_signal = Signal()
        volume_up_signal = Signal()
        volume_down_signal = Signal()
        mute_signal = Signal()
        error_signal = Signal(str)

    app = QApplication(sys.argv)
    move_thread = QThread()
    move_thread.run = start_mouse_listener
    app.setStyle("Fusion")
    app_settings = QSettings("7gxycn08@Github", "ClassicMixer")
    classic_tray = QSystemTrayIcon()
    classic_tray.setToolTip("Classic Mixer v2.9")
    classic_tray.setIcon(QIcon(r'Dependency\Resources\sound.ico'))
    module_available = is_module_installed("AudioDeviceCmdlets")
    signals = Signals()
    signals.cycle_left_signal.connect(cycle_audio_left)
    signals.cycle_right_signal.connect(cycle_audio_right)
    signals.volume_up_signal.connect(lambda: volume_control(0xAF))
    signals.volume_down_signal.connect(lambda: volume_control(0xAE))
    signals.error_signal.connect(on_error_show_msg)
    signals.mute_signal.connect(mute)

    if not module_available:
        install_module()

    menu = QMenu()
    menu.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint)

    sound_output_button = QAction(QIcon(r"Dependency\Resources\gear.ico"), 'Sound Output')
    sound_output_button.triggered.connect(sound_output)

    shortcuts_box = QAction("Enable Shortcuts", menu)
    shortcuts_box.setCheckable(True)
    shortcuts_check = bool(app_settings.value("Enable_Shortcuts", defaultValue=False, type=bool))
    shortcuts_box.setChecked(shortcuts_check)
    shortcuts_box.toggled.connect(lambda: shortcut_box_clicked(shortcuts_box.isChecked()))

    movable_box = QAction("Movable Audio Window", menu)
    movable_box.setCheckable(True)
    movable_check = bool(app_settings.value("Movable_Window", defaultValue=False, type=bool))
    movable_box.setChecked(movable_check)
    movable_box.toggled.connect(lambda: movable_box_trigger(movable_box.isChecked()))
    # Set movable value initially to load it's state.
    movable = movable_box.isChecked()

    menu.addSeparator()

    about_button = QAction(QIcon(r"Dependency\Resources\about.ico"), 'About')
    about_button.triggered.connect(about_page)

    action_exit = QAction(QIcon(r"Dependency\Resources\exit.ico"), 'Exit')
    action_exit.triggered.connect(close_tray_icon)

    menu.addActions([sound_output_button, shortcuts_box, movable_box, about_button, action_exit])

    classic_tray.activated.connect(on_double_click)
    classic_tray.setContextMenu(menu)

    # Initial start if checked
    if shortcuts_box.isChecked():
        shortcut_thread.run = shortcuts_listener
        shortcut_thread.start()

    classic_tray.show()
    app.exec()

if __name__ == '__main__':
    tray_icon()