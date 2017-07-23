import os, re, sys, subprocess
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
		self.resize(860,720)

		self.view_widget = ViewWidget(item = self.cutItem, parent = self)

		top_hlayout = QHBoxLayout()
		main_vlayout = QVBoxLayout()

		self.projects_cb = QComboBox()
		self.cuts_cb = QComboBox()

		projects = []
		path = os.path.join(self.__cacheDrive + '\\')
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

		self.cache_comment_widget = CommentWidget(label = 'Cache')
		self.ver_comment_widget = CommentWidget(label = 'Version')

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
		self.splitter.addWidget(self.cache_comment_widget)
		self.splitter.addWidget(self.ver_comment_widget)

		main_vlayout.addWidget(self.splitter)

		self.setLayout(main_vlayout)

		self.projects_cb.currentIndexChanged.connect(self.pick_project)
		self.cuts_cb.currentIndexChanged.connect(self.pick_cut)

		self.connect(self.view_widget, SIGNAL("itemClicked (QTableWidgetItem*)"), self.selectCache) 

	def pick_project(self):
		self.projectItem  = cc.ProjectCahce(cacheDrive = self.__cacheDrive, project = self.projects_cb.currentText())
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

	def selectCache(self, item):
		row = item.row()
		cacheItem = self.view_widget.getCacheItem(row)
		versionItem = self.view_widget.getVersionItem(row)
		self.cache_comment_widget.listWidget.refresh(cacheItem)
		self.ver_comment_widget.listWidget.refresh(versionItem)

############

class ViewWidget(QTableWidget):
	def __init__(self, item, parent = None):
		super(ViewWidget, self).__init__(parent)
		self.__parent = parent
		self.cutItem = item
		self.USER_F = 'User'
		self.CACHE_NAME_F = 'Cache Name'
		self.VERSION_F = 'ver.'
		self.TYPE_F = 'Type'
		self.START_F = 'Start'
		self.END_F = 'End'
		self.PREVIEW_B_F = 'Open Preview'
		self.SEQ_CB_F = 'Sequence'
		self.POST_SCALE_F = 'Post Scale'
		self.header = [self.USER_F, self.CACHE_NAME_F, self.VERSION_F, self.TYPE_F, self.SEQ_CB_F, self.START_F, self.END_F, self.POST_SCALE_F, self.PREVIEW_B_F]
		self.cacheItems = []

		self.mapper = QSignalMapper(self)
		self.mapper.mapped[int].connect(self.verChange)

		self.preview_mapper = QSignalMapper(self)
		self.preview_mapper.mapped[int].connect(self.openPreview)
		self.initUI()

	def initUI(self):		
		self.setColumnCount(len(self.header))
		self.setHorizontalHeaderLabels(self.header)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.SingleSelection)
		
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
				self.rowSetting(i, version)
			self.resizeRowsToContents()
			self.resizeColumnsToContents()

	def openPreview(self, row):
		version = self.getCacheItem(row).findVersion(self.cellWidget(row,self.header.index(self.VERSION_F)).currentText())
		subprocess.call("explorer " + version.previewPath(), shell=True)		

	def verChange(self,row):
		cb = self.cellWidget(row, self.header.index(self.VERSION_F))
		version = self.getCacheItem(row).findVersion(cb.currentText())
		self.rowSetting(row, version)
		self.selectRow(row)
		self.__parent.cache_comment_widget.listWidget.refresh(self.getCacheItem(row))
		self.__parent.ver_comment_widget.listWidget.refresh(self.getVersionItem(row))

	def rowSetting(self, row, version):
		self.setItem(row, self.header.index(self.USER_F), QTableWidgetItem(version.user()))
		#default_background = self.item(row, self.header.index(self.USER_F)).background()	
		self.setItem(row, self.header.index(self.TYPE_F), QTableWidgetItem(version.fileType()))
		if version.seqFlag() == 'SEQ':
			self.setItem(row, self.header.index(self.START_F), QTableWidgetItem(str(version.startFrame())))
			self.setItem(row, self.header.index(self.END_F), QTableWidgetItem(str(version.endFrame())))
		else:
			self.setItem(row, self.header.index(self.START_F), QTableWidgetItem(' '))
			self.setItem(row, self.header.index(self.END_F), QTableWidgetItem(' '))
		preview_bn = QPushButton('Open Folder')
		self.setCellWidget(row, self.header.index(self.PREVIEW_B_F), preview_bn)
		preview_bn.clicked.connect(self.preview_mapper.map)
		self.preview_mapper.setMapping(preview_bn, row)

		self.setItem(row, self.header.index(self.SEQ_CB_F), QTableWidgetItem('V' if version.seqFlag() == 'SEQ' else 'X'))
		self.setItem(row, self.header.index(self.POST_SCALE_F), QTableWidgetItem(str(version.getScale())))

		'''
		for i in range(self.columnCount()):
			if i != self.header.index(self.VERSION_F):
				if not version.check():
					self.item(row, i).setBackground(QColor(Qt.magenta))
				else:
					self.item(row, i).setBackground(default_background)
		'''

	def getCacheItems(self):
		return self.cacheItems

	def getCacheItem(self, row):
		return self.cacheItems[row]

	def getVersionItem(self, row):
		return self.cacheItem(row).children()

	def getVersionItem(self, row):
		ver = self.cellWidget(row, self.header.index(self.VERSION_F)).currentText()
		return self.getCacheItem(row).findVersion(ver)


