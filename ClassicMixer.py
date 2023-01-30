import subprocess
import sys
import os
import win32gui
import win32con
import time
import configparser
from threading import Thread
from PyQt5.QtWidgets import QMenu, QSystemTrayIcon,QApplication
from PyQt5.QtGui import QIcon
from pathlib import Path
from pynput import mouse

config = configparser.ConfigParser()
config.read('Config.ini')
screen_width = int(config['MainConfig']['screen_width'])
screen_height = int(config['MainConfig']['screen_height'])
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

    def write_to_config(xpos,ypos):
        config['MainConfig']['xpos'] = str(xpos)
        config['MainConfig']['ypos'] = str(ypos)
        with open('Config.ini', 'w') as configfile:
            config.write(configfile)

    def onDoubleClick(reason):
        global flag
        if reason == QSystemTrayIcon.DoubleClick:
            process = Thread(target=lambda: subprocess.Popen('sndvol.exe', creationflags=0x08000000), daemon=True)
            process.start()
            time.sleep(0.12)
            hwnd = win32gui.GetForegroundWindow()
            win32gui.SetForegroundWindow(hwnd)
            w, h = win32gui.GetWindowRect(hwnd)[2:]
            xpos = screen_width - w
            ypos = screen_height - h
            win32gui.SetWindowPos(hwnd, None, xpos, ypos, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
            Thread(target=write_to_config,args=(xpos,ypos),daemon=True).start()
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
