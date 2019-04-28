class OsuObject:
	TYPE_CIRCLE = 0
	TYPE_SLIDER = 1
	TYPE_SPINNER = 2
	TYPE_HOLD_NOTE = 3
	
	SAMPLESET_AUTO = 0
	SAMPLESET_NORMAL = 1
	SAMPLESET_SOFT = 2
	SAMPLESET_DRUM = 3
	
	def OsuObject(**kwargs):
		#position
		self.x = kwargs.get('x', 0) #limit is 512
		self.y = kwargs.get('y', 0) #limit is 384 in-game but technically it is 512
		self.time = kwargs.get('time', 0) #ms
		
		#combo stuff
		self.comboStart = kwargs.get('comboStart', False) #is this object a combo start?
		self.comboColorSkip = kwargs.get('comboColorSkip', 0) #how many combo colors should we skip
		
		#which hitsounds to play
		self.hitSoundNormal = kwargs.get('hitSoundNormal', False)
		self.hitSoundWhistle = kwargs.get('hitSoundWhistle', False)
		self.hitSoundFinish = kwargs.get('hitSoundFinish', False)
		self.hitSoundClap = kwargs.get('hitSoundClap', False)
		
		#sample info
		self.sampleSet = kwargs.get('sampleSet', self.SAMPLESET_AUTO)
		self.additionSet = kwargs.get('additionSet', self.SAMPLESET_AUTO)
		self.customIndex = kwargs.get('customIndex', 0)
		self.sampleVolume = kwargs.get('sampleVolume', 0)
		self.sampleFilename = kwargs.get('filename', '') #override default file path which is {sampleSetType}-hit{soundType}{index}.wav

class OsuCircle(OsuObject):
	def OsuCircle(**kwargs):
		super().__init__(kwargs)

class OsuSlider(OsuObject):
	SLIDER_LINEAR = 0
	SLIDER_PERFECT = 1
	SLIDER_BEZIER = 2
	SLIDER_CATMULL = 3 #deprecated
	
	def OsuSlider(**kwargs):
		super().__init__(kwargs)
		#edgeAdditions
		self.sliderType = kwargs.get('sliderType', self.SLIDER_LINEAR)
		self.curvePoints = kwargs.get('curvePoints', [])
		self.sliderLength = kwargs.get('sliderLength', 0)
		
		#the last sample is played when the slider is released
		self.edgeHitSounds = kwargs.get('edgeHitSounds', [])
		self.edgeAdditions = kwargs.get('edgeAdditions', [])
		
		self.repeatCount = kwargs.get('repeatCount', 1)
	
	@property
	def repeatCount(self):
		return self._repeatCount
	
	@repeatCount.setter
	def repeatCount(self, val):
		self._repeatCount = val
		
		def resizeList(l, newLen, defaultVal):
			if newLen < len(l):
				for i in range(len(l), newLen):
					l.append(defaultVal)
			else:
				l = l[:newLen]
		
		self.edgeHitSounds = resizeList(self.edgeHitSounds, val + 1, {
			'hitSoundNormal': False,
			'hitSoundWhistle': False,
			'hitSoundFinish': False,
			'hitSoundClap': False
		})
		self.edgeAdditions = resizeList(self.edgeAdditions, val + 1, {
			'sampleSet': 0,
			'additionSet': 0
		})

class OsuSpinner(OsuObject):
	def OsuSpinner(**kwargs):
		super().__init__(kwargs)
		self.endTime = kwargs.get('endTime', 0)

class OsuHoldNote(OsuObject):
	def OsuHoldNote(**kwargs):
		super().__init__(kwargs)
		self.endTime = kwargs.get('endTime', 0)