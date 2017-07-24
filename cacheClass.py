import os, re, time
import threading, Queue
import json

class ProjectCahce(object):
    def __init__(self, project, cacheDrive = 'Q:', projRegex = '^\d{6}\w+', cutRegex = '^\C', mThread = True):
        self.__cut_regex = re.compile(cutRegex)
        project_regex = re.compile(projRegex)
        self.__cacheDrive = cacheDrive
        self.__project = ''
        self.__cuts = []
        self.__mThread = mThread
        if project_regex.match(project):
            path = os.path.join(cacheDrive + '\\', project)
            if os.path.exists(path) and os.path.isdir(path):
                self.__cacheDrive = cacheDrive
                self.__project = project
                self.read()

    def exists(self):
        path = os.path.join(self.__cacheDrive + '\\', self.__project)
        if os.path.exists(path) and os.path.isdir(path) and self.__project != '':
            return True
        else:
            return False

    def read(self):
        self.__cuts = []
        path = os.path.join(self.path())

        if self.__mThread == 1:
            ths = []
            que = Queue.Queue()
            for ele in os.listdir(path):
                if self.__cut_regex.match(ele):
                    th = threading.Thread(target = CutCache, kwargs = {'cut' : ele, 'parent' : self, 'que' : que})
                    #self.__cuts.append(CutCache(cut = ele, parent = self))
                    th.start()
                    ths.append(th)
            
            for th in ths:
                th.join()
            while not que.empty():
                self.__cuts.append(que.get())

        else:
            for ele in os.listdir(path):
                if self.__cut_regex.match(ele):
                    self.__cuts.append(CutCache(cut = ele, parent = self, mThread = 0))
        
        self.__cuts = sorted(self.__cuts, key = lambda x: x.name())

    def name(self):
        return self.__project

    def parent(self):
        return None

    def children(self):
        return self.__cuts

    def cuts(self):
        return self.__cuts

    def path(self):
        return os.path.join(self.__cacheDrive , '\\', self.__project)

    def findCut(self, cut):
        return [x for x in self.children() if x.name() == cut][0]

    def checkFiles(self):
        vers = collect(self, 'VERSION')
        wrong_vers = []
        for ver in vers:
            if not ver.check():
                wrong_vers.append(ver.path().replace('\\','/'))
        return wrong_vers

    def flag(self):
        return 'PROJECT'


class CutCache(object):
    def __init__(self, cut, parent, que = None, mThread = 1):
        self.__cacheFilter = [['abc', 'obj'],['vdb','prt']]
        self.__parent = parent
        self.__cut = cut
        self.__mThread = mThread
        if self.__mThread == 1:
            que.put(self)
        self.read()

    def read(self):
        self.__caches = []


        que = Queue.Queue()
        ths = []
        for cacheType in os.listdir(self.path()):
            if os.path.isdir(os.path.join(self.path(), cacheType)) and (cacheType in self.__cacheFilter[0] or cacheType in self.__cacheFilter[1]):
                for name in os.listdir(self.path() + '\\' + cacheType):
                    if os.path.isdir(os.path.join(self.path(), cacheType, name)):
                        for i,j in enumerate(self.__cacheFilter):
                            if cacheType in self.__cacheFilter[i]:
                                #self.__caches.append(Cache(fileType = cacheType, name = name, parent = self, seq_flag = i))
                                if self.__mThread == 1:
                                    th = threading.Thread(target = Cache, kwargs = {'fileType' : cacheType, 'name' : name, 'parent' : self, 'seq_flag' : i, 'que' : que})
                                    th.start()
                                    ths.append(th)
                                else:
                                    self.__caches.append(Cache(fileType = cacheType, name = name, parent = self, seq_flag = i, mThread = 0))

        if self.__mThread == 1:
            for th in ths:
                th.join()
            while not que.empty():
                self.__caches.append(que.get())

        self.__caches = sorted(self.__caches, key = lambda x: x.name())

    def name(self):
        return self.__cut

    def project(self):
        return self.__parent

    def parent(self):
        return self.__parent

    def path(self):
        return os.path.join(self.parent().path(), self.name())

    def children(self):
        return self.__caches

    def caches(self):
        return self.__caches

    def path(self):
        return os.path.join(self.parent().path(), self.name())

    def findCache(self, fileType, cacheName):
        return [x for x in self.children() if x.cacheName() == cacheName and x.fileType() == fileType][0]

    def flag(self):
        return 'CUT'



