import subprocess
import sys
import os
import time
import configparser
import pyautogui
from threading import Thread
from PyQt5.QtWidgets import QMenu, QSystemTrayIcon,QApplication
from PyQt5.QtGui import QIcon
from pathlib import Path
from pynput import mouse

config = configparser.ConfigParser()
config.read('Config.ini')
screen_width = int(config['MainConfig']['screen_width'])
screen_height = int(config['MainConfig']['screen_height'])
spawn = float(config['MainConfig']['spawn'])
process = None
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
    global width_of_window,height_of_window,process,screen_width,screen_height
    def close_tray_icon():
        tray_icon.hide()
        app.exit()
        sys.exit()

    def on_click(x, y, button, pressed):
        global flag
        if not pressed:
            return

        # Specify the region of interest (ROI)
        x_min = 2936
        y_min = 1392
        x_max = x_min + 878
        y_max = y_min + 716

        # Check if the click occurred outside the ROI
        if x < x_min or x > x_max or y < y_min or y > y_max:
            subprocess.call('taskkill /im sndvol.exe /F',creationflags=0x08000000)
            flag = False
            return False

    def start_mouse_listener():
        with mouse.Listener(on_click=on_click) as listener:
            while flag:
                listener.join()

    def move_window_to_bottom_right(process_name):
        window = pyautogui.getWindowsWithTitle(process_name)[0]
        screen_width, screen_height = pyautogui.size()
        window.moveTo(screen_width - window.width, screen_height - window.height)

    def onDoubleClick(reason):
        global flag,spawn,screen_width,screen_height
        if reason == QSystemTrayIcon.DoubleClick:
            process = Thread(target=lambda: subprocess.Popen('sndvol.exe', creationflags=0x08000000), daemon=True)
            process.start()
            time.sleep(spawn)
            process_name = "volume mixer"
            move_window_to_bottom_right(process_name)
            flag = True
            start_mouse_listener()

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
