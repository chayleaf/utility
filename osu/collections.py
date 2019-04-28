from .utility import BinaryFile

class Collection:
	def __init__(self, colldb):
		self.name = colldb.readOsuString()
		bmCount = colldb.readInt()
		self.hashes = []
		for i in range(bmCount):
			self.hashes.append(colldb.readOsuString())

	def __repr__(self):
		return f'Collection(name={repr(self.name)}, {len(self.hashes)} hashes)'

class CollectionDb(BinaryFile):
	def __init__(self, filename=None):
		self.timestamp = 0
		self.collections = []

		if filename is None:
			super().__init__()
		else:
			super().__init__(filename, 'r')
			self.load(filename)

	def load(self, filename):
		self.timestamp = self.readInt()
		cnt = self.readInt()
		self.collections = []
		for i in range(cnt):
			self.collections.append(Collection(self))