from .utility import BinaryFile
import lzma
from .enums import MODE_MANIA, MODE_CTB

class Replay(BinaryFile):
	def __init__(self, filename=None, ignoreReplayData=False):
		self.mode = 0
		self.version = 0
		self.mapHash = ''
		self.username = ''
		self.replayHash = ''
		self.cnt300 = 0
		self.cnt100 = 0
		self.cnt50 = 0
		self.cntGeki = 0
		self.cntKatu = 0
		self.cntMiss = 0
		self.score = 0
		self.combo = 0
		self.perfectCombo = 0
		self.mods = 0
		self.hpGraph = []
		self.timestamp = 0
		self.scoreID = 0
		self.replayData = []
		self.randomSeed = None

		if filename is None:
			super().__init__()
		else:
			self.load(filename, ignoreReplayData)

	def load(self, filename, ignoreReplayData=False):
		super().__init__(filename, 'r')
		self.mode = self.readByte()
		self.version = self.readInt()
		self.mapHash = self.readOsuString()
		self.username = self.readOsuString()
		self.replayHash = self.readOsuString()
		self.cnt300 = self.readShort()
		self.cnt100 = self.readShort()
		self.cnt50 = self.readShort()
		self.cntGeki = self.readShort()
		self.cntKatu = self.readShort()
		self.cntMiss = self.readShort()
		self.score = self.readInt()
		self.combo = self.readShort()
		self.perfectCombo = self.readByte()
		self.mods = self.readInt()
		hpBarStr = self.readOsuString()
		self.hpGraph = []
		for uv in hpBarStr.split(','):
			if len(uv) == 0:
				continue
			t, val = uv.split('|')
			t = int(t)
			val = float(val)
			self.hpGraph.append((t, val))
		self.timestamp = self.readLL()
		rawReplayData = self.readBytes(len32=True)
		self.scoreID = self.readLL()

		if not ignoreReplayData:
			replayData = [s for s in lzma.decompress(data=rawReplayData).decode('utf-8').split(',') if len(s) > 0]
			self.replayData = []
			for wxyz in replayData[:-1] if self.version >= 20130319 else replayData:
				t, x, y, keyFlags = wxyz.split('|')
				t = int(t)
				x = float(x)
				y = float(y)
				keyFlags = int(keyFlags)
				self.replayData.append((t, x, y, keyFlags))
			if self.version >= 20130319:
				self.randomSeed = int(replayData[-1].split('|')[0])
