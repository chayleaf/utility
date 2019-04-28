class OsuEvent:
	LAYER_BACKGROUND = 0
	LAYER_FOREGROUND = 1
	LAYER_PASS = 2
	LAYER_FAIL = 3
	
	def __init__(**kwargs):
		pass

class OsuBackground(OsuEvent):
	def __init__(**kwargs):
		self.filename = kwargs.get('filename', '')
		self.time = kwargs.get('time', 0)
		self.x = kwargs.get('x', 0)
		self.y = kwargs.get('y', 0)

class OsuBackgroundVideo(OsuBackground):
	pass

class OsuBreak(OsuEvent):
	def __init__(**kwargs):
		self.time = kwargs.get('time', 0)
		self.endTime = kwargs.get('endTime', 0)
		
class OsuBackgroundColor(OsuEvent):
	def __init__(**kwargs):
		self.time = kwargs.get('time', 0)
		self.r = kwargs.get('r', 0)
		self.g = kwargs.get('g', 0)
		self.b = kwargs.get('b', 0)

class OsuSprite(OsuEvent):
	ORIGIN_TOPLEFT = 0
	ORIGIN_TOPCENTRE = 1
	ORIGIN_TOPRIGHT = 2
	ORIGIN_CENTRELEFT = 3
	ORIGIN_CENTRE = 4
	ORIGIN_CENTRERIGHT = 5
	ORIGIN_BOTTOMLEFT = 6
	ORIGIN_BOTTOMCENTRE = 7
	ORIGIN_BOTTOMRIGHT = 8
	
	def __init__(**kwargs):
		self.filename = kwargs.get('filename', '')
		self.x = kwargs.get('x', 0.0)
		self.y = kwargs.get('y', 0.0)
		self.origin = kwargs.get('origin', self.ORIGIN_CENTRE)
		self.layer = kwargs('layer', self.LAYER_BACKGROUND)

class OsuAnimation(OsuSprite):
	LOOP_FOREVER = 0
	LOOP_ONCE = 1
	
	def __init__(**kwargs):
		self.frameCount = kwargs.get('frameCount', 0)
		self.frameDelay = kwargs.get('frameDelay', 0.0)
		self.loopType = self.LOOP_FOREVER

class OsuSample(OsuEvent):
	def __init__(**kwargs):
		self.filename = kwargs.get('filename', '')
		self.time = kwargs.get('time', 0)
		self.volume = kwargs.get('volume', 0)
		self.layer = kwargs.get('layer', self.LAYER_BACKGROUND)

class OsuSpriteEvent:
	pass

class OsuTransformEvent(OsuSpriteEvent):
	EASING_NONE = 0
	EASING_SLOWDOWN = 1
	EASING_SPEEDUP = 2
	
	def __init__(**kwargs):
		self.easing = kwargs.get('easing', self.EASING_NONE)
		self.time = kwargs.get('time', 0)
		self.endTime = kwargs.get('endTime', 0)

class OsuFade(OsuTransformEvent):
	def __init__(**kwargs):
		super().__init__(kwargs)
		self.opacity = kwargs.get('opacity', 0.0)
		self.endOpacity = kwargs.get('endOpacity', 0.0)

class OsuMove(OsuTransformEvent):
	def __init__(**kwargs):
		super().__init__(kwargs)
		self.x = kwargs.get('x', None)
		self.y = kwargs.get('y', None)
		self.endX = kwargs.get('endX', None)
		self.endY = kwargs.get('endY', None)

class OsuScale(OsuTransformEvent):
	def __init__(**kwargs):
		super().__init__(kwargs)
		self.scale = kwargs.get('scale', 0.0)
		self.endScale = kwargs.get('endScale', 0.0)

class OsuVectorScale(OsuTransformEvent):
	def __init__(**kwargs):
		super().__init__(kwargs)
		self.scaleX = kwargs.get('scaleX', 0.0)
		self.scaleY = kwargs.get('scaleY', 0.0)
		self.endScaleX = kwargs.get('endScaleX', 0.0)
		self.endScaleY = kwargs.get('endScaleY', 0.0)

class OsuRotate(OsuTransformEvent):
	def __init__(**kwargs):
		super().__init__(kwargs)
		self.angle = kwargs.get('angle', 0.0)
		self.endAngle = kwargs.get('endAngle', 0.0)

class OsuColor(OsuTransformEvent):
	def __init__(**kwargs):
		super().__init__(kwargs)
		self.r = kwargs.get('r', 0.0)
		self.g = kwargs.get('g', 0.0)
		self.b = kwargs.get('b', 0.0)
		self.endR = kwargs.get('endR', 0.0)
		self.endG = kwargs.get('endG', 0.0)
		self.endB = kwargs.get('endB', 0.0)

class OsuLoop(OsuSpriteEvent):
	def __init__(**kwargs):
		self.time = kwargs.get('time', 0)
		self.loopCount = kwargs.get('loopCount', 0)
		self.events = kwargs.get('events', [])	

class OsuTriggeredLoop(OsuSpriteEvent):
	def __init__(**kwargs):
		self.triggerName = kwargs.get('triggerName', '')
		self.time = kwargs.get('time', 0)
		self.endTime = kwargs.get('endTime', 0)
		self.events = kwargs.get('events', [])	

class OsuParameters(OsuTransformEvent):
	EFFECT_HFLIP = 0
	EFFECT_VFLIP = 1
	EFFECT_ADDITIVEBLEND = 2
	
	def __init__(**kwargs):
		super().__init__(kwargs)
		self.effect = kwargs.get('effect', self.EFFECT_HFLIP)