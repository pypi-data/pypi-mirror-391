from collections import namedtuple

AnimationFrame	= namedtuple("AnimationFrame", ["frame", "size", "has_white"])	

class AnimationFrames(list[AnimationFrame]):
	def __init__(self, filename: str, *args) -> None:
		list.__init__(self, *args)
		self.filename = filename
