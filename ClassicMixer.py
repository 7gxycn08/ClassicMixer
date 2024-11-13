import ctypes
import subprocess
import pygetwindow as gw
import pyautogui
import threading
import time
from pynput import mouse
import configparser
import sys
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt

# Constants for window position flags
SWP_NOACTIVATE = 0x0010
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040
screen_width, screen_height = pyautogui.size()
window_name = "volume mixer"
config = configparser.ConfigParser()
config.read('Config.ini')
movable = str(config['MainConfig']['moveable'])
flag = True

def tray_icon():
    def close_tray_icon():
        classic_tray.hide()
        app.exit()
        sys.exit()

    def on_double_click(reason):
        global flag
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            threading.Thread(target=lambda: launch_and_move_window("sndvol.exe"),daemon=True).start()
            subprocess.Popen(r"sndvol.exe", creationflags=subprocess.CREATE_NO_WINDOW)
            flag = True

    # Function to set the window position immediately
    def move_window(hwnd, x, y, width, height):
        ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, width, height,
                                          SWP_NOACTIVATE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_NOZORDER)

    # Function to find the window handle (HWND) by process name
    def find_window_by_process():
        windows = gw.getWindowsWithTitle(window_name)
        if windows:
            return windows[0]._hWnd
        return None

    def on_click(x, y, x_min, y_min, x_max, y_max, button, pressed):
        global flag, movable
        if movable == "True":
            flag = False
            return
        else:
            if not pressed:
                return
            # Check if the click occurred outside the ROI

            if x < x_min or x > x_max or y < y_min or y > y_max:
                subprocess.call('taskkill /im sndvol.exe /F', creationflags=0x08000000)
                flag = False
                return

    def start_mouse_listener(x_min, y_min, x_max, y_max):
        global flag
        flag = True
        with mouse.Listener(on_click=lambda x, y, button, pressed: on_click(x, y, x_min, y_min, x_max, y_max, button,
                                                                            pressed)) as listener:
            while flag:
                time.sleep(1)
                continue

    # Function to launch and move the window to the bottom-right corner
    def launch_and_move_window(process_name):
        # Launch the process
        subprocess.Popen([process_name])

        retries = 5000  # Retry until window is found
        hwnd = None
        for _ in range(retries):
            hwnd = find_window_by_process()
            if hwnd:
                break

        if hwnd:
            # Define desired position for the bottom-right corner
            desired_width, desired_height = 1017, 834  # Adjust window size
            x = screen_width - desired_width - 30  # padding from the right edge
            y = screen_height - desired_height - 110  # padding from the bottom edge
            x_max = x + desired_width
            y_max = y + desired_height
            # Move the window immediately to the bottom-right corner
            move_window(hwnd, x, y, desired_width, desired_height)
            threading.Thread(target=lambda: start_mouse_listener(x, y, x_max, y_max),
                             daemon=True).start()
    def about_page():
        subprocess.Popen("start https://github.com/7gxycn08/ClassicMixer",
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

    app = QApplication(sys.argv)
    classic_tray = QSystemTrayIcon()
    classic_tray.setToolTip("Classic Mixer")
    classic_tray.setIcon(QIcon(r'Dependency\Resources\sound.ico'))

    menu = QMenu()
    menu.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint)

    about_button = QAction(QIcon(r"Dependency\Resources\about.ico"), 'About')
    about_button.triggered.connect(about_page)
    action_exit = QAction(QIcon(r"Dependency\Resources\exit.ico"), 'Exit')
    action_exit.triggered.connect(close_tray_icon)
    menu.addActions([about_button, action_exit])

    classic_tray.activated.connect(on_double_click)
    classic_tray.setContextMenu(menu)
    classic_tray.show()
    app.exec()

if __name__ == '__main__':
    tray_icon()
