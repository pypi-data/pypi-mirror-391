SCENE_TRANSITION_BLACK = "black"
SCENE_TRANSITION_BLEND = "blend"
SCENE_TRANSITION_BLUR = "blur"
SCENE_TRANSITION_FADE_IN = "fadein"
SCENE_TRANSITION_FADE_OUT = "fadeout"
SCENE_TRANSITION_FADE_OUT_IN = "fadeoutin"
SCENE_TRANSITION_LEFT = "left"
SCENE_TRANSITION_RIGHT = "right"
SCENE_TRANSITION_UP = "up"
SCENE_TRANSITION_DOWN = "down"

class SceneTransition:
	def __init__(self, type: str, to_scene_name: str, speed: str) -> None:
		self.type = type

		self.to_scene_name = to_scene_name
		self.speed = speed
		
		self.cur_scene = None
		self.next_scene  = None
	
	types = [
		SCENE_TRANSITION_BLACK,
		SCENE_TRANSITION_BLEND,
		SCENE_TRANSITION_BLUR,
		SCENE_TRANSITION_FADE_IN,
		SCENE_TRANSITION_FADE_OUT,
		SCENE_TRANSITION_FADE_OUT_IN,
		SCENE_TRANSITION_LEFT,
		SCENE_TRANSITION_RIGHT,
		SCENE_TRANSITION_UP,
		SCENE_TRANSITION_DOWN,
	]
