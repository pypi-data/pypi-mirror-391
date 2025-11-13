from pacab.types.condition import Condition
from pacab.types.gamestatevalue import GameStateValue


ACTION_UPDATE_GAME_STATE = "update_game_state"
ACTION_UPDATE_RANDOM = "update_random"
ACTION_ADD_INVENTORY_ITEM = "add_inventory_item"
ACTION_REMOVE_INVENTORY_ITEM = "remove_inventory_item"
ACTION_DISCARD_ITEM = "discard_inventory_item"
ACTION_GOTO_SCENE = "goto_scene"
ACTION_TRANSITION_SCENE = "transition_scene"
ACTION_START_ANIMATION = "start_animation"
ACTION_START_DIALOG = "start_dialog"
ACTION_SHOW_MESSAGE = "show_message"
ACTION_PLAY_SOUND = "play_sound"
ACTION_BLOCK_INPUT = "block_input"
ACTION_PAUSE_ACTIONS = "pause_actions"
ACTION_END_GAME = "end_game"

class Action:
	def __init__(
			self,
			type: str,
			key: str | None,
			value: GameStateValue | None,
			params: list[GameStateValue] | None,
			conditions: list[Condition] | None,
			conditions_use_or: bool,
		) -> None:
		self.type = type
		self.key = key
		self.value = value
		self.params = params
		self.conditions = conditions
		self.conditions_use_or = conditions_use_or
		self.is_async = type == ACTION_TRANSITION_SCENE or type == ACTION_BLOCK_INPUT or type == ACTION_PAUSE_ACTIONS
	
	types = [
		ACTION_UPDATE_GAME_STATE,
		ACTION_UPDATE_RANDOM,
		ACTION_ADD_INVENTORY_ITEM,
		ACTION_REMOVE_INVENTORY_ITEM,
		ACTION_DISCARD_ITEM,
		ACTION_GOTO_SCENE,
		ACTION_TRANSITION_SCENE,
		ACTION_START_ANIMATION,
		ACTION_START_DIALOG,
		ACTION_SHOW_MESSAGE,
		ACTION_PLAY_SOUND,
		ACTION_BLOCK_INPUT,
		ACTION_PAUSE_ACTIONS,
		ACTION_END_GAME,
	]
