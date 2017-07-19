import os, re, sys
import cacheClass as cc
from PySide.QtCore import *
from PySide.QtGui import *

class MainWidget(QWidget):
	def __init__(self, cacheDrive = 'Q:', parent = None, projRegex = '^\d{6}\w+'):
		super(MainWidget, self).__init__(parent)
		self.__cacheDrive = cacheDrive
		self.initUI(projRegex = projRegex)

	def initUI(self, projRegex):
		project_regex = re.compile(projRegex)

		self.setWindowTitle('VFX Pipeline Tool')
		self.resize(860,540)


		top_hlayout = QHBoxLayout()
		main_vlayout = QVBoxLayout()

		projects = []
		path = os.path.join(self.__cacheDrive)
		for direct in os.listdir(path):
			if os.path.isdir(os.path.join(path, direct)) and project_regex.match(direct):
				projects += [direct]

		self.projects_cb = QComboBox()
		self.cuts_cb = QComboBox()
		self.projects_cb.addItems(projects)

		self.refresh_cuts_cb()

		label = QLabel('Project:')
		label.setFixedWidth(40)
		top_hlayout.addWidget(label)
		top_hlayout.addWidget(self.projects_cb)
		label = QLabel('Cut:')
		label.setFixedWidth(30)
		top_hlayout.addWidget(label)
		top_hlayout.addWidget(self.cuts_cb)
		main_vlayout.addLayout(top_hlayout)

		self.setLayout(main_vlayout)

		self.projects_cb.currentIndexChanged.connect(self.pick_project)

	def pick_project(self):
		self.refresh_cuts_cb()

	def refresh_cuts_cb(self):
		self.projectItem  = cc.ProjectCahce(project = self.projects_cb.currentText())
		self.cuts_cb.clear()
		cuts = []
		for cut in cc.collect(self.projectItem, 'CUT'):
			cuts += [cut.name()]
		self.cuts_cb.addItems(cuts)



if __name__ == '__main__':
	cacheDrive = 'Q:'
	app = QApplication(sys.argv)
	mainWindow = MainWidget()

	mainWindow.show()

	sys.exit(app.exec_())