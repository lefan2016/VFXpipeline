import cacheGUI, sys, Queue, re
from maya import OpenMayaUI as omui
from shiboken import wrapInstance
from PySide.QtGui import *
from PySide.QtCore import *
import maya.cmds as cmds

def maya_initHead(self):
    self.M_INMAYA_F = 'in Maya'
    self.M_UPDATE_F = 'Update'
    self.M_IMPORT_F = 'Import'
    self.M_SELECT_F = 'Select'
    self.M_DELETE_F = 'Delete'
    self.header += [self.M_INMAYA_F, self.M_IMPORT_F, self.M_SELECT_F, self.M_UPDATE_F, self.M_DELETE_F]

    self.import_mapper = QSignalMapper(self)
    self.select_mapper = QSignalMapper(self)
    self.update_mapper = QSignalMapper(self)
    self.delete_mapper = QSignalMapper(self)
    self.import_mapper.mapped[int].connect(self.import_cache)
    self.select_mapper.mapped[int].connect(self.select_cache)
    self.update_mapper.mapped[int].connect(self.update_cache)
    self.delete_mapper.mapped[int].connect(self.delete_cache)


def maya_rowSetting(self, row, version):
    if self.M_IMPORT_F in self.header:
        import_bn = QPushButton('Import')
        self.setCellWidget(row, self.header.index(self.M_IMPORT_F), import_bn)
        import_bn.clicked.connect(self.import_mapper.map)
        self.import_mapper.setMapping(import_bn, row)
    if self.M_UPDATE_F in self.header:
        update_bn = QPushButton('Update')
        self.setCellWidget(row, self.header.index(self.M_UPDATE_F), update_bn)
        update_bn.clicked.connect(self.update_mapper.map)
        self.update_mapper.setMapping(update_bn, row)
    if self.M_SELECT_F in self.header:
        select_bn = QPushButton('Select')
        self.setCellWidget(row, self.header.index(self.M_SELECT_F), select_bn)
        select_bn.clicked.connect(self.select_mapper.map)
        self.select_mapper.setMapping(select_bn, row)
    if self.M_DELETE_F in self.header:
        delete_bn = QPushButton('Delete')
        self.setCellWidget(row, self.header.index(self.M_DELETE_F), delete_bn)
        delete_bn.clicked.connect(self.delete_mapper.map)
        self.delete_mapper.setMapping(delete_bn, row)
    #preview_bn.clicked.connect(self.preview_mapper.map)
    #self.preview_mapper.setMapping(preview_bn, row)

    if self.SET_SCALE_F in self.header:
        self.disableSetScale(row)

def disableSetScale(self, row):
    bn = self.cellWidget(row, self.header.index(self.SET_SCALE_F))
    bn.setEnabled(False)

def import_cache(self, row):
    ver = self.getVersionItem(row)
    cache = self.getCacheItem(row)
    if cache.fileType() == 'vdb':
        VFXnode(getVFXnode()).createVrayVolumeGrid(ver)
    print self.getCacheItem(row).name()

def select_cache(self, row):
    print self.getCacheItem(row).name()

def update_cache(self, row):
    print self.getCacheItem(row).name()

def delete_cache(self, row):
    print self.getCacheItem(row).name()

setattr(cacheGUI.ViewWidget, 'rowSettingForMaya', maya_rowSetting)
setattr(cacheGUI.ViewWidget, 'initHeadForMaya', maya_initHead)

setattr(cacheGUI.ViewWidget, 'import_cache', import_cache)
setattr(cacheGUI.ViewWidget, 'update_cache', update_cache)
setattr(cacheGUI.ViewWidget, 'select_cache', select_cache)
setattr(cacheGUI.ViewWidget, 'delete_cache', delete_cache)

setattr(cacheGUI.ViewWidget, 'disableSetScale', disableSetScale)


##########

