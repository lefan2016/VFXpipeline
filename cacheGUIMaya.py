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
    elif cache.fileType() == 'abc':
        dialog = AbcConfirm()
        dialog.show()
        if dialog.exec_():
            if dialog.tag == 'maya':
                VFXnode(getVFXnode()).createMayaRef(ver)
            elif dialog.tag == 'vray':
                VFXnode(getVFXnode()).createVrayProxyAbc(ver)
    elif cache.fileType() == 'ma':
        VFXnode(getVFXnode()).createMayaRef(ver, refType = 'mayaAscii')
    elif cache.fileType() == 'mb':
        VFXnode(getVFXnode()).createMayaRef(ver, refType = 'mayaBinary')

    self.rowSettingForMaya(row, self.getVersionItem(row))

def select_cache(self, row):
    vfx = VFXnode(getVFXnode())
    xform_node = vfx.getXformNode(self.getCacheItem(row))
    cmds.select(xform_node, r = True)

def update_cache(self, row):
    cache = self.getCacheItem(row)
    ver = self.getVersionItem(row)
    vfx = VFXnode(getVFXnode())
    if cache.fileType() == 'vdb':
        vfx.updateVrayVolumeGrid(ver)
    elif cache.fileType() == 'abc' and VFXnode(getVFXnode()).getWay(cache) == 'VrayProxy':
        vfx.updateVrayProxyAbc(ver)
    elif cache.fileType() == 'abc' and VFXnode(getVFXnode()).getWay(cache) == 'MayaRef':
        vfx.updateMayaRef(ver)
    elif cache.fileType() == 'ma':
        vfx.updateMayaRef(ver, refType = 'mayaAscii')
    elif cache.fileType() == 'mb':
        vfx.updateMayaRef(ver, refType = 'mayaBinary')

    self.rowSettingForMaya(row, self.getVersionItem(row))

def delete_cache(self, row):
    cache = self.getCacheItem(row)
    vfx = VFXnode(getVFXnode())
    if cmds.referenceQuery(vfx.getShapeNode(cache), inr = True) == False:
        dialog = DelConfirm(cache)
        dialog.show()
        if dialog.exec_():
            if cache.fileType() == 'vdb':
                vfx.deleteVrayVolumeGrid(cache)
            elif cache.fileType() == 'abc' and VFXnode(getVFXnode()).getWay(cache) == 'VrayProxy':
                vfx.deleteVrayProxyAbc(cache)
            elif cache.fileType() == 'abc' and VFXnode(getVFXnode()).getWay(cache) == 'MayaRef':
                vfx.deleteMayaRef(cache)
            elif cache.fileType() in ['ma', 'mb']:
                vfx.deleteMayaRef(cache)

        self.rowSettingForMaya(row, self.getVersionItem(row))
    else:
        dialog = WarningDialog('Can Not Delete Node in Reference File!!')
        dialog.show()
        if dialog.exec_():
            pass


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
        if 'vrayformaya' in cmds.pluginInfo(query=True, listPlugins=True):
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
        else:
            dialog = WarningDialog('No Vray!!')
            dialog.show()
            if dialog.exec_():
                pass


    def updateVrayVolumeGrid(self, ver):
        self.unlock()
        cache = ver.parent()
        if cache.fileType() == 'vdb':
            self.updateAttr(ver)
            self.setScale(ver)
            cmds.setAttr(self.getShapeNode(cache) + '.inFile', ver.path().replace('\\','/') + '/' + self.getFilelink(cache), type = 'string')
        self.lock()

    def deleteVrayVolumeGrid(self, cache):
        self.deleteCache(cache)

    def createVrayProxyAbc(self, ver):
        if 'vrayformaya' in cmds.pluginInfo(query=True, listPlugins=True):
            self.unlock()
            cache = ver.parent()
            name = self.compoundName(cache)
            shape_name = '_'.join([name, 'shape'])
            xform_name = '_'.join([name, 'xform'])
            if cache.fileType() == 'abc':
                path = ver.path().replace('\\','/') + '/' + ver.linkname()
                mel.eval('vrayCreateProxy -node "' + xform_name + '" -dir "'+ path + '" -existing -createProxyNode;')
                shape = cmds.ls(sl = True)[0]
                shape = cmds.rename(shape, shape_name)
                xform = cmds.listRelatives(shape, parent = True)
                xform = cmds.rename(xform, xform_name)
                self.createAttr(cache)
                self.setShapeNode(cache, shape)
                self.setXformNode(cache, xform)
                self.setWay(cache, 'VrayProxy')
                self.updateVrayProxyAbc(ver)
                vraymesh = cmds.listConnections(self.getShapeNode(cache) + '.inMesh')[0]
                cmds.setAttr(vraymesh + '.animType', 1)
                cmds.setAttr(vraymesh + '.useAlembicOffset', 1)
            self.lock()
        else:
            dialog = WarningDialog('No Vray!!')
            dialog.show()
            if dialog.exec_():
                pass

    def updateVrayProxyAbc(self, ver):
        self.unlock()
        self.setVersion(ver)
        self.setFilelink(ver)
        self.setScale(ver)
        vraymesh = cmds.listConnections(self.getShapeNode(ver.parent()) + '.inMesh')[0]
        path = ver.path().replace('\\','/') + '/' + ver.linkname()
        cmds.setAttr(vraymesh + '.fileName2', path, type = 'string' )
        self.lock()

    def deleteVrayProxyAbc(self, cache):
        self.unlock()
        vraymesh = cmds.listConnections(self.getShapeNode(cache) + '.inMesh')[0]
        timeToUnitConversion = cmds.listConnections(vraymesh + '.currentFrame')[0]
        cmds.delete(timeToUnitConversion)
        cmds.delete(vraymesh)
        
        self.deleteCache(cache)
        self.lock()

    def createMayaRef(self, ver, refType = 'Alembic'):
        self.unlock()
        cache = ver.parent()
        name = self.compoundName(cache)
        print name
        shape_name = '_'.join([name, 'shape'])
        xform_name = '_'.join([name, 'xform'])
        if ver.fileType() in ['abc', 'ma', 'mb']:
            path = ver.path().replace('\\','/') + '/' + ver.linkname()
            cmds.file(path, r = True, type = refType, gr = True, gn = xform_name, ignoreVersion = True, mergeNamespacesOnClash = False, namespace = ':')

            shape = cmds.file(path, q = True, rfn = True)
            cmds.lockNode(shape, l = False)
            shape = cmds.rename(shape, shape_name)
            cmds.lockNode(shape)
            self.createAttr(cache)
            self.setShapeNode(cache, shape)
            self.setXformNode(cache, xform_name)
            self.setWay(cache, 'MayaRef')
            self.updateMayaRef(ver, initial = True)
            
        self.lock()

    def updateMayaRef(self, ver, initial = False, refType = 'Alembic'):
        self.unlock()
        cache = ver.parent()
        node = self.getShapeNode(ver.parent())
        path = ver.path().replace('\\','/') + '/' + ver.linkname()
        if initial == False:
            cmds.file(path, type = refType, loadReference = self.getShapeNode(cache))

        xform = self.getXformNode(cache)
        cmds.lockNode(xform, lock = False)
        self.setScale(ver)
        cmds.lockNode(xform)

        self.setVersion(ver)
        self.setFilelink(ver)
        self.lock()

    def deleteMayaRef(self, cache):
        self.unlock()
        ver = cache.findVersion(self.getVersion(cache))
        path = ver.path().replace('\\','/') + '/' + ver.linkname()
        node = self.getShapeNode(cache)
        cmds.lockNode(node, lock = False)
        cmds.file(path, rr = True)
        xform = self.getXformNode(cache)
        cmds.lockNode(xform, lock = False)
        cmds.delete(xform)
        self.deleteCache(cache, cleanNode = False)
        self.lock()

    def updateAttr(self, ver):
        self.setVersion(ver)
        self.setFilelink(ver)

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

    def deleteCache(self, cache, cleanNode = True):
        self.unlock()
        if cleanNode == True:
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

