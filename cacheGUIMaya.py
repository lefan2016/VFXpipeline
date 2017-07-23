import cacheGUI, sys
from maya import OpenMayaUI as omui
from shiboken import wrapInstance
from PySide.QtGui import *
from PySide.QtCore import *

def maya_initHead(self):
	self.M_INMAYA_F = 'in Maya'
	self.M_UPDATE_F = 'Update'
	self.M_IMPORT_F = 'Import'
	self.header += [self.M_INMAYA_F, self.M_IMPORT_F, self.M_UPDATE_F]



def maya_rowSetting(self, row, version):
	import_bn = QPushButton('Import')
	self.setCellWidget(row, self.header.index(self.M_IMPORT_F), import_bn)
	#preview_bn.clicked.connect(self.preview_mapper.map)
	#self.preview_mapper.setMapping(preview_bn, row)

setattr(cacheGUI.ViewWidget, 'rowSettingForMaya', maya_rowSetting)
setattr(cacheGUI.ViewWidget, 'initHeadForMaya', maya_initHead)

#cacheGUI.ViewWidget.initHead = new_initHead
#cacheGUI.ViewWidget.rowSetting = new_rowSetting


def view():
    cacheDrive = 'C:'
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    mainWidget = cacheGUI.MainWidget(cacheDrive = cacheDrive)
    mainWidget.show()

def notMaya_view():
	cacheDrive = 'C:'
	app = QApplication(sys.argv)
	mainWindow = cacheGUI.MainWidget(cacheDrive = cacheDrive)

	mainWindow.show()

	sys.exit(app.exec_())	

if __name__ == '__main__':
	notMaya_view()