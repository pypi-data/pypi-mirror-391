from pacab.types.action import Action
from pacab.types.condition import Condition


class Reply:
	def __init__(
			self,
			name: str,
			text: str,
			actions: list[Action],
			conditions: list[Condition],
			goto: str | None,
			dialog_pause: int | None,
			end_dialog: bool,
		) -> None:
		self.name = name
		self.text = text
		self.actions = actions
		self.conditions = conditions
		self.goto = goto
		self.dialog_pause = dialog_pause
		self.end_dialog = end_dialog
