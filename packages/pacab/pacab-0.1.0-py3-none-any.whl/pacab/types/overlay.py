from pacab.gamestate import GameState
from pacab.types.animation import Animation
from pacab.types.condition import Condition
from pacab.types.interaction import Interaction
from pacab.types.navigation import Navigation
from pacab.types.scene import Scene
from pacab.types.sceneitem import SceneItem


class Overlay(Scene):
	def __init__(
		self,
			x: int,
			y: int,
			width: int,
			height: int,
			image: bytearray,
			navs: list[Navigation],
			items: list[SceneItem],
			interactions: list[Interaction],
			animations: list[Animation] | None,
			conditions: list[Condition],
			conditions_use_or: bool,
		) -> None:
		super().__init__("", image, None, None, 1, False, [], False, navs, [], items, interactions, animations, None)
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.conditions = conditions
		self.conditions_use_or = conditions_use_or

	def should_show(self, game_state: GameState) -> bool:
		return Condition.check_conditions(game_state, self.conditions, self.conditions_use_or)
