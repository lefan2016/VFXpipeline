import os, re, sys
import cacheClass as cc
from PySide.QtCore import *
from PySide.QtGui import *

class MainWidget(QWidget):
	def __init__(self, cacheDrive = 'Q:', parent = None, projRegex = '^\d{6}\w\F'):
		super(MainWidget, self).__init__(parent)
		self.__cacheDrive = cacheDrive
		self.initUI(projRegex = projRegex)

	def initUI(self, projRegex):
		self.__projRegex = re.compile(projRegex)

		self.setWindowTitle('VFX Pipeline Tool')
		self.resize(860,540)

		top_hlayout = QHBoxLayout()
		main_vlayout = QVBoxLayout()

		self.projects_cb = QComboBox()
		self.cuts_cb = QComboBox()

		projects = []
		path = os.path.join(self.__cacheDrive)
		for direct in os.listdir(path):
			if os.path.isdir(os.path.join(path, direct)) and self.__projRegex.match(direct):
				projects += [direct]
		self.projects_cb.addItems(projects)

		self.pick_project()

		self.cuts_cb.clear()
		cuts = []
		for cut in cc.collect(self.projectItem, 'CUT'):
			cuts += [cut.name()]
		self.cuts_cb.addItems(cuts)

		self.pick_cut()

		self.view_widget = ViewWidget(item = self.cutItem)

		label = QLabel('Project:')
		label.setFixedWidth(40)
		top_hlayout.addWidget(label)
		top_hlayout.addWidget(self.projects_cb)
		label = QLabel('Cut:')
		label.setFixedWidth(30)
		top_hlayout.addWidget(label)
		top_hlayout.addWidget(self.cuts_cb)
		main_vlayout.addLayout(top_hlayout)
		main_vlayout.addWidget(self.view_widget)

		self.setLayout(main_vlayout)

		self.projects_cb.currentIndexChanged.connect(self.pick_project)
		self.cuts_cb.currentIndexChanged.connect(self.pick_cut)

	def pick_project(self):
		self.projectItem  = cc.ProjectCahce(project = self.projects_cb.currentText())		
		self.refresh_cuts_cb()

	def pick_cut(self):
		cut = self.cuts_cb.currentText()
		if cut != '':
			cuts = [x for x in self.projectItem.children() if x.name() == cut ]
			self.cutItem = cuts[0]
		else:
			self.cutItem = None

	def refresh_cuts_cb(self):
		self.cuts_cb.clear()
		cuts = []
		for cut in cc.collect(self.projectItem, 'CUT'):
			cuts += [cut.name()]
		self.cuts_cb.addItems(cuts)





class ViewWidget(QListWidget):
	def __init__(self, item, parent = None):
		super(ViewWidget, self).__init__(parent)
		self.cutItem = item
		self.initUI()

	def initUI(self):
		print self.cutItem
		if self.cutItem != None:
			print self.cutItem.name()
			for i,j in enumerate(self.cutItem.children()):
				self.insertItem(i, j.cacheName())


if __name__ == '__main__':
	cacheDrive = 'Q:'
	app = QApplication(sys.argv)
	mainWindow = MainWidget()

	mainWindow.show()

	sys.exit(app.exec_())