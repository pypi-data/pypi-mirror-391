from typing import Self


class GameState:
	def __init__(
		self,
		scene_name: str,
		items: list[str],
		selected_item: str | None,
		game_globals: dict,
		dead_items: list[str],
		dead_replies: list[str],
		dead_animations: list[str],
		dead_music_2: list[str],
		dead_scene_actions: list[str],
	) -> None:
		self.scene_name = scene_name
		self.items = items
		self.selected_item = selected_item
		self.game_globals = game_globals
		self.dead_items = dead_items
		self.dead_replies = dead_replies
		self.dead_animations = dead_animations
		self.dead_music_2 = dead_music_2
		self.dead_scene_actions = dead_scene_actions
	
	@classmethod
	def new_game_state(cls, init_scene_name: str, game_globals: dict) -> Self:
		return cls(init_scene_name, [], None, game_globals.copy(), [], [], [], [], [])
