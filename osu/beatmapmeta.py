class BeatmapMetadata:
	def __init__(self):
		self.artistA = ''
		self.artistU = ''
		self.titleA = ''
		self.titleU = ''
		self.creator = ''
		self.diffName = ''
		self.mp3 = ''
		self.md5 = ''
		self.filename = ''

		self.state = 0
		self.circles = 0
		self.sliders = 0
		self.spinners = 0
		self.editDate = 0
		self.AR = 0.0
		self.CS = 0.0
		self.HP = 0.0
		self.OD = 0.0
		self.SV = 0.0
		self.SR = [{},{},{},{}]
		self.drainTime = 0
		self.totalTime = 0
		self.previewTime = 0

		self.timingPoints = []

		self.mapId = 0
		self.mapsetId = 0
		self.threadId = 0
		self.rating = 0
		self.offset = 0
		self.stackLeniency = 0.0
		self.mode = 0
		self.source = ''
		self.tags = ''
		self.audioOffset = 0
		self.letterbox = ''
		self.notPlayed = 0
		self.lastPlayed = 0
		self.osz2 = 0
		self.path = ''
		self.lastSync = 0
		self.disableHitSounds = 0
		self.disableSkin = 0
		self.disableSb = 0
		
		self.bgDim = 0

	@classmethod
	def fromOsuDb(cls, osudb):
		self = cls()
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

		return self

	def hasSRData(self, mode=0):
		return len(self.SR[mode]) > 0

	def __str__(self):
		return f'{self.artistU if self.artistU != "" else self.artistA} - {self.titleU if self.titleU != "" else self.titleA} [{self.diffName}]'

	def filePath(self):
		return f'{self.path}/{self.filename}'