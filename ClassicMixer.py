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
x_min,y_min = None,None
x_max,y_max = None,None

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

    def on_click(x, y, button, pressed):
        global flag, movable,x_min,x_max,y_min,y_max
        if movable == "True":
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



    app = QApplication(sys.argv)
    classic_tray = QSystemTrayIcon()
    classic_tray.setToolTip("Classic Mixer v2.1")
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
