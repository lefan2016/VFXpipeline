# -*- coding: utf-8 -*-
import os, re, sys, subprocess, io
import cacheClass as cc
try:
    from PySide2.QtCore import * 
    from PySide2.QtGui import * 
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *

reload(cc)

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
        path_hlayout = QHBoxLayout()
        self.path_lineEdit = QLineEdit()
        self.path_lineEdit.setReadOnly(True)
        self.open_path_bn = QPushButton('Open Folder')
        path_hlayout.addWidget(self.path_lineEdit)
        path_hlayout.addWidget(self.open_path_bn)

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
        main_vlayout.addLayout(path_hlayout)

        self.setLayout(main_vlayout)

        self.projects_cb.currentIndexChanged.connect(self.pick_project)
        self.cuts_cb.currentIndexChanged.connect(self.pick_cut)
        self.open_path_bn.clicked.connect(self.open_path)

        self.connect(self.view_widget, SIGNAL("itemClicked (QTableWidgetItem*)"), self.selectCache)
        self.maya_init()

    def maya_init(self):
        pass
        
    def pick_project(self):
        self.projectItem  = cc.ProjectCahce(cacheDrive = self.__cacheDrive, project = self.projects_cb.currentText())
        self.refresh_cuts_cb()
        self.view_widget.cutChange(self.cutItem)

    def pick_cut(self):
        cut = self.cuts_cb.currentText()
        if cut != '':
            cuts = [x for x in self.projectItem.children() if x.name() == cut ]
            self.cutItem = cuts[0]
            self.cutItem.read()
            self.view_widget.cutChange(self.cutItem)
        else:
            self.cutItem = None
        self.path_lineEdit.setText('')
        
    def refresh_cuts_cb(self):
        self.cuts_cb.clear()
        cuts = []
        for cut in self.projectItem.children():
            cuts += [cut.name()]
        self.cuts_cb.addItems(cuts)


    def selectCache(self, item):
        row = item.row()
        cacheItem = self.view_widget.getCacheItem(row)
        versionItem = self.view_widget.getVersionItem(row)
        self.path_lineEdit_display(versionItem)
        self.cache_comment_widget.listWidget.refresh(cacheItem)
        self.ver_comment_widget.listWidget.refresh(versionItem)

    def open_path(self):
        row = self.view_widget.currentRow()
        try:
            versionItem = self.view_widget.getVersionItem(row)
            subprocess.call("explorer " + versionItem.path(), shell=True)      
        except:
            pass

    def path_lineEdit_display(self, version):
        if version.check() == False:
            self.path_lineEdit.setText('Error')
        elif version.checkSeq() == True:
            self.path_lineEdit.setText(version.path() + '\\' + version.filename() + '.' + '#'*version.padding() + '.' + version.fileType())
        elif version.checkSeq() == False:
            self.path_lineEdit.setText(version.path() + '\\' + version.filename() + '.' + version.fileType())


############

