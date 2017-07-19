import os
import re

class ProjectCahce(object):
	def __init__(self, project, cacheDrive = 'Q:'):
		self.__cut_regex = re.compile('^\C')
		project_regex = re.compile('^\d{6}\w+')
		self.__cacheDrive = cacheDrive
		self.__project = ''
		self.__cuts = []
		if project_regex.match(project):
			path = os.path.join(cacheDrive, project)
			if os.path.exists(path) and os.path.isdir(path):
				self.__cacheDrive = cacheDrive
				self.__project = project
				self.read()

	def exists(self):
		path = os.path.join(self.__cacheDrive, self.__project)
		if os.path.exists(path) and os.path.isdir(path) and self.__project != '':
			return True
		else:
			return False

	def read(self):
		dirs = []
		self.__cuts = []
		path = os.path.join(self.__cacheDrive, self.__project)
		for ele in os.listdir(path):
			if self.__cut_regex.match(ele):
				dirs.extend([ele])
		if len(dirs) > 0:
			for d in dirs:
				self.__cuts.append(CutCache(cut = d, parent = self))

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

	def flag(self):
		return 'PROJECT'


class CutCache(object):
	def __init__(self, cut, parent):
		self.__cacheFilter = [['abc', 'obj'],['vdb','prt']]
		self.__parent = parent
		self.__cut = cut
		self.read()

	def read(self):
		self.__caches = []
		for cacheType in os.listdir(self.path()):
			if os.path.isdir(os.path.join(self.path(), cacheType)):
				for name in os.listdir(self.path() + '\\' + cacheType):
					if os.path.isdir(os.path.join(self.path(), cacheType, name)):
						for i,j in enumerate(self.__cacheFilter):
							if cacheType in self.__cacheFilter[i]:
								self.__caches.append(Cache(fileType = cacheType, name = name, parent = self, seq_flag = i))

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

	def flag(self):
		return 'CUT'


class Cache(object):
	def __init__(self, fileType, name, parent, seq_flag):
		self.__version_regex = re.compile('^\w\d+')
		self.__parent = parent
		self.__fileType = fileType
		self.__name = name
		self.__seq_flag = seq_flag
		self.read()

	def parent(self):
		return self.__parent

	def path(self):
		return os.path.join(self.parent().path(), self.fileType(), self.name())

	def name(self):
		return self.__name

	def fileType(self):
		return self.__fileType

	def read(self):
		self.__versions = []
		for dirs in os.listdir(self.path()):
			if os.path.isdir(os.path.join(self.path(), dirs)) and self.__version_regex.match(dirs):
				self.__versions.append(Version(version = dirs, parent = self, seq_flag = self.__seq_flag))

	def versions(self):
		return self.__versions

	def children(self):
		return self.__versions

	def flag(self):
		return 'CACHE'


class Version(object):
	def __init__(self, version, parent, seq_flag):
		self.__parent = parent
		self.__version = version
		self.__seq_flag = seq_flag
		self.__filename = ''
		self.__user = ''
		self.__startFrame = 0
		self.__endFrame = 0
		self.__padding = 0
		self.__check = True
		self.findFile()

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

			if '_'.join(filename.split('.')[0].split('_')[1:-1]) != self.parent().name():
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

	def startFrame(self):
		return self.__startFrame

	def endFrame(self):
		return self.__endFrame

	def padding(self):
		return self.__padding

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


	def check(self):
		return self.__check

	def seqFlag(self):
		if self.__seq_flag == 1:
			return 'SEQ'
		else:
			return None

	def flag(self):
		return 'VERSION'


def collect(item, flag):
	returnItem = []

	if item.flag() == flag:
		returnItem.append(item)

	if item.children() != None:
		for child in item.children():
			if child.flag() == flag:
				returnItem.append(child)
			returnItem += list(set(collect(child, flag)))
	return returnItem



if __name__ == '__main__':

	a = ProjectCahce(project = '201706_FuriousWings')
	print a.exists()
	print a.name()
	print a.cuts()[0].path()

	col = collect(a, 'VERSION')
	for c in col:
		print c.filenames()
		if c.seqFlag() == 'SEQ':
			print c.startFrame(),c.endFrame(),c.padding()



	