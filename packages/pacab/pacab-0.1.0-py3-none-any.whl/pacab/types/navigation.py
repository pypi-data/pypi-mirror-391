from pacab.types.box import Box
from pacab.types.scenetransition import SceneTransition


class Navigation(Box):
	def __init__(
			self,
			x: int,
			y: int,
			width: int,
			height: int,
			to_scene_name: str,
			sound: str | None,
			transition: str | None,
			transition_speed: str
		) -> None:
		super().__init__(x, y, width, height)
		self.to_scene_name = to_scene_name
		self.sound = sound
		self.transition_speed = transition_speed

		if transition:
			self.transition = SceneTransition(transition, to_scene_name, transition_speed)
		else:
			self.transition = None
