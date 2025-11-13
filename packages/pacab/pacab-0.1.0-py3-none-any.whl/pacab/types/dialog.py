from pacab.types.prompt import Prompt


class Dialog:
	def __init__(self, name: str, title: str, init_prompt: str, prompts: list[Prompt]) -> None:
		self.name = name
		self.title = title
		self.init_prompt = init_prompt
		self.prompts = { prompts[i].name: prompts[i] for i in range(len(prompts)) }
