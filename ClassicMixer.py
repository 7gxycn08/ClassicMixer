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

window_name = "volume mixer"
config = configparser.ConfigParser()
config.read('Config.ini')
movable = str(config['MainConfig']['moveable'])
flag = True
current_keys = set()

def tray_icon():
    def close_tray_icon():
        classic_tray.hide()
        app.exit()
        sys.exit()

    def on_double_click(reason):
        global flag
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            threading.Thread(target=launch_and_move_window, daemon=True).start()  # noqa
            flag = True

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
                subprocess.call('taskkill /im sndvol.exe /F', creationflags=0x08000000) # noqa
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

    def launch_and_move_window():
        subprocess.Popen("bin/ClassicMixerBin.exe", creationflags=subprocess.CREATE_NO_WINDOW)
        window = gw.getWindowsWithTitle(window_name)
        while True:
            if window:
                win = window[0]
                x, y = win.left, win.top
                x_max, y_max = win.width, win.height
                threading.Thread(target=lambda: start_mouse_listener(x, y, x_max, y_max),
                                 daemon=True).start()
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



    app = QApplication(sys.argv)
    classic_tray = QSystemTrayIcon()
    classic_tray.setToolTip("Classic Mixer v1.9")
    classic_tray.setIcon(QIcon(r'Dependency\Resources\sound.ico'))

    menu = QMenu()
    menu.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint)

    sound_output_button = QAction(QIcon(r"Dependency\Resources\gear.ico"), 'Sound Output')
    sound_output_button.triggered.connect(sound_output)
    about_button = QAction(QIcon(r"Dependency\Resources\about.ico"), 'About')
    about_button.triggered.connect(about_page)
    action_exit = QAction(QIcon(r"Dependency\Resources\exit.ico"), 'Exit')
    action_exit.triggered.connect(close_tray_icon)
    menu.addActions([sound_output_button, about_button, action_exit])

    classic_tray.activated.connect(on_double_click)
    classic_tray.setContextMenu(menu)
    classic_tray.show()
    app.exec()

if __name__ == '__main__':
    tray_icon()
