from .utility import BinaryFile

class BeatmapMetadata: #TODO separate class for beatmaps
	def __init__(self, osudb):
		self.artistA = osudb.readOsuString()
		self.artistU = osudb.readOsuString()
		self.titleA = osudb.readOsuString()
		self.titleU = osudb.readOsuString()
		self.creator = osudb.readOsuString()
		self.diffName = osudb.readOsuString()
		self.mp3 = osudb.readOsuString()
		self.md5 = osudb.readOsuString()
		self.filename = osudb.readOsuString()

		self.state = osudb.readByte()
		self.circles = osudb.readShort()
		self.sliders = osudb.readShort()
		self.spinners = osudb.readShort()
		self.editDate = osudb.readOsuDate()
		self.AR = osudb.readFloat()
		self.CS = osudb.readFloat()
		self.HP = osudb.readFloat()
		self.OD = osudb.readFloat()
		self.SV = osudb.readDouble()
		self.SR = []
		for i in range(4):
			modComboCnt = osudb.readInt()
			SRs = {}
			for i in range(modComboCnt):
				mods = int(osudb.readOsuAny())
				sr = float(osudb.readOsuAny())
			self.SR.append(SRs)
		self.drainTime = osudb.readInt()
		self.totalTime = osudb.readInt()
		self.previewTime = osudb.readInt()

		self.timingPoints = []
		timingPointCnt = osudb.readInt()
		for i in range(timingPointCnt):
			msPerBeat = osudb.readDouble()
			time = osudb.readDouble()
			inherit = osudb.readByte()
			self.timingPoints.append([msPerBeat, time, inherit])

		self.mapId = osudb.readInt()
		self.mapsetId = osudb.readInt()
		self.threadId = osudb.readInt()
		self.rating = osudb.readInt()
		self.offset = osudb.readShort()
		self.stackLeniency = osudb.readFloat()
		self.mode = osudb.readByte()
		self.source = osudb.readOsuString()
		self.tags = osudb.readOsuString()
		self.audioOffset = osudb.readShort()
		self.letterbox = osudb.readOsuString()
		self.notPlayed = osudb.readByte()
		self.lastPlayed = osudb.readOsuDate()
		self.osz2 = osudb.readByte()
		self.path = osudb.readOsuString()
		self.lastSync = osudb.readOsuDate()
		self.disableHitSounds = osudb.readByte()
		self.disableSkin = osudb.readByte()
		self.disableSb = osudb.readByte()
		osudb.readByte()
		self.bgDim = osudb.readShort()

		if osudb.version <= 20160403:
			osudb.readInt()
		else:
			osudb.readLL()

	def __str__(self):
		return f'{self.artistU if self.artistU != "" else self.artistA} - {self.titleU if self.titleU != "" else self.titleA}' 

class OsuDb(BinaryFile):
	def __init__(self, filename=None):
		self.version = 0

		if filename is None:
			super().__init__()
		else:
			super().__init__(filename, 'r')
			self.load(filename)

	def load(self, filename):
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
			self.beatmaps.append(BeatmapMetadata(self))
