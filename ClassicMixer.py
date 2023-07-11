import subprocess
import sys
import os
import threading
import time
import configparser
import pyautogui
from PyQt5.QtWidgets import QMenu, QSystemTrayIcon,QApplication
from PyQt5.QtGui import QIcon
from pathlib import Path
from pynput import mouse

config = configparser.ConfigParser()
config.read('Config.ini')
movable = str(config['MainConfig']['moveable'])
flag = True
script_path = Path(__file__).parent.absolute()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

res_path = resource_path(script_path)

def Tray_Icon():
    global process
    def close_tray_icon():
        tray_icon.hide()
        app.exit()
        sys.exit()

    def on_click(x, y, x_min, y_min, x_max, y_max, button, pressed):
        global flag,movable
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
                time.sleep(0.1)
                continue

    def move_window_to_bottom_right(process_name):
        while True:
            try:
                window = pyautogui.getWindowsWithTitle(process_name)
                if window:
                    window = window[0]
                    # do something with the window
                    screen_width, screen_height = pyautogui.size()
                    x_min, y_min = screen_width - window.width, screen_height - window.height
                    x_max, y_max = screen_width, screen_height
                    x_min, y_min = x_min, y_min - 80
                    window.moveTo(x_min, y_min)
                    threading.Thread(target=lambda :start_mouse_listener(x_min, y_min, x_max, y_max),
                                     daemon=True).start()
                    break
                else:
                    raise Exception("Window not Found")
            except:
                pass

    def onDoubleClick(reason):
        global flag
        if reason == QSystemTrayIcon.Trigger:
            process_name = "volume mixer"
            threading.Thread(target=lambda: move_window_to_bottom_right(process_name),daemon=True).start()
            threading.Thread(target=lambda: subprocess.Popen('sndvol.exe'),daemon=True).start()
            flag = True
    app = QApplication(sys.argv)

    tray_icon = QSystemTrayIcon()
    tray_icon.setToolTip("Classic Mixer")
    tray_icon.setIcon(QIcon(f'{res_path}\\Resources\\sound.ico'))

    menu = QMenu()
    menu.addAction("Exit").triggered.connect(lambda: close_tray_icon())
    tray_icon.activated.connect(onDoubleClick)

    tray_icon.setContextMenu(menu)
    tray_icon.show()
    app.exec_()

if __name__ == '__main__':
    Tray_Icon()
