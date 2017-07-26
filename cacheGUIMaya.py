import cacheGUI, sys, Queue, re
from maya import OpenMayaUI as omui
from shiboken import wrapInstance
from PySide.QtGui import *
from PySide.QtCore import *
import maya.cmds as cmds
import maya.mel as mel

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
    if self.M_INMAYA_F in self.header:
        if findVFXnode() != None:
            vfx = VFXnode(getVFXnode())
            if vfx.findCache(version.parent()) != None:
                vfx = VFXnode(getVFXnode())
                self.setItem(row, self.header.index(self.M_INMAYA_F), QTableWidgetItem(vfx.getWay(version.parent())))
            else:
                self.setItem(row, self.header.index(self.M_INMAYA_F), QTableWidgetItem('X'))
        else:
            self.setItem(row, self.header.index(self.M_INMAYA_F), QTableWidgetItem('X'))

    if self.M_IMPORT_F in self.header:
        import_bn = QPushButton('Import')
        self.setCellWidget(row, self.header.index(self.M_IMPORT_F), import_bn)
        import_bn.clicked.connect(self.import_mapper.map)
        self.import_mapper.setMapping(import_bn, row)
        if findVFXnode() != None:
            vfx = VFXnode(getVFXnode())
            if vfx.findCache(version.parent()) != None:
                import_bn.setEnabled(False)

    if self.M_UPDATE_F in self.header:
        update_bn = QPushButton('Update')
        self.setCellWidget(row, self.header.index(self.M_UPDATE_F), update_bn)
        update_bn.clicked.connect(self.update_mapper.map)
        self.update_mapper.setMapping(update_bn, row)
        if findVFXnode() != None:
            vfx = VFXnode(getVFXnode())
            if vfx.findCache(version.parent()) == None:
                update_bn.setEnabled(False)
            elif vfx.getVersion(version.parent()) == version.name():
                update_bn.setEnabled(False)
        else:
            update_bn.setEnabled(False)


    if self.M_SELECT_F in self.header:
        select_bn = QPushButton('Select')
        self.setCellWidget(row, self.header.index(self.M_SELECT_F), select_bn)
        select_bn.clicked.connect(self.select_mapper.map)
        self.select_mapper.setMapping(select_bn, row)
        if findVFXnode() != None:
            vfx = VFXnode(getVFXnode())
            if vfx.findCache(version.parent()) == None:
                select_bn.setEnabled(False)
        else:
            select_bn.setEnabled(False)

    if self.M_DELETE_F in self.header:
        delete_bn = QPushButton('Delete')
        self.setCellWidget(row, self.header.index(self.M_DELETE_F), delete_bn)
        delete_bn.clicked.connect(self.delete_mapper.map)
        self.delete_mapper.setMapping(delete_bn, row)
        if findVFXnode() != None:
            vfx = VFXnode(getVFXnode())
            if vfx.findCache(version.parent()) == None:
                delete_bn.setEnabled(False)
        else:
            delete_bn.setEnabled(False)
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
    self.rowSettingForMaya(row, self.getVersionItem(row))

def select_cache(self, row):
    vfx = VFXnode(getVFXnode())
    shape_node = vfx.getShapeNode(self.getCacheItem(row))
    cmds.select(shape_node, r = True)

def update_cache(self, row):
    vfx = VFXnode(getVFXnode())
    vfx.updateVrayVolumeGrid(self.getVersionItem(row))
    self.rowSettingForMaya(row, self.getVersionItem(row))

