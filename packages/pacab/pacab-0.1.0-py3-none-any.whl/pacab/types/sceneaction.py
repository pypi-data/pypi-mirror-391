from pacab.logger import Logger
from pacab.types.action import Action
from pacab.types.condition import Condition
from pacab.gamestate import GameState


class SceneAction:
	def __init__(
			self,
			name: str,
			repeat: bool,
			actions: list[Action],
			conditions: list[Condition],
			conditions_use_or: bool,
		) -> None:
		self.name = name
		self.repeat = repeat
		self.actions = actions
		self.conditions = conditions
		self.conditions_use_or = conditions_use_or

	def should_execute(self, game_state: GameState) -> bool:
		if not self.repeat and self.name in game_state.dead_scene_actions:
			return False
		if not Condition.check_conditions(game_state, self.conditions, self.conditions_use_or):
			Logger.log(f"Scene action '{self.name}' will not execute, Conditions are not met.")
			return False
		return True
