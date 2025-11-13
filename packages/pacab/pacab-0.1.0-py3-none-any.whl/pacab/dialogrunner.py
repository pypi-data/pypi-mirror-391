import pygame

from pacab.actionrunner import ActionRunner
from pacab.constants import *
from pacab.gamestate import GameState
from pacab.types.dialog import Dialog
from pacab.types.prompt import Prompt
from pacab.types.reply import Reply


class DialogRunner:
	current_dialog = None
	__last_prompt_name = None

	@staticmethod
	def create_from_str(text: str | list[str], timeout: int | None = None, after_event: pygame.event.Event | None = None) -> None:
		is_blocking = True if after_event else False
		prompt = Prompt("", text, [], None, False, False)
		pygame.event.post(pygame.event.Event(DIALOG_CLEAR_TIMEOUT))
		pygame.event.post(pygame.event.Event(DIALOG_SHOW, { "prompt": prompt, "timeout": timeout, "is_blocking": is_blocking, "after_event": after_event }))

	@staticmethod
	def start_dialog(dialog: Dialog) -> None:
		DialogRunner.current_dialog = dialog
		DialogRunner.__last_prompt_name = dialog.init_prompt
		prompt = dialog.prompts[dialog.init_prompt]
		pygame.event.post(pygame.event.Event(DIALOG_CLEAR_TIMEOUT))
		pygame.event.post(pygame.event.Event(DIALOG_SHOW, { "title": dialog.title, "prompt": prompt }))

	@staticmethod
	def continue_dialog() -> None:
		if DialogRunner.current_dialog and isinstance(DialogRunner.__last_prompt_name, str):
			prompt = DialogRunner.current_dialog.prompts[DialogRunner.__last_prompt_name]
			if prompt.goto:
				prompt = DialogRunner.current_dialog.prompts[prompt.goto]
				pygame.event.post(pygame.event.Event(DIALOG_SHOW, { "title": DialogRunner.current_dialog.title, "prompt": prompt }))
			elif prompt.end_dialog:
				DialogRunner.end_dialog()

	@staticmethod
	def reply_dialog(reply: Reply, game_state: GameState) -> None:
		# Save reply to `game_state.dead_replies`
		if DialogRunner.current_dialog:
			reply_key = DialogRunner.current_dialog.name + "." + reply.name
			if reply_key not in game_state.dead_replies:
				game_state.dead_replies.append(reply_key)

		ActionRunner.execute_actions(game_state, reply.actions)

		if reply.dialog_pause:
			pygame.event.post(pygame.event.Event(REFRESH_SCENE, { "keep_animations": True }))
			pygame.event.post(pygame.event.Event(DIALOG_PAUSE_START, { "reply": reply, "timeout": reply.dialog_pause }))
		else:
			DialogRunner.reply_dialog_finish(reply)

	@staticmethod
	def reply_dialog_finish(reply: Reply) -> None:
		if reply.end_dialog:
			DialogRunner.end_dialog()
		elif isinstance(DialogRunner.current_dialog, Dialog):
			if isinstance(reply.goto, str):
				prompt = DialogRunner.current_dialog.prompts[reply.goto]
				DialogRunner.__last_prompt_name = prompt.name
				pygame.event.post(pygame.event.Event(DIALOG_SHOW, { "title": DialogRunner.current_dialog.title, "prompt": prompt }))
			else:
				DialogRunner.end_dialog()
	
	@staticmethod
	def end_dialog() -> None:
		DialogRunner.current_dialog = None
		DialogRunner.__last_prompt_name = None
		pygame.event.post(pygame.event.Event(REFRESH_SCENE, { "keep_animations": True }))