class Cache(object):
    def __init__(self, fileType, name, parent, seq_flag, que = None, verRegex = '^\w\d+', mThread = 1):
        self.__version_regex = re.compile(verRegex)
        self.__mThread = mThread
        self.__parent = parent
        self.__fileType = fileType
        self.__name = name
        self.__seq_flag = seq_flag
        if self.__mThread == 1:
            que.put(self)
        self.read()
        self.__msg = MSG(os.path.join(self.path(), 'msg'))

    def parent(self):
        return self.__parent

    def path(self):
        return os.path.join(self.parent().path(), self.fileType(), self.cacheName())

    def name(self):
        return self.__fileType + '\\' + self.__name

    def cacheName(self):
        return self.__name

    def fileType(self):
        return self.__fileType

    def msg(self):
        return self.__msg

    def eraseMsg(self):
        with open(self.__msgFile, 'w') as file:
            json.dump({'Comments' : [None]}, file)


    def read(self):
        self.__versions = []

        if self.__mThread == 1:
            que = Queue.Queue()
            ths = []
            for dirs in os.listdir(self.path()):
                if os.path.isdir(os.path.join(self.path(), dirs)) and self.__version_regex.match(dirs):
                    #self.__versions.append(Version(version = dirs, parent = self, seq_flag = self.__seq_flag))
                    th = threading.Thread(target = Version, kwargs = {'version' : dirs, 'parent' : self, 'seq_flag' : self.__seq_flag, 'que' : que})
                    th.start()
                    ths.append(th)

            for th in ths:
                th.join()
            while not que.empty():
                self.__versions.append(que.get())
        else:
            for dirs in os.listdir(self.path()):
                if os.path.isdir(os.path.join(self.path(), dirs)) and self.__version_regex.match(dirs):
                    self.__versions.append(Version(version = dirs, parent = self, seq_flag = self.__seq_flag, mThread = 0))

        self.__versions = sorted(self.__versions, key = lambda x: x.name())

    def versions(self):
        return self.__versions

    def children(self):
        return self.__versions

    def flag(self):
        return 'CACHE'

    def findVersion(self, ver):
        return [x for x in self.children() if x.name() == ver][0]


class Version(object):
    def __init__(self, version, parent, seq_flag, que = None, mThread = 1):
        self.__parent = parent
        self.__mThread = mThread
        self.__version = version
        self.__seq_flag = seq_flag
        self.__filename = ''
        self.__user = ''
        self.__startFrame = 0
        self.__endFrame = 0
        self.__padding = 0
        self.__check = True
        if self.__mThread == 1:
            que.put(self)

        self.findFile()
        self.__msg = MSG(os.path.join(self.path(), 'msg'))

        if not os.path.exists(self.previewPath()) or not os.path.isdir(self.previewPath()):
            os.mkdir(self.previewPath())

    def name(self):
        return self.__version

    def parent(self):
        return self.__parent

    def children(self):
        return None

    def path(self):
        return os.path.join(self.parent().path(), self.name())

    def findFile(self):
        filenames = []
        for (dirpath, dirname, files) in os.walk(os.path.join(self.parent().path(), self.name())):
            for file in files:
                if file.endswith('.' + self.parent().fileType()):
                    filenames.append(file)

        filenames = list(set([x.split('.')[0] for x in filenames]))

        if len(filenames) != 1:
            self.__check = False

        for filename in filenames:

            if '_'.join(filename.split('.')[0].split('_')[1:-1]) != self.parent().cacheName():
                self.__check = False

            if filename.split('.')[0].split('_')[-1] != self.name():
                self.__check = False

            self.__filename = filename
            self.__user = self.__filename.split('_')[0]

            if self.__seq_flag == 1:
                self.calibrateFrame()

    def calibrateFrame(self):
        frame_codes = []
        padding = []
        if self.check() == True:
            path = os.path.join(self.parent().path(), self.name())
            for file in os.listdir(path):
                if file.split('.')[0] == self.filename() and file.endswith(self.fileType()):
                    code = file.split('.')[1]
                    frame_codes.append(int(code))
                    padding.append(len(code))
            frame_codes.sort()
            padding = list(set(padding))
            padding.sort()
            min_frame = frame_codes[0]
            max_frame = frame_codes[-1]
            if max_frame - min_frame +1 == len(frame_codes):
                self.__startFrame = min_frame
                self.__endFrame = max_frame
                self.__padding = padding[0]
            else:
                self.__check = False
        else:
            self.__check = False


    def filename(self):
        return self.__filename

    def fileType(self):
        return self.parent().fileType()

    def user(self):
        return self.__user

    def cacheName(self):
        return self.parent().cacheName()

    def startFrame(self):
        return self.__startFrame

    def endFrame(self):
        return self.__endFrame

    def padding(self):
        return self.__padding

    def msg(self):
        return self.__msg

    def filenames(self):
        files = []
        if self.check() == True:
            if self.seqFlag() == None:
                name = self.filename() + '.' + self.fileType()
                files += [name]
            if self.seqFlag() == 'SEQ':
                for i in range(self.startFrame(), self.endFrame()+1):
                    name = '%s.%s.%s' % (self.filename(), str(i).zfill(self.padding()), self.fileType())
                    files += [name]
        return files

    def previewPath(self):
        return os.path.join(self.path(), 'preview')

    def getScale(self):
        return self.msg().getScale()

    def setScale(self, xyz):
        self.msg().setScale(xyz)

    def check(self):
        return self.__check

    def checkSeq(self):
        if self.__seq_flag == 1:
            return True
        else:
            return False

    def seqFlag(self):
        if self.__seq_flag == 1:
            return 'SEQ'
        else:
            return None

    def flag(self):
        return 'VERSION'

