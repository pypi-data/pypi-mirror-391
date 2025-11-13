import random

import pygame

from pacab.constants import *
from pacab.gamestate import GameState
from pacab.logger import Logger
from pacab.types.action import *


class ActionRunner:
	index = 0
	paused = False
	queue: list[Action] | None = None

	@staticmethod
	def execute_actions(game_state: GameState, actions: list[Action]) -> None:
		ActionRunner.queue = None

		index = 0

		for action in actions:
			index += 1

			if action.conditions and not Condition.check_conditions(game_state, action.conditions, action.conditions_use_or):
				Logger.log(f"Action '{action.type}' will not be executed!")
				continue

			Logger.log(f"Action '{action.type}' executing!")

			if action.is_async:
				if action.type == ACTION_TRANSITION_SCENE:
					if not action.params: return
					Logger.log(f"  Transitioning Scene to '{action.value}', transition type '{action.params[0]}'.")
					pygame.event.post(pygame.event.Event(SCENE_TRANSITION_START, { "scene_name": action.value, "transition_type": action.params[0], "speed": action.params[1] }))
				elif action.type == ACTION_BLOCK_INPUT:
					Logger.log(f"  Blocking input for {action.value}ms.")
					pygame.event.post(pygame.event.Event(BLOCK_INPUT_START, { "timeout": action.value }))
				elif action.type == ACTION_PAUSE_ACTIONS:
					Logger.log(f"  Pausing actions for {action.value}ms.")
					pygame.event.post(pygame.event.Event(PAUSE_ACTIONS_START, { "timeout": action.value }))
				ActionRunner.queue = actions[index:]
				return

			else:
				if action.type == ACTION_UPDATE_GAME_STATE:
					Logger.log(f"  Updating game_global '{action.key}' from '{game_state.game_globals[action.key]}' to '{action.value}'.")
					game_state.game_globals[action.key] = action.value

				elif action.type == ACTION_UPDATE_RANDOM:
					rand = random.randint(action.params[0], action.params[1]) # type: ignore
					Logger.log(f"  Updating game_global '{action.key}' from '{game_state.game_globals[action.key]}' to random value: '{rand}'.")
					game_state.game_globals[action.key] = rand

				elif action.type == ACTION_ADD_INVENTORY_ITEM:
					Logger.log(f"  Adding inventory item '{action.value}'.")
					if isinstance(action.value, str):
						game_state.items.append(action.value)

				elif action.type == ACTION_REMOVE_INVENTORY_ITEM:
					Logger.log(f"  Removing inventory item '{action.value}'.")
					if isinstance(action.value, str) and isinstance(game_state.selected_item, str):
						if action.value in game_state.items:
							game_state.items.remove(action.value)
							if action.value not in game_state.dead_items:
								game_state.dead_items.append(action.value)
							pygame.event.post(pygame.event.Event(INVENTORY_MENU_RESET_PAGE))
						if game_state.selected_item == action.value:
							pygame.event.post(pygame.event.Event(DISCARD_SELECTED_ITEM))

				elif action.type == ACTION_DISCARD_ITEM:
					Logger.log(f"  Discarding inventory item.")
					pygame.event.post(pygame.event.Event(DISCARD_SELECTED_ITEM))

				elif action.type == ACTION_GOTO_SCENE:
					Logger.log(f"  Going to Scene '{action.value}'.")
					pygame.event.post(pygame.event.Event(GOTO_SCENE, { "scene_name": action.value }))

				elif action.type == ACTION_START_ANIMATION:
					Logger.log(f"  Starting animation '{action.value}'.")
					if action.params:
						pygame.event.post(pygame.event.Event(START_ANIMATION, {
							"animation_name": action.value,
							"x": action.params[0],
							"y": action.params[1],
							"width": action.params[2],
							"height": action.params[3],
							"duration": action.params[4],
							"alpha": action.params[5],
							"hold_final_frame": action.params[6],
							"needs_scene_refresh": action.params[7],
						}))

				elif action.type == ACTION_START_DIALOG:
					Logger.log(f"  Starting dialog '{action.value}'.")
					pygame.event.post(pygame.event.Event(DIALOG_START, { "dialog_name": action.value }))

				elif action.type == ACTION_SHOW_MESSAGE:
					Logger.log(f"  Showing message.")
					text = action.params if action.params else action.value
					pygame.event.post(pygame.event.Event(DIALOG_FROM_STR, { "text": text }))

				elif action.type == ACTION_PLAY_SOUND:
					Logger.log(f"  Playing sound '{action.value}'.")
					pygame.event.post(pygame.event.Event(PLAY_SOUND, { "sound": action.value }))

				elif action.type == ACTION_END_GAME:
					Logger.log(f"  Ending game.")
					text = action.params if action.params else action.value
					pygame.event.post(pygame.event.Event(END_GAME, { "message": text }))

	@staticmethod
	def resume(game_state: GameState) -> None:
		ActionRunner.execute_actions(game_state, ActionRunner.queue) # type: ignore
