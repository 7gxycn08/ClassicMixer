import os
import subprocess
import pygetwindow as gw
import pyautogui
import threading
import time
from pynput import mouse, keyboard
import sys
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSettings


COMBO_LEFT = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.left}
COMBO_RIGHT = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.right}
combo_left_triggered = False
combo_right_triggered = False
window_name = "volume mixer"
movable = None
flag = True
current_keys = set()
x_min,y_min = None,None
x_max,y_max = None,None
initial_flag = None
shortcut_thread = None
shortcut_thread_running = True
cycle_script = rf"{os.getcwd()}\bin\CycleAudio.ps1"
current_device_txt = rf"{os.getcwd()}\bin\Current_Device.txt"


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


    def is_ctrl(key):
        return key in {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}


    def is_alt(key):
        return key in {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r}


    def combo_left_pressed():
        return (any(is_ctrl(k) for k in current_keys)
                and any(is_alt(k) for k in current_keys)
                and keyboard.Key.left in current_keys)


    def combo_right_pressed():
        return (any(is_ctrl(k) for k in current_keys)
                and any(is_alt(k) for k in current_keys)
                and keyboard.Key.right in current_keys)


    def on_press(key):
        global current_keys, combo_left_triggered, combo_right_triggered
        current_keys.add(key)

        # Check for CTRL + ALT + LEFT ARROW
        if combo_left_pressed() and not combo_left_triggered:
            combo_left_triggered = True
            cycle_audio_left()

        # Check for CTRL + ALT + RIGHT ARROW
        if combo_right_pressed() and not combo_right_triggered:
            combo_right_triggered = True
            cycle_audio_right()


    def on_release(key):
        global current_keys, combo_left_triggered, combo_right_triggered
        current_keys.discard(key)
        if keyboard.Key.left == key:
            combo_left_triggered = False
        if keyboard.Key.right == key:
            combo_right_triggered = False


    def shortcuts_listener():
        global shortcut_thread_running
        # Start listening
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        while shortcut_thread_running:
            time.sleep(0.1)

        listener.stop()
        listener.join()


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
        global initial_flag, shortcut_thread_running, shortcut_thread
        app_settings.setValue("Enable_Shortcuts", checked)
        try:
            if checked:
                if shortcut_thread is None or not shortcut_thread.is_alive():
                    shortcut_thread = threading.Thread(target=shortcuts_listener, daemon=True)
                    shortcut_thread.start()
                    shortcut_thread_running = True
            if not checked:
                shortcut_thread_running = False
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