def delete_cache(self, row):
    cache = self.getCacheItem(row)
    vfx = VFXnode(getVFXnode())
    vfx.deleteCache(cache)
    self.rowSettingForMaya(row, self.getVersionItem(row))



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
        self.__tags = ['shape', 'xform', 'ver', 'way', 'filelink']
        self.__tagTypes = ['message', 'message', 'string', 'string', 'string']

    def createVrayVolumeGrid(self, ver):
        self.unlock()
        cache = ver.parent()
        name = self.compoundName(cache)
        shape_name = '_'.join([name, 'shape'])
        xform_name = '_'.join([name, 'xform'])
        if cache.fileType() == 'vdb':
            shape = cmds.createNode('VRayVolumeGrid', n = shape_name)
            xform = cmds.listRelatives(shape, parent = True)
            xform = cmds.rename(xform, xform_name)
            self.createAttr(cache)
            self.setShapeNode(cache, shape)
            self.setXformNode(cache, xform)
            self.setWay(cache, 'VolumeGrid')
            self.updateVrayVolumeGrid(ver)
        self.lock()

    def updateVrayVolumeGrid(self, ver):
        self.unlock()
        cache = ver.parent()
        if cache.fileType() == 'vdb':
            self.updateAttr(ver)
            self.setScale(ver)
            cmds.setAttr(self.getShapeNode(cache) + '.inFile', ver.path().replace('\\','/') + '/' + self.getFilelink(cache), type = 'string')
        self.lock()

    def deleteVrayVolumeGrid(self, cache):
        self.unlock()
        self.deleteCache(cache)
        self.lock()

    def createVrayProxyAbc(self, ver):
        self.unlock()
        cache = ver.parent()
        name = self.compoundName(cache)
        shape_name = '_'.join([name, 'shape'])
        xform_name = '_'.join([name, 'xform'])
        if cache.fileType() == 'abc':
            path = ver.path().replace('\\','/') + '/' + ver.filename() + '.' + ver.fileType()
            mel.eval('vrayCreateProxy -node "' + xform_name + '" -dir "'+ path + '" -existing -createProxyNode;')
            shape = cmds.ls(sl = True)[0]
            shape = cmds.rename(shape, shape_name)
            xform = cmds.listRelatives(shape, parent = True)
            xform = cmds.rename(xform, xform_name)
            self.createAttr(cache)
            self.setShapeNode(cache, shape)
            self.setXformNode(cache, xform)
            self.setVersion(ver)
            self.setFilelink(ver)
            self.setWay(cache, 'VrayProxy')
            self.setScale(ver)
            cmds.setAttr(self.getShapeNode(cache) + '.inFile', ver.path().replace('\\','/') + '/' + self.getFilelink(cache), type = 'string')
        self.lock()


    def updateAttr(self, ver):
        self.unlock()
        self.setVersion(ver)
        self.setFilelink(ver)
        self.lock()

    def setShapeNode(self, cache, node):
        self.unlock()
        shape_attr = self.getTagAttr(cache, 'shape')
        cmds.connectAttr(node + '.message', shape_attr)
        self.lock()

    def getShapeNode(self, cache):
        shape_attr = self.getTagAttr(cache, 'shape')
        if shape_attr:
            shape = cmds.listConnections(shape_attr, sh = True)[0]
            return shape

    def setXformNode(self, cache, node):
        self.unlock()
        xform_attr = self.getTagAttr(cache, 'xform')
        cmds.connectAttr(node + '.message', xform_attr)
        self.lock()

    def getXformNode(self, cache):
        xform_attr = self.getTagAttr(cache, 'xform')
        if xform_attr:
            xform = cmds.listConnections(xform_attr)[0]
            return xform

    def setScale(self, ver):
        self.unlock()
        cache = ver.parent()
        cmds.setAttr(self.getXformNode(cache) + '.scale', ver.getScale()[0], ver.getScale()[1], ver.getScale()[2])
        self.lock()

    def createAttr(self, cache):
        self.unlock()
        name = self.compoundName(cache)
        cmds.addAttr(self.__node, longName = name, attributeType = 'compound', numberOfChildren = len(self.__tags))
        for i, tag in enumerate(self.__tags):
            if self.__tagTypes[i] == 'message':
                cmds.addAttr(self.__node, longName = '_'.join([name, tag]), attributeType = self.__tagTypes[i], parent = name)
            elif self.__tagTypes[i] == 'string':
                cmds.addAttr(self.__node, longName = '_'.join([name, tag]), dataType = self.__tagTypes[i], parent = name)
        self.lock()


    def getTagAttr(self, cache, tag):
        attr = self.findCache(cache)
        if attr != None and tag in self.__tags:
            return self.__node + '.' + '_'.join([attr, self.__tags[self.__tags.index(tag)]])
        return None

    def getVersion(self, cache):
        attr = self.findCache(cache)
        if attr != None:
            ver_attr = self.getTagAttr(cache, 'ver')
            if ver_attr != None:
                ver = cmds.getAttr(ver_attr)
                return ver
        return None

    def setVersion(self, ver):
        self.unlock()
        cache = ver.parent()
        ver_attr = self.getTagAttr(cache, 'ver')
        if ver_attr:
            cmds.setAttr(ver_attr, ver.name(), type = 'string')
            self.setFilelink(ver)
        self.lock()

    def setFilelink(self, ver):
        self.unlock()
        cache = ver.parent()
        filelink_attr = self.getTagAttr(cache, 'filelink')
        cmds.setAttr(filelink_attr, ver.linkname(), type = 'string')
        self.lock()

    def getFilelink(self, cache):
        filelink_attr = self.getTagAttr(cache, 'filelink')
        return cmds.getAttr(filelink_attr)

    def getWay(self, cache):
        way_attr = self.getTagAttr(cache, 'way')
        return cmds.getAttr(way_attr)

    def setWay(self, cache, way):
        self.unlock()
        if type(way) is str:
            way_attr = self.getTagAttr(cache, 'way')
            cmds.setAttr(way_attr, way, type = 'string')
        self.lock()

    def getVfxAttr(self):
        cuts = []
        caches = []
        regex = re.compile('^vfx_')
        for attr in cmds.listAttr(self.__node):
            if regex.match(attr) and cmds.getAttr(self.__node + '.' + attr, type = True) == 'TdataCompound':
                cuts.append(attr.split('_')[1])
                caches.append('_'.join(attr.split('_')[2:]))
        return cuts, caches

    def findCache(self, cache):
        name = self.compoundName(cache)
        for attr in cmds.listAttr(self.__node):
            if attr == name:
                return attr
        return None

    def deleteCache(self, cache):
        self.unlock()
        cmds.delete(self.getShapeNode(cache))
        cmds.delete(self.getXformNode(cache))
        '''
        for tag in self.__tags:
            attr = self.getTagAttr(cache, tag)
            cmds.deleteAttr(attr)
        '''
        cmds.deleteAttr(self.__node + '.' + self.compoundName(cache))
        self.lock()

    def compoundName(self, cache):
        name = '_'.join(['vfx', cache.parent().name(), cache.name().replace('\\','_')])
        return name

    def getNamespace(self):
    	return ':'.join(self.__node.split(':')[:-1])

    def lock(self):
        cmds.lockNode(self.__node)

    def unlock(self):
        cmds.lockNode(self.__node, lock = False)


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