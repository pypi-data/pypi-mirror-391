from pacab.types.reply import Reply


class Prompt:
	def __init__(
			self,
			name: str,
			text: str | list[str],
			replies: list[Reply],
			goto: str | None,
			show_separator: bool,
			end_dialog: bool,
		) -> None:
		self.name = name
		self.text = text
		self.replies = replies
		self.goto = goto
		self.show_separator = show_separator
		self.end_dialog = end_dialog
