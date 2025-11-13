from pacab.types.animation import Animation
from pacab.types.condition import Condition
from pacab.types.interaction import Interaction
from pacab.types.navigation import Navigation
from pacab.types.sceneaction import SceneAction
from pacab.types.sceneitem import SceneItem


class Scene:
	def __init__(
			self,
			name: str,
			image: bytearray,
			music: str | None,
			music_2: str | None,
			music_2_loops: int,
			music_2_repeat: bool,
			music_2_conditions: list[Condition],
			music_2_conditions_use_or: bool,
			navs: list[Navigation],
			scene_actions: list[SceneAction],
			items: list[SceneItem],
			interactions: list[Interaction],
			animations: list[Animation] | None,
			overlays: list | None,
		) -> None:
		self.name = name
		self.image = image
		self.music = music
		self.music_2 = music_2
		self.music_2_loops = music_2_loops
		self.music_2_repeat = music_2_repeat
		self.music_2_conditions = music_2_conditions
		self.music_2_conditions_use_or = music_2_conditions_use_or
		self.navs = navs
		self.scene_actions = scene_actions
		self.items = items
		self.interactions = interactions
		self.animations = animations
		self.overlays = overlays
