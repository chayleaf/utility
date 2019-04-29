import struct
from .enums import *

class BinaryFile:
	def __init__(self, filename=None, mode='r'):
		self.data = b''
		self.cur = 0
		if filename is not None:
			if mode == 'r':
				with open(filename, 'rb') as f:
					self.filename = filename
					self.data = f.read()
			else:
				self.outFile = open(filename, 'wb')

	def close(self):
		self.outFile.close()

	def unpackData(self, fmt, byteCount):
		try:
			ret = struct.unpack(fmt, self.data[self.cur:self.cur+byteCount])[0]
			self.cur += byteCount
			return ret
		except:
			print('Error at', cur)
			raise

	def packData(self, fmt, data):
		self.outFile.write(struct.pack(fmt, data))

	def readDouble(self):	return self.unpackData('<d', 8)
	def writeDouble(self, n):	return self.packData('<d', n)
	def readFloat(self):	return self.unpackData('<f', 4)
	def writeFloat(self, n):	return self.packData('<f', n)
	def readLL(self):		return self.unpackData('<q', 8)
	def writeLL(self, n):	return self.packData('<q', n)
	def readULL(self):		return self.unpackData('<Q', 8)
	def writeULL(self, n):	return self.packData('<Q', n)
	def readInt(self):		return self.unpackData('<i', 4)
	def writeInt(self, n):	return self.packData('<i', n)
	def readUInt(self):		return self.unpackData('<I', 4)
	def writeUInt(self, n):	return self.packData('<I', n)
	def readShort(self):	return self.unpackData('<h', 2)
	def writeShort(self, n):	return self.packData('<h', n)
	def readUShort(self):	return self.unpackData('<H', 2)
	def writeUShort(self, n):	return self.packData('<H', n)
	def readChar(self):		return self.unpackData('<b', 1)
	def writeChar(self, n):	return self.packData('<b', n)
	def readUChar(self):	return self.unpackData('<B', 1)
	def writeUChar(self, n):	return self.packData('<B', n)
	def readByte(self): 	return self.readUChar()
	def writeByte(self, n):	return self.writeUChar(n)

	def read7bitInt(self):
		b = self.readByte()
		ret = b & 0x7F
		sh = 0
		while b & 0x80:
			sh += 7
			b = self.readByte()
			ret |= (b & 0x7F) << sh
		return ret

	def write7bitInt(self, b):
		self.writeByte((b & 0x7F) | (0x80 if b > 0x7F else 0))
		sh = 0
		while b > (0x7F << sh):
			sh += 7
			self.writeByte((b & (0x7F << sh)) | (0x80 if b > (0x7F << sh) else 0))

	def readBytes(self, n=None, len32=False):
		if n is None:
			n = (self.readInt() if len32 else self.read7bitInt())
		return self.unpackData(f'<{n}s', n)

	def writeBytes(self, b, len32=False):
		if len32:
			self.writeInt(len(b))
		else:
			self.write7bitInt(len(b))
		self.outFile.write(b)

	def readString(self, n=None, len32=False):
		curOld = self.cur
		try:
			return self.readBytes(n, len32).decode('utf-8')
		except:
			print('Error decoding string at', curOld)
			raise

	def writeString(self, s, len32=False):
		self.writeBytes(s.encode('utf-8'))
		
	def readOsuString(self):
		if self.readUChar() != 11:
			return ''
		return self.readString()

	def writeOsuString(self, s):
		if len(s) != 0:
			self.writeByte(11)
			self.writeString(s)
		else:
			self.writeByte(0)

	def readOsuDate(self):
		return self.readLL()

	def writeOsuDate(self, n):
		self.writeLL(n)

	def readOsuAny(self):
		t = self.readByte()
		if t == 1:
			return self.readByte()
		elif t == 2:
			return self.readByte()
		elif t == 3:
			return self.readUShort()
		elif t == 4:
			return self.readUInt()
		elif t == 5:
			return self.readULL()
		elif t == 6:
			return self.readChar()
		elif t == 7:
			return self.readShort()
		elif t == 8:
			return self.readInt()
		elif t == 9:
			return self.readLL()
		elif t == 10:
			return self.readChar()
		elif t == 11:
			return self.readString()
		elif t == 12:
			return self.readFloat()
		elif t == 13:
			return self.readDouble()
		elif t == 14:
			pass #readQuadruple lmao
		elif t == 15:
			return self.readOsuDate()
		elif t == 16:
			return self.readBytes(len32=True)
		elif t == 17:
			return self.readString(len32=True)
		raise NotImplementedError()

def totalHits(mode, cntMiss, cnt50, cnt100, cnt300, cntGeki, cntKatu):
	ret = cntMiss + cnt50 + cnt100 + cnt300

	if mode in [MODE_MANIA, MODE_CTB]:
		ret += cntKatu

	if mode == MODE_MANIA:
		ret += cntGeki

	return ret

def accuracy(*args):
	mode, cntMiss, cnt50, cnt100, cnt300, cntGeki, cntKatu = args

	tHits = totalHits(*args)

	if tHits == 0:
		return 0.0

	if mode == MODE_STD:
		return (cnt50 * 50 + cnt100 * 100 + cnt300 * 300) / tHits / 3
	elif mode == MODE_TAIKO:
		return (cnt100 * 150 + cnt300 * 300) / tHits / 3
	elif mode == MODE_CTB:
		return (cnt50 + cnt100 + cnt300) / tHits * 100
	elif mode == MODE_MANIA:
		return (cnt50 * 50 + cnt100 * 100 + cntKatu * 200 + (cnt300 + cntGeki) * 300) / tHits / 3
	
	raise NotImplementedError()