class ViewWidget(QTableWidget):
    def __init__(self, item, parent = None):
        super(ViewWidget, self).__init__(parent)
        self.__parent = parent
        self.cutItem = item

        self.initHead()

        self.cacheItems = []

        self.mapper = QSignalMapper(self)
        self.mapper.mapped[int].connect(self.verChange)

        self.preview_mapper = QSignalMapper(self)
        self.preview_mapper.mapped[int].connect(self.openPreview)

        self.setScale_mapper = QSignalMapper(self)
        self.setScale_mapper.mapped[int].connect(self.setScale)
        self.initUI()

    def initHead(self):
        self.USER_F = 'User'
        self.CACHE_NAME_F = 'Cache Name'
        self.VERSION_F = 'ver.'
        self.TYPE_F = 'Type'
        self.START_F = 'Start'
        self.END_F = 'End'
        self.PREVIEW_B_F = 'Open Preview'
        self.SEQ_CB_F = 'Sequence'
        self.POST_SCALE_F = 'Post Scale'
        self.SET_SCALE_F = 'Set Scale'
        self.MTIME_F = 'Last Modified'
        self.header = [self.USER_F, self.CACHE_NAME_F, self.VERSION_F, self.TYPE_F, self.SEQ_CB_F, self.START_F, self.END_F, self.MTIME_F, self.POST_SCALE_F, self.SET_SCALE_F, self.PREVIEW_B_F]
        self.initHeadForMaya()

    def initHeadForMaya(self):
        pass

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
        self.__parent.path_lineEdit_display(version)

    def setScale(self, row):
        ver = self.getVersionItem(row)
        dialog = ScaleDialog(ver)
        dialog.show()
        if dialog.exec_():
            ver.setScale([float(dialog.xyz_lineEdit[0].text()), float(dialog.xyz_lineEdit[1].text()), float(dialog.xyz_lineEdit[2].text())])
            self.verChange(row)
        else:
            pass

    def rowSetting(self, row, version):
        if self.USER_F in self.header:
            self.setItem(row, self.header.index(self.USER_F), QTableWidgetItem(version.user()))
        #default_background = self.item(row, self.header.index(self.USER_F)).background()
        if self.TYPE_F in self.header:
            self.setItem(row, self.header.index(self.TYPE_F), QTableWidgetItem(version.fileType()))
        if self.START_F in self.header and self.END_F in self.header:
            if version.seqFlag() == 'SEQ':
                self.setItem(row, self.header.index(self.START_F), QTableWidgetItem(str(version.startFrame())))
                self.setItem(row, self.header.index(self.END_F), QTableWidgetItem(str(version.endFrame())))
            else:
                self.setItem(row, self.header.index(self.START_F), QTableWidgetItem(' '))
                self.setItem(row, self.header.index(self.END_F), QTableWidgetItem(' '))
        if self.PREVIEW_B_F in self.header:
            preview_bn = QPushButton('Open Folder')
            self.setCellWidget(row, self.header.index(self.PREVIEW_B_F), preview_bn)
            preview_bn.clicked.connect(self.preview_mapper.map)
            self.preview_mapper.setMapping(preview_bn, row)

        if self.SEQ_CB_F in self.header:
            if version.check() == True:
                self.setItem(row, self.header.index(self.SEQ_CB_F), QTableWidgetItem('V' if version.seqFlag() == 'SEQ' else 'X'))
            else:
                self.setItem(row, self.header.index(self.SEQ_CB_F), QTableWidgetItem('Error'))

        if self.MTIME_F in self.header:
            mtime = ' ' + version.getmtime(simple = True) + ' '
            self.setItem(row, self.header.index(self.MTIME_F), QTableWidgetItem(mtime))

        if self.POST_SCALE_F in self.header:
            scale = version.getScale()
            if len(set(scale)) == 1:
                scale = scale[0]
            self.setItem(row, self.header.index(self.POST_SCALE_F), QTableWidgetItem(str(scale)))

        if self.SET_SCALE_F in self.header:
            setScale_bn = QPushButton('Set Scale')
            self.setCellWidget(row, self.header.index(self.SET_SCALE_F), setScale_bn)
            setScale_bn.clicked.connect(self.setScale_mapper.map)
            self.setScale_mapper.setMapping(setScale_bn, row)



        '''
        for i in range(self.columnCount()):
            if i != self.header.index(self.VERSION_F):
                if not version.check():
                    self.item(row, i).setBackground(QColor(Qt.magenta))
                else:
                    self.item(row, i).setBackground(default_background)
        '''
        self.rowSettingForMaya(row, version)

    def rowSettingForMaya(self, row, version):
        pass

    def getCacheItems(self):
        return self.cacheItems

    def getCacheItem(self, row):
        return self.cacheItems[row]

    def getVersionItem(self, row):
        return self.cacheItem(row).children()

    def getVersionItem(self, row):
        ver = self.cellWidget(row, self.header.index(self.VERSION_F)).currentText()
        return self.getCacheItem(row).findVersion(ver)

###########

class ScaleDialog(QDialog):
    def __init__(self, ver, parent = None):
        super(ScaleDialog, self).__init__(parent)
        self.__ver = ver
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        xyz_layout = QHBoxLayout()
        bn_layout = QHBoxLayout()

        self.xyz_lineEdit = []
        for i,j in enumerate(['X:', 'Y:', 'Z:']):
            xyz_layout.addWidget(QLabel(j))
            self.xyz_lineEdit.append(QLineEdit(str(self.__ver.getScale()[i])))
            xyz_layout.addWidget(self.xyz_lineEdit[i])

        self.ok_bn = QPushButton('OK')
        self.cancel_bn = QPushButton('Cancel')
        bn_layout.addWidget(self.ok_bn)
        bn_layout.addWidget(self.cancel_bn)

        main_layout.addLayout(xyz_layout)
        main_layout.addLayout(bn_layout)

        self.setLayout(main_layout)

        self.ok_bn.clicked.connect(lambda: self.submit(1))
        self.cancel_bn.clicked.connect(lambda: self.submit(0))

    def submit(self, check):
        if check == 1:
            self.accept()
        else:
            self.close()


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
                self.addItem(comment[0])
                widgetItem = self.item(pointer)
                widgetItem.setToolTip(' / '.join([comment[1], comment[2]]))
                pointer += 1
        self.scrollToItem(self.item(pointer - 1))

    def sendComment(self, comment):
        self.getItem().msg().sendComment(comment)
        self.refresh(self.getItem())

    def getItem(self):
        return self.__item

def view():
    cacheDrive = 'Q:'
    app = QApplication(sys.argv)
    mainWindow = MainWidget(cacheDrive = cacheDrive)
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    view()