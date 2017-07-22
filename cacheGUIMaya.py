import cacheGUI
from maya import OpenMayaUI as omui
from shiboken import wrapInstance
from PySide.QtGui import *

def view():
    cacheDrive = 'C:'
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    mainWidget = cacheGUI.MainWidget(cacheDrive = cacheDrive)
    mainWidget.show()