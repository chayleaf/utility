from .objects import *

class OsuBeatmap:
	MODE_OSU = 0
	MODE_TAIKO = 1
	MODE_CTB = 2
	MODE_MANIA = 3
	
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
							self.sampleSet = OsuObject.SAMPLESET_NORMAL
						elif v == 'Soft':
							self.sampleSet = OsuObject.SAMPLESET_SOFT
						elif v == 'Drum':
							self.sampleSet = OsuObject.SAMPLESET_DRUM
						elif v == 'Auto':
							self.sampleSet = OsuObject.SAMPLESET_AUTO
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
	
	#Objects
	
	MASK_OBJECT_IS_CIRCLE = 1
	MASK_OBJECT_IS_SLIDER = 2
	MASK_OBJECT_COMBO_START = 4
	MASK_OBJECT_IS_SPINNER = 8
	MASK_OBJECT_COMBO_COLOR_SKIP = 112
	MASK_OBJECT_IS_HOLD_NOTE = 128 #mania
	
	MASK_HITSOUND_NORMAL = 1
	MASK_HITSOUND_WHISTLE = 2
	MASK_HITSOUND_FINISH = 4
	MASK_HITSOUND_CLAP = 8
	
	def loadObject(self, initStr):
		initValues = initStr.split(',')
		
		if len(initValues) < 5:
			raise ValueError('Object info too short')
		
		args = {}
		
		args['x'] = int(initValues[0])
		args['y'] = int(initValues[1])
		args['time'] = int(initValues[2])
		
		objectType = int(initValues[3])
		args['comboStart'] = (objectType & self.MASK_OBJECT_COMBO_START) != 0
		args['comboColorSkip'] = (objectType & self.MASK_OBJECT_COMBO_COLOR_SKIP) >> 4
		
		def parseHitSound(hitSound):
			return {
				'hitSoundNormal': (hitSound & self.MASK_HITSOUND_NORMAL) != 0,
				'hitSoundWhistle': (hitSound & self.MASK_HITSOUND_WHISTLE) != 0,
				'hitSoundFinish': (hitSound & self.MASK_HITSOUND_FINISH) != 0,
				'hitSoundClap': (hitSound & self.MASK_HITSOUND_CLAP) != 0
			}
		
		args.update(parseHitSound(int(initValues[4])))
		
		def parseExtras(initValues, index):
			if len(initValues) <= index:
				return {}
			
			if not ':' in initValues[index]:
				return {}
			
			extras = initValues[index].split(':')
			if len(extras) != 5:
				return {}
			
			ret = {}
			
			numericFields = ['sampleSet', 'additionSet', 'customIndex', 'sampleVolume']
			for name, index in zip(numericFields, range(len(numericFields))):
				ret[name] = int(extras[index])
			ret['filename'] = extras[4]
			
			return ret
		
		if objectType | OsuObject.MASK_IS_CIRCLE:
			#x,y,time,type,hitSound,extras
			args.update(parseExtras(initValues, 5))
			return OsuCircle(args)
		elif objectType | OsuObject.MASK_IS_SLIDER: 
			#x,y,time,type,hitSound,sliderType|curvePoint1|curvePoint2...,repeat,pixelLength,edgeHitsounds,edgeAdditions,extras
			if len(initValues) < 10:
				raise ValueError('Object info too short')
			
			sliderPoints = initValues[5].split('|')
			slidetType = sliderPoints[0]
			sliderPoints = sliderPoints[1:]
			
			if sliderType == 'L':
				args['sliderType'] = OsuSlider.SLIDER_LINEAR
			elif sliderType == 'P':
				args['sliderType'] = OsuSlider.SLIDER_PERFECT
			elif sliderType == 'B':
				args['sliderType'] = OsuSlider.SLIDER_BEZIER
			elif sliderType == 'C':
				args['sliderType'] = OsuSlider.SLIDER_CATMULL
			else:
				print('Warning: unsupported slider type!')
			
			args['curvePoints'] = [tuple(map(int, point.split(':'))) for point in sliderPoints]
			args['repeatCount'] = int(initValues[6])
			args['sliderLength'] = int(initValues[7]) #actual slider length, if it doesnt match the points they will be changed apparently
			
			args['edgeHitSounds'] = [parseHitSound(hs) for hs in initValues[8].split('|')]
			args['edgeAdditions'] = []
			for sampleSets in initValues[9].split('|'):
				sampleSets = sampleSets.split(':')
				args['edgeAdditions'].append({'sampleSet': sampleSets[0], 'additionSet': sampleSets[1]})
			
			args.update(parseExtras(initValues, 10))
			return OsuSlider(args)
		
		if len(initValues) < 6:
			raise ValueError('Object info too short')
		
		if objectType | OsuObject.MASK_IS_SPINNER:
			#x,y,time,type,hitSound,endTime,extras
			args['endTime'] = int(initValues[5])
			args.update(parseExtras(initValues, 6))
			return OsuSpinner(args)
		elif objectType | OsuObject.MASK_IS_HOLD_NOTE:
			#x,y,time,type,hitSound,endTime:extras
			holdNoteValues = initValues[5].split(':', 1)
			args['endTime'] = int(holdNoteValues[0])
			args.update(parseExtras(holdNoteValues, 1))
			return OsuHoldNote(args)
		
		raise ValueError('Invalid object type')
	
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