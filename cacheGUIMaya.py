import cacheGUI, sys
from maya import OpenMayaUI as omui
from shiboken import wrapInstance
from PySide.QtGui import *
from PySide.QtCore import *

def maya_initHead(self):
    self.M_INMAYA_F = 'in Maya'
    self.M_UPDATE_F = 'Update'
    self.M_IMPORT_F = 'Import'
    self.M_SELECT_F = 'Select'
    self.header += [self.M_INMAYA_F, self.M_IMPORT_F, self.M_SELECT_F, self.M_UPDATE_F]



def maya_rowSetting(self, row, version):
    if self.M_IMPORT_F in self.header:
        import_bn = QPushButton('Import')
        self.setCellWidget(row, self.header.index(self.M_IMPORT_F), import_bn)
    if self.M_UPDATE_F in self.header:
        update_bn = QPushButton('Update')
        self.setCellWidget(row, self.header.index(self.M_UPDATE_F), update_bn)
    if self.M_SELECT_F in self.header:
        select_bn = QPushButton('Select')
        self.setCellWidget(row, self.header.index(self.M_SELECT_F), select_bn)
    #preview_bn.clicked.connect(self.preview_mapper.map)
    #self.preview_mapper.setMapping(preview_bn, row)

setattr(cacheGUI.ViewWidget, 'rowSettingForMaya', maya_rowSetting)
setattr(cacheGUI.ViewWidget, 'initHeadForMaya', maya_initHead)


def view(cacheDrive = 'Q:'):
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    mainWidget = cacheGUI.MainWidget(cacheDrive = cacheDrive)
    mainWidget.show()

def notMaya_view():
    cacheDrive = 'Q:'
    app = QApplication(sys.argv)
    mainWindow = cacheGUI.MainWidget(cacheDrive = cacheDrive)

    mainWindow.show()

    sys.exit(app.exec_())   

if __name__ == '__main__':
    notMaya_view()