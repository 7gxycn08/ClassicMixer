import os
import subprocess
import pygetwindow as gw
import pyautogui
import threading
import time
from pynput import mouse
import keyboard
import sys
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSettings
import ctypes

window_name = "volume mixer"
movable = None
flag = True
current_keys = set()
x_min,y_min = None,None
x_max,y_max = None,None
shortcut_thread = None
shortcut_thread_running = True
cycle_script = rf"{os.getcwd()}\bin\CycleAudio.ps1"
current_device_txt = rf"{os.getcwd()}\bin\Current_Device.txt"
user_32 = ctypes.WinDLL("user32.dll")


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
        subprocess.run(
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
            print(f"Error checking module: {e}")
            return False


    def volume_control(hex_key_code):
        user_32.keybd_event(hex_key_code, 0, 0x1, 0)
        user_32.keybd_event(hex_key_code, 0, 0x2, 0)
        time.sleep(0.1)


    def shortcuts_listener():
        global shortcut_thread_running
        # Start listening
        keyboard.add_hotkey('ctrl+alt+left', cycle_audio_left)
        keyboard.add_hotkey('ctrl+alt+right', cycle_audio_right)
        keyboard.add_hotkey('ctrl+alt+up', lambda: volume_control(0xAF))
        keyboard.add_hotkey('ctrl+alt+down', lambda: volume_control(0xAE))
        while shortcut_thread_running:
            time.sleep(0.1)
        keyboard.remove_all_hotkeys()


    def close_tray_icon():
        global shortcut_thread_running
        shortcut_thread_running = False
        classic_tray.hide()
        app.exit()
        sys.exit()


    def on_double_click(reason):
        global flag
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            threading.Thread(target=launch_and_move_window, daemon=True).start()  # noqa
            flag = True


    def on_click(x, y, button, pressed):
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
        with mouse.Listener(on_click=on_click) as listener:
            while flag:
                time.sleep(1)
                continue


    def launch_and_move_window():
        global x_min, y_min, x_max, y_max
        subprocess.Popen("bin/ClassicMixerBin.exe", creationflags=subprocess.CREATE_NO_WINDOW)

        while True:
            window = gw.getWindowsWithTitle(window_name)
            if window:
                win = window[0]
                x_min, y_min = win.left, win.top
                x_max, y_max = win.left + win.width, win.top + win.height
                if (x_min == 0 and y_min == 0) or (x_max == 0 and y_max == 0):
                    time.sleep(0.1)
                    continue
                threading.Thread(target= start_mouse_listener,daemon=True).start()
                break
            else:
                time.sleep(0.1)


    def about_page():
        subprocess.Popen("start https://github.com/7gxycn08/ClassicMixer",
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)


    def sound_output():
        pyautogui.keyDown("win")
        pyautogui.keyDown("ctrl")
        pyautogui.keyDown("v")

        pyautogui.keyUp("win")
        pyautogui.keyUp("ctrl")
        pyautogui.keyUp("v")


    def shortcut_box_clicked(checked):
        global shortcut_thread_running, shortcut_thread
        app_settings.setValue("Enable_Shortcuts", checked)
        try:
            if checked:
                if shortcut_thread is None or not shortcut_thread.is_alive():
                    shortcut_thread_running = True
                    shortcut_thread = threading.Thread(target=shortcuts_listener, daemon=True)
                    shortcut_thread.start()
            if not checked:
                shortcut_thread_running = False
                keyboard.remove_all_hotkeys()
                shortcut_thread.join()
                shortcut_thread = None
        except Exception as e:
            print(e)


    def movable_box_trigger(checked):
        global movable
        app_settings.setValue("Movable_Window", checked)
        if movable_box.isChecked():
            movable = True
        else:
            movable = False

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app_settings = QSettings("7gxycn08@Github", "ClassicMixer")
    classic_tray = QSystemTrayIcon()
    classic_tray.setToolTip("Classic Mixer v2.2")
    classic_tray.setIcon(QIcon(r'Dependency\Resources\sound.ico'))
    module_available = is_module_installed("AudioDeviceCmdlets")

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
        initial_thread = threading.Thread(target=shortcuts_listener, daemon=True)
        shortcut_thread = initial_thread
        shortcut_thread.start()

    classic_tray.show()
    app.exec()

if __name__ == '__main__':
    tray_icon()