#################

class CommentWidget(QWidget):
	def __init__(self, label, parent = None):
		super(CommentWidget, self).__init__(parent)
		self.label = label
		self.initUI()

	def initUI(self):
		self.comment_send_bn = QPushButton('Send')
		self.comment_read_bn = QPushButton('Read ' + self.label + ' Comment')
		main_layout = QVBoxLayout()
		send_hlayout = QHBoxLayout()
		read_hlayout = QHBoxLayout()
		main_layout.addWidget(QLabel(self.label + ' Comment:'))

		self.listWidget = CommentListWidget()
		self.lineEdit = QLineEdit()

		main_layout.addWidget(self.listWidget)
		send_hlayout.addWidget(self.lineEdit)
		send_hlayout.addWidget(self.comment_send_bn)
		read_hlayout.addWidget(self.comment_read_bn)
		
		main_layout.addLayout(send_hlayout)
		main_layout.addLayout(read_hlayout)
		self.setLayout(main_layout)

		self.comment_send_bn.clicked.connect(self.sendComment)

	def sendComment(self):
		self.listWidget.sendComment(self.lineEdit.text())
		self.lineEdit.setText('')

####################

class CommentListWidget(QListWidget):
	def __init__(self, item = None, parent = None):
		super(CommentListWidget, self).__init__(parent)
		self.__item = item
		self.setAlternatingRowColors(True)
		if self.__item != None:
			self.__item = item
			self.initUI()

	def initUI(self):
		self.refresh(self.__item)

	def refresh(self, item):
		self.clear()
		if self.getItem() != item:
			self.__item = item
		pointer = 0
		for comment in self.__item.msg().getComments():
			if comment != None:
				self.addItem(str(comment[0]))
				widgetItem = self.item(pointer)
				widgetItem.setToolTip(' / '.join([comment[1], comment[2]]))
				pointer += 1
		self.scrollToItem(self.item(pointer - 1))

	def sendComment(self, comment):
		self.getItem().msg().sendComment(str(comment))
		self.refresh(self.getItem())

	def getItem(self):
		return self.__item




if __name__ == '__main__':
	cacheDrive = 'C:'
	app = QApplication(sys.argv)
	mainWindow = MainWidget(cacheDrive = cacheDrive)

	mainWindow.show()

	sys.exit(app.exec_())