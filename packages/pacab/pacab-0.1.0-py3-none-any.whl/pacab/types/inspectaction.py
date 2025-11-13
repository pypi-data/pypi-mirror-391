from pacab.types.action import Action
from pacab.types.condition import Condition


class InspectAction:
	def __init__(self, actions: list[Action], conditions: list[Condition], conditions_use_or: bool) -> None:
		self.actions = actions
		self.conditions = conditions
		self.conditions_use_or = conditions_use_or
