import os, re, sys
import cacheClass as cc
from PySide.QtCore import *
from PySide.QtGui import *

class MainWidget(QWidget):
	def __init__(self, cacheDrive = 'Q:', parent = None, projRegex = '^\d{6}\w+'):
		super(MainWidget, self).__init__(parent)
		self.__cacheDrive = cacheDrive
		self.cutItem = None

		self.initUI(projRegex = projRegex)

	def initUI(self, projRegex):
		self.__projRegex = re.compile(projRegex)

		self.setWindowTitle('VFX Pipeline Tool')
		self.resize(860,540)

		self.view_widget = ViewWidget(item = self.cutItem)

		top_hlayout = QHBoxLayout()
		main_vlayout = QVBoxLayout()

		self.projects_cb = QComboBox()
		self.cuts_cb = QComboBox()

		self.cache_textEdit = QTextEdit()
		self.ver_textEdit = QTextEdit()

		cache_comment_widget = QWidget()
		self.cache_comment_bn_s = QPushButton('Save Cache Comment')
		self.cache_comment_bn_r = QPushButton('Read Cache Comment')
		cache_comment_widget_layout = QVBoxLayout()
		cache_comment_widget_hlayout = QHBoxLayout()
		cache_comment_widget_layout.addWidget(QLabel('Cache Comment:'))
		cache_comment_widget_layout.addWidget(self.cache_textEdit)
		cache_comment_widget_hlayout.addWidget(self.cache_comment_bn_r)
		cache_comment_widget_hlayout.addWidget(self.cache_comment_bn_s)
		cache_comment_widget_layout.addLayout(cache_comment_widget_hlayout)
		cache_comment_widget.setLayout(cache_comment_widget_layout)

		ver_comment_widget = QWidget()
		self.ver_comment_bn_s = QPushButton('Save Version Comment')
		self.ver_comment_bn_r = QPushButton('Read Version Comment')
		ver_comment_widget_layout = QVBoxLayout()
		ver_comment_widget_hlayout = QHBoxLayout()
		ver_comment_widget_layout.addWidget(QLabel('Version Comment:'))
		ver_comment_widget_layout.addWidget(self.ver_textEdit)
		ver_comment_widget_hlayout.addWidget(self.ver_comment_bn_r)
		ver_comment_widget_hlayout.addWidget(self.ver_comment_bn_s)
		ver_comment_widget_layout.addLayout(ver_comment_widget_hlayout)
		ver_comment_widget.setLayout(ver_comment_widget_layout)

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

		self.splitter = QSplitter()
		self.splitter.setOrientation(Qt.Vertical)

		label = QLabel('Project:')
		label.setFixedWidth(40)
		top_hlayout.addWidget(label)
		top_hlayout.addWidget(self.projects_cb)
		label = QLabel('Cut:')
		label.setFixedWidth(30)
		top_hlayout.addWidget(label)
		top_hlayout.addWidget(self.cuts_cb)
		main_vlayout.addLayout(top_hlayout)

		self.splitter.addWidget(self.view_widget)
		self.splitter.addWidget(cache_comment_widget)
		self.splitter.addWidget(ver_comment_widget)

		main_vlayout.addWidget(self.splitter)

		self.setLayout(main_vlayout)

		self.projects_cb.currentIndexChanged.connect(self.pick_project)
		self.cuts_cb.currentIndexChanged.connect(self.pick_cut)

	def pick_project(self):
		self.projectItem  = cc.ProjectCahce(project = self.projects_cb.currentText())		
		self.refresh_cuts_cb()
		self.view_widget.cutChange(self.cutItem)

	def pick_cut(self):
		cut = self.cuts_cb.currentText()
		if cut != '':
			cuts = [x for x in self.projectItem.children() if x.name() == cut ]
			self.cutItem = cuts[0]
			self.view_widget.cutChange(self.cutItem)
		else:
			self.cutItem = None

	def refresh_cuts_cb(self):
		self.cuts_cb.clear()
		cuts = []
		for cut in cc.collect(self.projectItem, 'CUT'):
			cuts += [cut.name()]
		self.cuts_cb.addItems(cuts)





class ViewWidget(QTableWidget):
	def __init__(self, item, parent = None):
		super(ViewWidget, self).__init__(parent)
		self.cutItem = item
		self.USER_F = 'User'
		self.CACHE_NAME_F = 'Cache Name'
		self.VERSION_F = 'ver.'
		self.TYPE_F = 'Type'
		self.START_F = 'Start'
		self.END_F = 'End'
		self.header = [self.USER_F, self.CACHE_NAME_F, self.VERSION_F, self.TYPE_F, self.START_F, self.END_F]
		self.cacheItems = []
		self.initUI()

	def initUI(self):		
		self.setColumnCount(len(self.header))
		self.setHorizontalHeaderLabels(self.header)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.SingleSelection)

		self.mapper = QSignalMapper(self)
		self.mapper.mapped[int].connect(self.verChange)
		if self.cutItem != None:
			self.cutChange(self.cutItem)
				

	def cutChange(self, cutItem):
		self.clear()
		self.setRowCount(0)
		self.cacheItems = []
		self.setColumnCount(len(self.header))
		self.setHorizontalHeaderLabels(self.header)
		self.cutItem = cutItem
		if self.cutItem != None:
			self.setRowCount(len(self.cutItem.children()))
			self.ver_cb = []
			for i,j in enumerate(self.cutItem.children()):
				self.cacheItems.append(j)

				self.setItem(i, 1, QTableWidgetItem(j.cacheName()))
				cb = QComboBox()
				for ver in j.children():
					cb.addItem(ver.name())
				cb.setCurrentIndex(cb.count()-1)
				self.setCellWidget(i, self.header.index("ver."), cb)
				
				cb.currentIndexChanged.connect(self.mapper.map)
				self.mapper.setMapping(cb, i)
				
				version = j.findVersion(cb.currentText())
				self.setRow(i, version)
			self.resizeRowsToContents()
			self.resizeColumnsToContents()

	def verChange(self,row):
		cb = self.cellWidget(row, self.header.index(self.VERSION_F))
		version = self.cacheItems[row].findVersion(cb.currentText())
		self.setRow(row, version)

	def setRow(self, row, version):
		self.setItem(row, self.header.index(self.USER_F), QTableWidgetItem(version.user()))
		default_background = self.item(row, self.header.index(self.USER_F)).background()				
		self.setItem(row, self.header.index(self.TYPE_F), QTableWidgetItem(version.fileType()))
		if version.seqFlag() == 'SEQ':
			self.setItem(row, self.header.index(self.START_F), QTableWidgetItem(str(version.startFrame())))
			self.setItem(row, self.header.index(self.END_F), QTableWidgetItem(str(version.endFrame())))
		else:
			self.setItem(row, self.header.index(self.START_F), QTableWidgetItem('X'))
			self.setItem(row, self.header.index(self.END_F), QTableWidgetItem('X'))

		for i in range(self.columnCount()):
			if i != self.header.index(self.VERSION_F):
				if not version.check():
					self.item(row, i).setBackground(QColor(Qt.magenta))
				else:
					self.item(row, i).setBackground(default_background)


if __name__ == '__main__':
	cacheDrive = 'C:/temp'
	app = QApplication(sys.argv)
	mainWindow = MainWidget(cacheDrive = cacheDrive)

	mainWindow.show()

	sys.exit(app.exec_())