class MSG(object):
    def __init__(self, path):
        self.path = None
        if os.path.exists(path) and os.path.isfile(path):
            self.path = path
        else:
            with open(path, 'w') as file:
                json.dump({'Comments' : [None]}, file)

    def eraseAll(self):
        with open(self.path, 'w') as file:
            json.dump({'Comments' : [None]}, file)

    def getContent(self):
        with open(self.path, 'r') as file:
            return json.load(file)

    def getComments(self):
        return self.getContent()['Comments']

    def sendComment(self, comment):
        if type(comment) is str and comment != '':
            content = self.getContent()
            content['Comments'].append([comment, os.environ['COMPUTERNAME'], time.asctime(time.localtime(time.time()))])
            with open(self.path, 'w') as file:
                json.dump(content, file)

    def getPostAdjust(self):
        if 'postAdjust' in self.getContent().keys():
            return self.getContent()['postAdjust']
        else:
            return None

    def getScale(self):
        if self.getPostAdjust() != None:
            if 'scale' in self.getPostAdjust().keys():
                return self.getPostAdjust()['scale']
            else:
                return (1,1,1)

        else:
            return (1,1,1)

    def setScale(self, xyz):
        postAdjust = 'postAdjust'
        if type(xyz) is int or type(xyz) is float:
            xyz = (xyz,xyz,xyz)
        if len(xyz) == 3:
            content = self.getContent()
            if postAdjust not in content.keys():
                content[postAdjust] = {}
                with open(self.path, 'w') as file:
                    json.dump(content, file)
            content = self.getContent()
            content[postAdjust]['scale'] = xyz
            with open(self.path, 'w') as file:
                    json.dump(content, file)







def collect(item, flag):
    returnItem = []

    if item.flag() == flag:
        returnItem.append(item)

    if item.children() != None:
        for child in item.children():
            if child.flag() == flag:
                returnItem.append(child)
            returnItem += list(set(collect(child, flag)))
    return list(set(returnItem))



if __name__ == '__main__':

    a = ProjectCahce(mThread = 1, cacheDrive = 'Q:', project = '201706_FuriousWings')
    print a.exists()
    print a.name()
    print a.path()
    print a.cuts()[0].path()
    print a.cuts()[0].children()[0].path()

    col = collect(a, 'VERSION')


    col = collect(a, 'VERSION')
    for c in col:
        c.msg().eraseAll()
    
    col = collect(a, 'CACHE')
    for c in col:
        c.msg().eraseAll()
    
    