#########

class WarningDialog(QDialog):
    def __init__(self, text, parent = None):
        super(WarningDialog, self).__init__(parent)
        self.initUI(text)
    def initUI(self, text):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(text))
        ok_bn = QPushButton('OK')
        main_layout.addWidget(ok_bn)
        self.setLayout(main_layout)

        ok_bn.clicked.connect(self.bn)

    def bn(self):
        self.close()

##########

class AbcConfirm(QDialog):
    def __init__(self, parent = None):
        super(AbcConfirm, self).__init__(parent)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        bn_layout = QHBoxLayout()

        self.vray = QRadioButton('Vray Proxy')
        self.maya = QRadioButton('Maya Ref')

        ok_bn = QPushButton('OK')
        cancel_bn = QPushButton('Cancel')

        bn_layout.addWidget(ok_bn)
        bn_layout.addWidget(cancel_bn)

        main_layout.addWidget(self.vray)
        main_layout.addWidget(self.maya)
        main_layout.addLayout(bn_layout)

        self.setLayout(main_layout)

        cancel_bn.clicked.connect(self.cancel)
        ok_bn.clicked.connect(self.ok)

    def ok(self):
        if self.vray.isChecked():
            self.tag = 'vray'
        elif self.maya.isChecked():
            self.tag = 'maya'
        else:
            self.tag = None
        self.accept()
        self.cloed()

    def cancel(self):
        self.close()

########

class DelConfirm(QDialog):
    def __init__(self, cache, parent = None):
        super(DelConfirm, self).__init__(parent)
        self.initUI(cache)

    def initUI(self, cache):
        main_layout = QVBoxLayout()
        bn_layout = QHBoxLayout()

        ok_bn = QPushButton('OK')
        cancel_bn = QPushButton('Cancel')

        bn_layout.addWidget(ok_bn)
        bn_layout.addWidget(cancel_bn)
        main_layout.addWidget(QLabel('Delete: ' + cache.name() + '?' ))
        main_layout.addLayout(bn_layout)

        self.setLayout(main_layout)

        ok_bn.clicked.connect(lambda: self.final(1))
        cancel_bn.clicked.connect(lambda: self.final(0))

    def final(self, check):
        if check == 1:
            self.accept()
        self.close()


#######

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

