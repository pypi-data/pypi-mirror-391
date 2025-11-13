from pacab.types.action import Action
from pacab.types.box import Box
from pacab.types.condition import Condition


class Interaction(Box):
	def __init__(
			self,
			x: int,
			y: int,
			width: int,
			height: int,
			message: str | list | None,
			actions: list[Action],
			conditions: list[Condition],
			conditions_use_or: bool,
		) -> None:
		super().__init__(x, y, width, height)
		self.message = message
		self.actions = actions
		self.conditions = conditions
		self.conditions_use_or = conditions_use_or