class VFXnode(object):
    def __init__(self, node):
        self.__node = node

    def createVrayVolumeGrid(self, ver):
        cache = ver.parent()
        name = '_'.join(['vfx', cache.parent().name(), cache.name().replace('\\','_')])
        shape_name = '_'.join([name, 'shape'])
        xform_name = '_'.join([name, 'xform'])
        if cache.fileType() == 'vdb':
            shape = cmds.createNode('VRayVolumeGrid', n= shape_name)
            xform = cmds.listRelatives(shape, parent = True)
            xform = cmds.rename(xform, xform_name)
            cmds.addAttr(self.__node, longName = name, attributeType = 'compound', numberOfChildren = 4)
            cmds.addAttr(self.__node, longName = shape_name, attributeType = 'message', parent = name)            
            cmds.addAttr(self.__node, longName = xform_name, attributeType = 'message', parent = name)            
            cmds.addAttr(self.__node, longName = name + '_ver', dataType = 'string', parent = name)
            cmds.addAttr(self.__node, longName = name + '_filelink', dataType = 'string', parent = name)
            cmds.connectAttr(shape + '.message', self.__node + '.' + shape_name)
            cmds.connectAttr(xform + '.message', self.__node + '.' + xform_name)
            cmds.setAttr(self.__node + '.' + name + '_ver', ver.name(), type = 'string')
            cmds.setAttr(self.__node + '.' + name + '_filelink', ver.linkname(), type = 'string')

            cmds.setAttr(xform + '.scale', ver.getScale()[0], ver.getScale()[1], ver.getScale()[2])
            cmds.setAttr(shape + '.inFile', ver.path().replace('\\','/') + '/' + ver.linkname(), type = 'string')
            
    def getVfxAttr(self):
        cuts = []
        caches = []
        regex = re.compile('^vfx_')
        for attr in cmds.listAttr(self.__node):
            if regex.match(attr) and cmds.getAttr(self.__node + '.' + attr, type = True) == 'TdataCompound':
                print attr
                cuts.append(attr.split('_')[1])
                caches.append(attr.split('_')[2:])
        print cuts, caches

    def getNamespace(self):
    	return ':'.join(self.__node.split(':')[:-1])


########

def walkNamespace(que, root = ':', target = 'VFX'):
    cmds.namespace(set = root)
    nss = cmds.namespaceInfo(lon = True)
    if nss != None:
        for name in nss:
            if name.split(':')[-1] == target:
                que.put(name)
            else:
                walkNamespace(que, root = ':' + name, target = target)
                
def findNamespace(target = 'VFX'):
    result = []
    que = Queue.Queue()
    walkNamespace(que, root = ':', target = target)
    while not que.empty():
        result.append(que.get())
    cmds.namespace(set = ':')
    if result:
        return result
    else:
        return None

def createVFXnode(ns = None):
    if ns == None:
        cmds.namespace(set = ':')
        if 'VFX' not in cmds.namespaceInfo(lon = True):
            cmds.namespace(add = 'VFX')
        cmds.namespace(set = ':VFX')
    else:
        cmds.namespace(set = ':' + ns)
    vfxNode = cmds.createNode('shadingEngine', name = 'VFXpipeline')
    cmds.namespace(set = ':')
    return vfxNode

def findVFXnode():
    if findNamespace(target = 'VFX') == None:
        return None
    else:
        result = []
        for namespace in findNamespace(target = 'VFX'):
            cmds.namespace(set = ':' + namespace)
            if cmds.namespaceInfo(lod = True):
                for node in cmds.namespaceInfo(lod = True):
                    if node.split(':')[-1] == 'VFXpipeline':
                        result += [node]
        cmds.namespace(set = ':')
        return result if len(result) > 0 else None

def getVFXnode():
    if findNamespace() == None:
        return createVFXnode()
    else:
        if findVFXnode() == None:
            return createVFXnode()
        else:
            return findVFXnode()[0] 


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