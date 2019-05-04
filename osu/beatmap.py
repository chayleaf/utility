from .objects import *
from .enums import *

class Beatmap:
	def __init__(self, path):
		self.data = {}
		
		self.path = path
		with open(path, 'rb') as f:
			d = f.read().decode('utf-8')
		
		lines = [l.strip() for l in d.split('\n') if not l.startswith('//')]
		
		n = -1
		i = 0
		
		if len(lines) > 0 and 'osu file format' in lines[0] and 'v' in lines[0]:
			self.version = int(lines[0].split('v')[-1])
			i = 1
		else:
			raise ValueError(f'Invalid file header')
		
		while i < len(lines):
			if len(lines[i]) == 0 or lines[i][0] != '[':
				i += 1
				continue
			
			sectionName = lines[i].trim('[').trim(']')
			if sectionName in ['General', 'Editor', 'Metadata', 'Difficulty']:
				while i < len(lines) and len(lines[i]) > 0:
					k,v = lines[i].split(':' if sectionName in ['Metadata', 'Difficulty'] else ': ', 1)
					
					#General
					if k == 'AudioFilename':
						self.audioFile = v
					elif k == 'AudioLeadIn':
						self.audioLeadIn = int(v)
					elif k == 'PreviewTime':
						self.previewTime = int(v)
					elif k == 'Countdown':
						self.countdown = v == '1'
					elif k == 'SampleSet':
						if v == 'Normal':
							self.sampleSet = self.SAMPLESET_NORMAL
						elif v == 'Soft':
							self.sampleSet = self.SAMPLESET_SOFT
						elif v == 'Drum':
							self.sampleSet = self.SAMPLESET_DRUM
						elif v == 'Auto':
							self.sampleSet = self.SAMPLESET_AUTO
					elif k == 'StackLeniency':
						self.stackLeniency = float(v)
					elif k == 'Mode':
						self.mode = int(v)
					elif k == 'LetterboxInBreaks':
						self.letterboxInBreaks = v == '1'
					elif k == 'WidescreenStoryboard':
						self.widescreenStoryboard = v == '1'
					#Editor
					elif k == 'DistanceSpacing':
						self.editorSpacing = float(v)
					elif k == 'BeatDivisor':
						self.editorBeatDivisor = int(v)
					elif k == 'GridSize':
						self.editorGridSize = int(v)
					elif k == 'TimelineZoom':
						self.editorZoom = float(v)
					#Metadata
					elif k == 'Title':
						self. = 
					elif k == 'TitleUnicode':
						self. = 
					elif k == 'Artist':
						self. = 
					elif k == 'ArtistUnicode':
						self. = 
					elif k == 'Creator':
						self. = 
					elif k == 'Version':
						self. = 
					elif k == 'Source':
						self. = 
					elif k == 'Tags':
						self. = 
					elif k == 'BeatmapID':
						self. = 
					elif k == 'BeatmapSetID':
						self. = 
					#Difficulty
					elif k == '':
						self. = 
					elif k == '':
						self. = 
					elif k == '':
						self. = 
					elif k == '':
						self. = 
					elif k == '':
						self. = 
					elif k == '':
						self. = 
			
			i += 1
	
	#Events
	
	def loadEvent(self, lines, i, spriteEvent=False):
		ret = 0
		while i < len(lines) and len(lines[i]) == 0:
			i += 1
			ret += 1
		
		if i >= len(lines):
			return (None, ret)
		
		ret += 1
		
		if spriteEvent:
			return (OsuSpriteEvent(), ret) #TODO
		
		eventInfo = lines[i].split(',')
		
		type = eventInfo[0]
		
		if type in ['0', 'Background']:
			filename = eventInfo[2].strip('"')
			time = int(eventInfo[1])
			
			if len(eventInfo) >= 5:
				return (OsuBackground(filename=filename, time=time, x=int(eventInfo[3]), y=int(eventInfo[4])), ret)
			return (OsuBackground(filename=filename, time=time), ret)
		
		if type in ['1', 'Video']:
			filename = eventInfo[2].strip('"')
			time = int(eventInfo[1])
			
			if len(eventInfo) >= 5:
				return (OsuBackgroundVideo(filename=filename, time=time, x=int(eventInfo[3]), y=int(eventInfo[4])), ret)
			return (OsuBackgroundVideo(filename=filename, time=time), ret)
		
		if type in ['2', 'Break']:
			start = int(eventInfo[1])
			end = int(eventInfo[2])
			return (OsuBreak(time=start, endTime=end), ret)
		
		if type in ['3', 'Colour']:
			time = int(eventInfo[1])
			r,g,b = tuple(map(int, eventInfo[2:5]))
			return (OsuBackgroundColor(time=time, r=r, g=g, b=b), ret)
		
		if type in ['4', 'Sprite']:
			pass
		
		if type in ['5', 'Sample']:
			pass
		
		if type in ['6', 'Animation']:
			pass
		
		return (None, ret)
	
	def save(self):
		d = ['osu file format v', self.data['Version'], '\n']
		
		d.append('\n[General]\n')
		for k,v in self.data['General'].items():
			d.append(k)
			d.append(': ')
			d.append(v)
			d.append('\n')
		
		d.append('\n[Editor]\n')
		for k,v in self.data['Editor'].items():
			d.append(k)
			d.append(': ')
			d.append(v)
			d.append('\n')
		
		d.append('\n[Metadata]\n')
		for k,v in self.data['Metadata'].items():
			d.append(k)
			d.append(':')
			d.append(v)
			d.append('\n')
		
		d.append('\n[Difficulty]\n')
		for k,v in self.data['Difficulty'].items():
			d.append(k)
			d.append(':')
			d.append(v)
			d.append('\n')
		
		d.append('\n[Events]\n')
		for v in self.data['Events']:
			d.append(','.join(v))
			d.append('\n')
		
		d.append('\n[TimingPoints]\n')
		for v in self.data['TimingPoints']:
			d.append(','.join(v))
			d.append('\n')
		
		if 'Colours' in self.data.keys():
			d.append('\n[Colours]\n')
			for v in self.data['Colours']:
				d.append(v)
				d.append('\n')
		
		d.append('\n[HitObjects]\n')
		for v in self.data['HitObjects']:
			v = (*v[:-1], ':'.join(v[-1]))
			d.append(','.join(v))
			d.append('\n')
		
		d.append('\n')
		d = ''.join(d).encode('utf-8')
		
		with open(self.path, 'wb') as f:
			f.write(d)