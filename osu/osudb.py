from .utility import BinaryFile
from .beatmapmeta import BeatmapMetadata

class OsuDb(BinaryFile):
	def __init__(self, filename=None):
		self.version = 0

		if filename is None:
			super().__init__()
		else:
			self.load(filename)

	def load(self, filename):
		super().__init__(filename, 'r')
		self.version = self.readInt()
		mapsetCnt = self.readInt()
		self.editDate = self.readOsuDate()
		self.unk0 = self.readByte()
		self.username = self.readOsuString()
		beatmapCnt = self.readInt()
		if self.version > 20160403:
			self.unk1 = self.readInt()
		else:
			self.unk1 = 0

		self.beatmaps = []

		for i in range(beatmapCnt):
			self.beatmaps.append(BeatmapMetadata.fromOsuDb(self))
