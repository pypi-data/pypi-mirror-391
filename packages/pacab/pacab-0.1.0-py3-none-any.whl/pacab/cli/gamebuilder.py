import os
import sys
from glob import glob

import tomllib
from PIL import Image, ImageSequence

from pacab.displayinfo import SCENE_W, SCENE_H
from pacab.types.action import *
from pacab.types.animation import Animation
from pacab.types.animationframes import AnimationFrame, AnimationFrames
from pacab.types.condition import *
from pacab.types.dialog import Dialog
from pacab.types.inspectaction import InspectAction
from pacab.types.interaction import Interaction
from pacab.types.inventoryitem import InventoryItem
from pacab.types.itemcombination import ItemCombination
from pacab.types.navigation import Navigation
from pacab.types.overlay import Overlay
from pacab.types.pacabgame import PacabGame
from pacab.types.prompt import Prompt
from pacab.types.reply import Reply
from pacab.types.scene import Scene
from pacab.types.sceneaction import SceneAction
from pacab.types.sceneitem import SceneItem
from pacab.types.scenetransition import SceneTransition
from pacab.types.theme import *


DIR_SEPARATOR = "\\" if sys.platform == "win32" else "/"

class ValidationError:
	def __init__(self, type: str, filename: str, message: str) -> None:
		self.type = type
		self.filename = filename
		self.message = message
	
	def __str__(self):
		return f"""{"Error" if self.type == "E" else "Warning" if self.type == "W" else "Info"}
File:\t\t{self.filename}
Message:\t{self.message}
"""

_errors: list[ValidationError] = []

class GameBuilder:
	@staticmethod
	def build(file_path: str, debug_mode: bool) -> PacabGame:
		pacab_game = GameBuilder.__build_pacab_game(file_path, debug_mode)
		
		if pacab_game != None:
			GameBuilder.__post_build_validations(pacab_game, file_path)

			if len(_errors):
				errors = [e for e in _errors if e.type == "E"]
				warnings = [e for e in _errors if e.type == "W"]
				infos = [e for e in _errors if e.type == "I"]
				
				for error in errors: print(error)
				if (len(errors)): print("----------")
				for warning in warnings: print(warning)
				if (len(warnings)): print("----------")
				for info in infos: print(info)
				if (len(infos)): print("----------")

				if len(errors):
					raise Exception("*** Error(s) found - Unable to build Pacab Game! ***")

			print(f"\n'{pacab_game.name}' built successfully!\n")

		if pacab_game:
			return pacab_game
		else:
			raise Exception("*** Error(s) found - Unable to build Pacab Game! ***")

	@staticmethod
	def __build_pacab_game(file_path: str, debug_mode: bool) -> PacabGame | None:
		root_dir = os.path.dirname(file_path)
		data = GameBuilder.__read_file(file_path)
		if data == None: return None

		name = data.get("name", None)
		if not isinstance(name, str) or len(name) == 0:
			_errors.append(ValidationError("E", file_path, "Value 'name' missing or invalid."))
		else:
			print(f"Building '{name}'")

		short_name = file_path.replace(".toml", "").split(DIR_SEPARATOR).pop()

		init_scene_name = data.get("init_scene", None)
		if not isinstance(init_scene_name, str):
			_errors.append(ValidationError("E", file_path, "Value 'init_scene' missing or invalid."))

		start_game_message = data.get("start_game_message", None)
		if start_game_message == None:
			_errors.append(ValidationError("I", file_path, "Value 'start_game_message' missing."))
		elif not isinstance(start_game_message, str | list):
			_errors.append(ValidationError("E", file_path, "Value 'start_game_message' invalid."))

		init_items = data.get("init_items", None)
		if init_items == None:
			_errors.append(ValidationError("I", file_path, "Value 'init_items' missing."))
		elif not isinstance(init_items, list):
			_errors.append(ValidationError("E", file_path, "Value 'init_items' invalid."))
		else:
			for item_name in init_items:
				if not isinstance(item_name, str):
					_errors.append(ValidationError("E", file_path, f"Value '{item_name}' in 'init_items' invalid."))

		game_globals = data.get("game_globals", None)
		if game_globals == None:
			_errors.append(ValidationError("W", file_path, "Value 'game_globals' missing."))
			game_globals = {}
		elif not isinstance(game_globals, dict):
			_errors.append(ValidationError("E", file_path, "Value 'game_globals' invalid."))
		else:
			for key, value in game_globals.items():
				if not isinstance(value, bool | int | str):
					_errors.append(ValidationError("E", file_path, f"Value 'game_globals.{key}' invalid."))

		icon = GameBuilder.__get_icon_image(os.path.join(root_dir, "assets"))
		theme = GameBuilder.__build_theme(data, file_path, root_dir)
		audio_files = GameBuilder.__build_audio(root_dir)
		animation_frames = GameBuilder.__build_animation_frames(root_dir)
		dialogs = GameBuilder.__build_dialogs(root_dir)
		inventory_items = GameBuilder.__build_inventory_items(root_dir)
		scenes = GameBuilder.__build_scenes(root_dir, inventory_items, [x[0] for x in audio_files])
		translations = GameBuilder.__build_translations(root_dir)

		return PacabGame(
			name,
			short_name,
			init_scene_name,
			start_game_message,
			init_items,
			icon,
			theme,
			scenes,
			translations,
			inventory_items,
			animation_frames,
			dialogs,
			game_globals,
			audio_files,
			debug_mode,
		)

	@staticmethod
	def __post_build_validations(pacab_game: PacabGame, filename: str) -> None:
		dialog_names = list(map(lambda x: x.name, pacab_game.dialogs))
		item_names = list(map(lambda x: x.name, pacab_game.items))
		scene_names = list(map(lambda x: x.name, pacab_game.scenes))
		sound_names = list(map(lambda x: os.path.basename(x), [x[0] for x in pacab_game.audio_files]))

		actions = []
		animations = []
		conditions = []
		dialogs = pacab_game.dialogs
		interactions = []
		items = pacab_game.items
		navs = []
		prompts = []
		replies = []
		scenes = []
		scene_items = []

		go_to_scene_names = []
		add_item_names = []
		start_dialogs = []

		if pacab_game.init_items:
			for item in pacab_game.init_items:
				add_item_names.append(item)
		for scene in pacab_game.scenes:
			scenes.append(scene)
			for scene_action in scene.scene_actions:
				for action in scene_action.actions:
					actions.append(("scene.scene_action.action", action))
					if action.conditions:
						for condition in action.conditions:
							conditions.append(("scene.action.condition", condition))
			for nav in scene.navs:
				navs.append(("scene.nav", nav))
			for interaction in scene.interactions:
				interactions.append(("scene.interaction", interaction))
				for action in interaction.actions:
					actions.append(("scene.interaction.action", action))
					if action.conditions:
						for condition in action.conditions:
							conditions.append(("scene.action.condition", condition))
				for condition in interaction.conditions:
					conditions.append(("scene.interaction.condition", condition))
			for item in scene.items:
				scene_items.append(("scene.item", item))
				add_item_names.append(item.name)
			for animation in scene.animations or []:
				animations.append(animation.filename)
				for condition in animation.conditions:
					conditions.append(("animation.condition", condition))
			for overlay in scene.overlays or []:
				for condition in overlay.conditions:
					conditions.append(("scene.overlay.condition", condition))
				for nav in overlay.navs:
					navs.append(("overlay.nav", nav))
				for interaction in overlay.interactions:
					interactions.append(("overlay.interaction", interaction))
					for action in interaction.actions:
						actions.append(("overlay.interaction.action", action))
						if action.conditions:
							for condition in action.conditions:
								conditions.append(("overlay.interaction.action.condition", condition))
					for condition in interaction.conditions:
						conditions.append(("overlay.interaction.condition", condition))
				for item in overlay.items:
					scene_items.append(("overlay.item", item))
					add_item_names.append(item.name)
				for animation in overlay.animations or []:
					animations.append(animation.filename)
		for dialog in pacab_game.dialogs:
			for _, prompt in dialog.prompts.items():
				prompts.append((dialog, prompt))
				for reply in prompt.replies:
					replies.append((dialog, prompt, reply))
					for action in reply.actions:
						actions.append(("dialog.reply.action", action))
						if action.conditions:
							for condition in action.conditions:
								conditions.append(("dialog.reply.action.condition", condition))
					for condition in reply.conditions:
						conditions.append(("overlay.reply.condition", condition))

		if pacab_game.init_scene_name not in scene_names:
			_errors.append(ValidationError("E", filename, f"Value '{pacab_game.init_scene_name}' for 'init_scene_name' not a valid scene."))

		for action in actions:
			obj_name, action = action
			if action.type == ACTION_GOTO_SCENE:
				if action.value not in scene_names:
					_errors.append(ValidationError("E", "", f"Value '{action.value}' for '{obj_name}.value' not a valid scene."))
				else:
					go_to_scene_names.append(action.value)
			if action.type == ACTION_TRANSITION_SCENE:
				if action.value not in scene_names:
					_errors.append(ValidationError("E", "", f"Value '{action.value}' for '{obj_name}.value' not a valid scene."))
				else:
					go_to_scene_names.append(action.value)
			elif (action.type == ACTION_ADD_INVENTORY_ITEM or action.type == ACTION_REMOVE_INVENTORY_ITEM):
				if action.value not in item_names:
					_errors.append(ValidationError("E", "", f"Value '{action.value}' for '{obj_name}.value' not a valid item."))
				else:
					add_item_names.append(action.value)
			elif action.type == ACTION_UPDATE_GAME_STATE and action.key not in pacab_game.game_globals.keys():
				_errors.append(ValidationError("E", "", f"Value '{action.key}' for '{obj_name}.key' not a value in `game_globals`."))
			elif action.type == ACTION_START_DIALOG:
				if action.value not in dialog_names:
					_errors.append(ValidationError("E", "", f"Value '{action.value}' for '{obj_name}.value' not a valid dialog."))
				else:
					start_dialogs.append(action.value)
			elif action.type == ACTION_PLAY_SOUND and action.value not in sound_names:
				_errors.append(ValidationError("E", "", f"Value '{action.value}' for '{obj_name}.value' not a valid audio file."))
			elif action.type == ACTION_BLOCK_INPUT and (not isinstance(action.value, int) or (isinstance(action.value, int) and action.value <= 0)):
				_errors.append(ValidationError("E", "", f"Value '{action.value}' for '{obj_name}.value' for 'block_input' invalid."))
			elif action.type == ACTION_PAUSE_ACTIONS and (not isinstance(action.value, int) or (isinstance(action.value, int) and action.value <= 0)):
				_errors.append(ValidationError("E", "", f"Value '{action.value}' for '{obj_name}.value' for 'pause_actions' invalid."))
			elif action.type == ACTION_START_ANIMATION:
				animations.append(action.value)

		for condition in conditions:
			obj_name, condition = condition
			if condition.type == COND_KEY_VALUE:
				if condition.key not in pacab_game.game_globals.keys():
					_errors.append(ValidationError("E", "", f"Value '{condition.key}' for '{obj_name}.key' not a value in `game_globals`."))
			elif condition.type == COND_ITEM or condition.type == COND_INVENTORY_ITEM:
				if condition.value not in item_names:
					_errors.append(ValidationError("E", "", f"Value '{condition.value}' for '{obj_name}.value' not a valid item."))

		for dialog in dialogs:
			if dialog.init_prompt not in dialog.prompts.keys():
				_errors.append(ValidationError("E", "", f"Value '{dialog.init_prompt}' for 'dialog.init_prompt' for dialog '{dialog.name}' not a valid prompt."))
			if dialog.name not in start_dialogs:
				_errors.append(ValidationError("W", "", f"Dialog '{dialog.name}' is not being used."))

		for nav in navs:
			obj_name, nav = nav
			if nav.to_scene_name not in scene_names:
				_errors.append(ValidationError("E", "", f"Value '{nav.to_scene_name}' for '{obj_name}.to_scene_name' not a valid scene."))
			else:
				go_to_scene_names.append(nav.to_scene_name)
			if nav.sound and nav.sound not in sound_names:
				_errors.append(ValidationError("E", "", f"Value '{nav.sound}' for '{obj_name}.sound' not a valid audio file."))

		for prompt in prompts:
			dialog, prompt = prompt
			if prompt.goto and prompt.goto not in dialog.prompts.keys():
				_errors.append(ValidationError("E", "", f"Value '{prompt.goto}' for dialog '{dialog.name}', prompt '{prompt.name}' not a valid prompt."))

		for reply in replies:
			dialog, prompt, reply = reply
			if reply.goto and reply.goto not in dialog.prompts.keys():
				_errors.append(ValidationError("E", "", f"Value '{reply.goto}' for dialog '{dialog.name}', prompt '{prompt.name}', reply '{reply.name}' not a valid prompt."))

		for scene in scenes:
			if scene.music and scene.music not in sound_names:
				_errors.append(ValidationError("E", "", f"Value '{scene.music}' for 'scene.music' not a valid audio file."))
			if scene.name not in go_to_scene_names:
				_errors.append(ValidationError("W", "", f"Scene '{scene.name}' is not being used."))

		for item in scene_items:
			obj_name, item = item
			if item.name not in item_names:
				_errors.append(ValidationError("E", "", f"Value '{item.name}' for '{obj_name}' not a valid item."))

		if pacab_game.init_items:
			for item_name in pacab_game.init_items:
				if item_name not in item_names:
					_errors.append(ValidationError("E", filename, f"Value '{item_name}' for 'init_items' not a valid item."))

		for item in items:
			if item.combos and len(item.combos):
				for combo in item.combos:
					add_item_names.append(combo.to_item)
					if combo.sound and combo.sound not in sound_names:
						_errors.append(ValidationError("E", "", f"Value '{combo.sound}' for 'combination.sound' not a valid audio file."))
			for deconstruct_item in item.deconstruct_to:
				if deconstruct_item not in item_names:
					_errors.append(ValidationError("E", "", f"Value '{deconstruct_item}' for 'item.deconstruct_to' not a valid item."))
				else:
					add_item_names.append(deconstruct_item)
			if item.pickup_sound and item.pickup_sound not in sound_names:
				_errors.append(ValidationError("E", "", f"Value '{item.pickup_sound}' for '{obj_name}.pickup_sound' not a valid audio file."))

		for item_name in item_names:
			if item_name not in add_item_names:
				_errors.append(ValidationError("W", "", f"Item '{item_name}' is not being used."))
		
		all_animation_names = [x.filename for x in pacab_game.animation_frames]
		new_animation_frames = []
		for animation in all_animation_names:
			if animation not in animations:
				_errors.append(ValidationError("W", "", f"Animation '{animation}' is not used."))
			else:
				new_animation_frames.append(pacab_game.get_animation_frames(animation))
		pacab_game.animation_frames = new_animation_frames
		for animation in animations:
			if animation not in all_animation_names:
				_errors.append(ValidationError("E", "", f"Animation '{animation}' does not exist."))
				
	@staticmethod
	def __build_audio(root_dir: str) -> list[tuple[str, bytearray]]:
		print("Building audio files...")

		dir_path = os.path.join(root_dir, "audio")
		file_paths = [y for x in os.walk(dir_path) for y in glob(os.path.join(x[0], "*"))]

		files = []

		for file_path in file_paths:
			with open(file_path, 'rb') as file:
				data = bytearray(file.read())
			file = (os.path.basename(file_path), data)
			files.append(file)

		print(f"{len(files)} audio files!")
		return files

	@staticmethod
	def __build_scenes(root_dir: str, inventory_items: list[InventoryItem], audio_file_names: list[str]) -> list[Scene]:
		print("Building scenes...")

		dir_path = os.path.join(root_dir, "scenes")
		scene_files = [y for x in os.walk(dir_path) for y in glob(os.path.join(x[0], "*.toml"))]

		scenes = []
		for scene_file in scene_files:
			scene_dir = os.path.dirname(scene_file)
			data = GameBuilder.__read_file(scene_file)
			if data == None: continue

			name = scene_file.replace(".toml", "").split(DIR_SEPARATOR).pop()

			image_path = data.get("image", None)
			if not isinstance(image_path, str):
				_errors.append(ValidationError("E", scene_file, "Value 'image' missing or invalid."))
			else:
				image_path = os.path.join(scene_dir, image_path)
				if not os.path.exists(image_path):
					_errors.append(ValidationError("E", scene_file, f"Scene image file '{image_path}' does not exist."))

			music = data.get("music", None)
			if not isinstance(music, str | None) or (isinstance(music, str) and not len(music)):
				_errors.append(ValidationError("E", scene_file, "Value 'music' invalid."))
			if music and not len([x for x in audio_file_names if music in x]):
				_errors.append(ValidationError("E", scene_file, f"Scene music file '{music}' does not exist."))
			
			music_2 = data.get("music_2", None)
			if not isinstance(music_2, str | None) or (isinstance(music_2, str) and not len(music_2)):
				_errors.append(ValidationError("E", scene_file, "Value 'music_2' invalid."))
			if music_2 and not len([x for x in audio_file_names if music_2 in x]):
				_errors.append(ValidationError("E", scene_file, f"Scene music_2 file '{music_2}' does not exist."))
			
			music_2_loops = data.get("music_2_loops", -1)
			if not isinstance(music_2_loops, int) or (isinstance(music_2_loops, int) and (music_2_loops < -1 or music_2_loops == 0)):
				_errors.append(ValidationError("E", scene_file, "Value 'music_2_loops' invalid."))

			music_2_repeat = data.get("music_2_repeat", True)
			if not isinstance(music_2_repeat, bool):
				_errors.append(ValidationError("W", scene_file, "Value 'music_2_repeat' invalid."))
				music_2_repeat = True

			music_2_conditions = GameBuilder.__build_conditions(data, scene_file, "scene", "music_2_conditions") 
			music_2_conditions_use_or = data.get("music_2_conditions_use_or", False)

			navs = GameBuilder.__build_navs(data, scene_file, "scene")

			scene_actions = GameBuilder.__build_scene_actions(data, scene_file, "scene", name)

			items = GameBuilder.__build_scene_items(data, scene_file, "scene", inventory_items)

			interactions = GameBuilder.__build_interactions(data, scene_file, "scene")

			animations = GameBuilder.__build_scene_animations(root_dir, data, scene_file, "scene", name)

			overlays = []
			overlay_list = data.get("overlays", [])
			if not isinstance(overlay_list, list):
				_errors.append(ValidationError("E", scene_file, "Value 'overlays' invalid."))
			elif len(overlay_list):
				for i, overlay in enumerate(overlay_list):
					box = GameBuilder.__build_box(overlay, scene_file, "overlay")

					overlay_image_path = overlay.get("image", None)
					if not isinstance(overlay_image_path, str) or (isinstance(overlay_image_path, str) and not len(overlay_image_path)):
						_errors.append(ValidationError("E", scene_file, "Value 'scene.overlay.image' missing or invalid."))
					else:
						overlay_image_path = os.path.join(root_dir, "overlays", overlay_image_path)
						if not os.path.exists(overlay_image_path):
							_errors.append(ValidationError("E", scene_file, f"Overlay image file '{overlay_image_path}' does not exist."))
				
					overlay_navs = GameBuilder.__build_navs(overlay, scene_file, "overlay")
		
					overlay_items = GameBuilder.__build_scene_items(overlay, scene_file, "overlay", inventory_items)
		
					overlay_interactions = GameBuilder.__build_interactions(overlay, scene_file, "overlay")

					animation_namespace = name + "_" + str(i)
					overlay_animations = GameBuilder.__build_scene_animations(root_dir, overlay, scene_file, "overlay", animation_namespace)

					overlay_conditions = GameBuilder.__build_conditions(overlay, scene_file, "overlay") 

					overlay_conditions_use_or = overlay.get("conditions_use_or", False)
					if not isinstance(overlay_conditions_use_or, bool):
						_errors.append(ValidationError("W", scene_file, f"Value 'overlay.interaction.conditions_use_or' invalid."))
						overlay_conditions_use_or = False

					if box and overlay_image_path:
						x, y, width, height = box

						with open(overlay_image_path, "rb") as file:
							overlay_image = bytearray(file.read())

						overlays.append(Overlay(
							x,
							y,
							width,
							height,
							overlay_image,
							overlay_navs,
							overlay_items,
							overlay_interactions,
							overlay_animations,
							overlay_conditions,
							overlay_conditions_use_or,
						))

			if name and image_path:
				with open(image_path, "rb") as file:
					image = bytearray(file.read())
				scenes.append(Scene(
					name,
					image,
					music,
					music_2,
					music_2_loops,
					music_2_repeat,
					music_2_conditions,
					music_2_conditions_use_or,
					navs,
					scene_actions,
					items,
					interactions,
					animations,
					overlays,
				))
		
		print(f"{len(scenes)} scenes!")
		return scenes

	@staticmethod
	def __build_animation_frames(root_dir: str) -> list[AnimationFrames]:
		print("Building animations...")

		dir_path = os.path.join(root_dir, "animations")
		file_paths = [y for x in os.walk(dir_path) for y in glob(os.path.join(x[0], "*"))]

		animation_frames = []
		for file_path in file_paths:
			if os.path.isdir(file_path): continue
			frames = GameBuilder.__unpack_gif(file_path)
			animation_frames.append(frames)

		print(f"{len(animation_frames)} animations!")
		return animation_frames

	@staticmethod
	def __build_scene_animations(root_dir: str, data: dict, filename: str, obj_name: str, namespace: str) -> list[Animation] | None:
		animations = []
		animations_list = data.get("animations", [])
		if not isinstance(animations_list, list):
			_errors.append(ValidationError("E", filename, f"Value '{obj_name}.animations' invalid."))
		elif len(animations_list):
			for animation in animations_list:
				box = GameBuilder.__build_box(animation, filename, "animation")

				name = None

				image = animation.get("image", None)
				if not isinstance(image, str) or (isinstance(image, str) and not len(image)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.image' for missing or invalid."))
				else:
					name = image
					image = glob(os.path.join(root_dir, "animations", "**", image), recursive=True)
					image = "" if not len(image) else image[0]
					if not os.path.exists(image):
						_errors.append(ValidationError("E", filename, f"Animation image file '{image}' does not exist."))
					else:
						image = image[0]

				loops = animation.get("loops", -1)
				if not isinstance(loops, int) or (isinstance(loops, int) and (loops < -1 or loops == 0)):
					_errors.append(ValidationError("E", filename, "Value 'loops' invalid."))

				repeat = animation.get("repeat", True)
				if not isinstance(repeat, bool):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.animation.repeat' invalid."))
					repeat = True

				duration = animation.get("duration", None)
				if not isinstance(duration, int) or duration <= 0:
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.animation.duration' invalid."))

				alpha = animation.get("alpha", None)
				if not isinstance(alpha, int | None) or (isinstance(alpha, int) and (alpha <= 0 or alpha > 255)):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.animation.alpha' invalid, must be between 0 and 255."))
					alpha = 255
				if alpha == None: alpha = 255

				hold_final_frame = animation.get("hold_final_frame", False)
				if not isinstance(hold_final_frame, bool):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.animation.hold_final_frame' invalid."))
					hold_final_frame = False

				conditions = GameBuilder.__build_conditions(animation, filename, "interaction")

				conditions_use_or = animation.get("conditions_use_or", False)
				if not isinstance(conditions_use_or, bool):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.animation.conditions_use_or' invalid."))
					conditions_use_or = False

				if box and name and duration:
					x, y, width, height = box
					animations.append(Animation(
						x,
						y,
						width,
						height,
						namespace + "_" + name,
						name,
						loops,
						repeat,
						duration,
						alpha,
						hold_final_frame,
						conditions,
						conditions_use_or,
					))

		return animations

	@staticmethod
	def __build_dialogs(root_dir: str) -> list[Dialog]:
		print("Building dialogs...")

		dir_path = os.path.join(root_dir, "dialogs")
		dialog_files = [y for x in os.walk(dir_path) for y in glob(os.path.join(x[0], "*.toml"))]

		dialogs = []
		for dialog_file in dialog_files:
			root_dir = os.path.dirname(dialog_file)
			data = GameBuilder.__read_file(dialog_file)
			if data == None: continue

			dialog_name = dialog_file.replace(".toml", "").split(DIR_SEPARATOR).pop()

			title = data.get("title", None)
			if not isinstance(title, str):
				_errors.append(ValidationError("E", dialog_file, "Value 'title' missing or invalid."))
			if len(title) > 30:
				_errors.append(ValidationError("E", dialog_file, "Value 'title' is over the maximum length (30)."))

			init_prompt  = data.get("init_prompt", None)
			if not isinstance(init_prompt, str) or not len(init_prompt):
				_errors.append(ValidationError("E", dialog_file, "Value 'init_prompt' missing or invalid."))

			prompts = []
			prompt_list  = data.get("prompts", [])
			if not isinstance(prompt_list, list) or not len(prompt_list):
				_errors.append(ValidationError("E", dialog_file, "Value 'prompts' missing or invalid."))
			elif len(prompt_list):
				for prompt in prompt_list:
					prompt_name = prompt.get("name", None)
					if not isinstance(prompt_name, str) or not len(prompt_name):
						_errors.append(ValidationError("E", dialog_file, "Value 'prompt.name' missing or invalid."))

					text = prompt.get("text", None)
					if not isinstance(text, str | list) or not len(text):
						_errors.append(ValidationError("E", dialog_file, "Value 'prompt.text' missing or invalid."))
					if isinstance(text, list):
						for t in text:
							if not isinstance(t, str): _errors.append(ValidationError("E", dialog_file, "Value 'prompt.text' invalid."))
					
					replies = []
					reply_list = prompt.get("replies", [])
					if not isinstance(reply_list, list):
						_errors.append(ValidationError("E", dialog_file, "Value 'prompt.replies' missing or invalid."))
					elif len(reply_list):
						for reply in reply_list:
							reply_name = reply.get("name", None)
							if not isinstance(reply_name, str) or not len(reply_name):
								_errors.append(ValidationError("E", dialog_file, "Value 'prompt.reply.name' missing or invalid."))

							reply_text = reply.get("text", None)
							if not isinstance(reply_text, str) or not len(reply_text):
								_errors.append(ValidationError("E", dialog_file, "Value 'prompt.reply.text' missing or invalid."))

							reply_actions = GameBuilder.__build_actions(reply, dialog_file, "reply")

							reply_conditions = GameBuilder.__build_conditions(reply, dialog_file, "reply")

							reply_goto = reply.get("goto", None)
							if not isinstance(reply_goto, str | None) or (isinstance(reply_goto, str) and not len(reply_goto)):
								_errors.append(ValidationError("E", dialog_file, "Value 'prompt.reply.goto' missing or invalid."))

							reply_dialog_pause = reply.get("dialog_pause", None)
							if not isinstance(reply_dialog_pause, int | None) or (isinstance(reply_dialog_pause, int) and reply_dialog_pause <= 0):
								_errors.append(ValidationError("E", dialog_file, f"Value 'prompt.reply.dialog_pause' invalid."))

							reply_end_dialog = reply.get("end_dialog", False)
							if not isinstance(reply_end_dialog, bool):
								_errors.append(ValidationError("W", dialog_file, "Value 'prompt.reply.end_dialog' invalid."))
								reply_end_dialog = False

							if not reply_goto and not reply_end_dialog:
								_errors.append(ValidationError("E", dialog_file, f"Reply '{reply_name}' must have either a `goto` or have `end_dialog=true`."))
								continue

							if reply_name and reply_text:
								replies.append(Reply(
									reply_name,
									reply_text,
									reply_actions,
									reply_conditions,
									reply_goto,
									reply_dialog_pause,
									reply_end_dialog,
								))

					goto = prompt.get("goto", None)
					if not isinstance(goto, str | None) or (isinstance(goto, str) and not len(goto)):
						_errors.append(ValidationError("E", dialog_file, "Value 'prompt.reply_goto' missing or invalid."))

					show_separator = prompt.get("show_separator", True)
					if not isinstance(show_separator, bool):
						_errors.append(ValidationError("W", dialog_file, "Value 'prompt.reply.show_separator' invalid."))
						show_separator = True

					end_dialog = prompt.get("end_dialog", False)
					if not isinstance(end_dialog, bool):
						_errors.append(ValidationError("W", dialog_file, "Value 'prompt.end_dialog' invalid."))
						reply_end_dialog = False

					if not goto and not end_dialog and not len(replies):
						_errors.append(ValidationError("E", dialog_file, f"Prompt '{prompt_name}' must have either a `goto`, a list of replies, or have `end_dialog=true`."))
						continue

					if prompt_name and text:
						prompts.append(Prompt(prompt_name, text, replies, goto, show_separator, end_dialog))

			dialogs.append(Dialog(dialog_name, title, init_prompt, prompts))

		print(f"{len(dialogs)} dialogs!")
		return dialogs

	@staticmethod
	def __build_inventory_items(root_dir: str) -> list[InventoryItem]:
		print("Building items...")

		dir_path = os.path.join(root_dir, "items")
		item_files = [y for x in os.walk(dir_path) for y in glob(os.path.join(x[0], "*.toml"))]
		items = []
		for item_file in item_files:
			root_dir = os.path.dirname(item_file)
			data = GameBuilder.__read_file(item_file)
			if data == None: continue

			name = item_file.replace(".toml", "").split(DIR_SEPARATOR).pop()

			title = data.get("title", None)
			if not isinstance(title, str) or not len(title):
				_errors.append(ValidationError("E", item_file, "Value 'title' missing or invalid."))
			if len(title) > 30:
				_errors.append(ValidationError("E", item_file, "Value 'title' is over the maximum length (30)."))

			image_names = data.get("images", None)
			image_paths = []
			if not isinstance(image_names, list) or (isinstance(image_names, list) and not len(image_names)):
				_errors.append(ValidationError("E", item_file, "Value 'images' missing or invalid."))
			else:
				image_paths = list(map(lambda x: os.path.join(root_dir, x), image_names))
				for image_path in image_paths:
					if not os.path.exists(image_path):
						_errors.append(ValidationError("E", item_file, f"Item '{title}' image '{image_path}' does not exist."))

			pickup_message  = data.get("pickup_message", None)

			inventory_message = data.get("inventory_message", None)
			if not isinstance(inventory_message, str) or not len(inventory_message):
				_errors.append(ValidationError("W", item_file, "Value 'inventory_message' missing or invalid."))
			if len(inventory_message) > 200:
				_errors.append(ValidationError("E", item_file, "Value 'inventory_message' is over the maximum length (200)."))
			
			pickup_sound = data.get("pickup_sound", None)

			combos = []
			combo_list = data.get("combinations", None)
			if not isinstance(combo_list, list | None) or (isinstance(combo_list, list) and not len(combo_list)):
				_errors.append(ValidationError("E", item_file, "Value 'combinations' invalid."))
			elif isinstance(combo_list, list) and len(combo_list):
				for combo in combo_list:
					with_item = combo.get("with_item", None)
					if not isinstance(with_item, str) or not len(with_item):
						_errors.append(ValidationError("E", item_file, "Value 'combination.with_item' missing or invalid."))

					to_item = combo.get("to_item", None)
					if not isinstance(to_item, str) or not len(to_item):
						_errors.append(ValidationError("E", item_file, "Value 'combination.to_item' missing or invalid."))

					sound = combo.get("sound", None)
					if not isinstance(sound, str | None) or (isinstance(sound, str) and not len(sound)):
						_errors.append(ValidationError("E", item_file, "Value 'combination.sound' invalid."))

					if with_item and to_item:
						combos.append(ItemCombination(with_item, to_item, sound))

			inspect_actions = []
			inspect_actions_list = data.get("inspect_actions", None)
			if not isinstance(inspect_actions_list, list | None) or (isinstance(inspect_actions_list, list) and not len(inspect_actions_list)):
				_errors.append(ValidationError("E", item_file, "Value 'inspect_actions' invalid."))
			elif isinstance(inspect_actions_list, list) and len(inspect_actions_list):
				for inspect_action in inspect_actions_list:
					actions = GameBuilder.__build_actions(inspect_action, item_file, "inspect_action")
					conditions = GameBuilder.__build_conditions(inspect_action, item_file, "inspect_action")
					conditions_use_or = inspect_action.get("conditions_use_or", False)
					if not isinstance(conditions_use_or, bool):
						_errors.append(ValidationError("W", item_file, f"Value 'inspect_action.conditions_use_or' invalid."))
						conditions_use_or = False

					inspect_actions.append(InspectAction(actions, conditions, conditions_use_or))

			show_inspect = data.get("show_inspect", False)
			if not isinstance(show_inspect, bool):
				_errors.append(ValidationError("E", item_file, "Value 'show_inspect' invalid."))

			deconstruct_to = data.get("deconstruct_to", [])
			if not isinstance(deconstruct_to, list):
				_errors.append(ValidationError("E", item_file, "Value 'deconstruct_to' invalid."))
			else:
				for item in deconstruct_to:
					if not isinstance(item, str):
						_errors.append(ValidationError("E", item_file, f"Value 'deconstruct_to' invalid."))
						break

			deconstruct_label = data.get("deconstruct_label", "Take Apart")
			if not isinstance(deconstruct_label, str) or (isinstance(deconstruct_label, str) and len(deconstruct_to) > 15):
				_errors.append(ValidationError("E", item_file, "Value 'deconstruct_to' invalid."))

			if name and title and len(image_paths):
				images = []
				for image_path in image_paths:
					with open(image_path, "rb") as file:
						image = bytearray(file.read())
					images.append((os.path.basename(image_path), image))

				items.append(InventoryItem(
					name,
					title,
					images,
					pickup_message,
					inventory_message,
					pickup_sound,
					combos,
					inspect_actions,
					show_inspect,
					deconstruct_to,
					deconstruct_label,
				))
		
		print(f"{len(items)} items!")
		return items

	@staticmethod
	def __build_box(data: dict, filename: str, obj_name: str) -> tuple | None:
		box = data.get("box", None)
		if not isinstance(box, dict):
			_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box' for missing or invalid."))
			return None

		edge = box.get("edge", None)
		if edge != None:
			if edge not in [ "left", "right", "top", "bottom"]:
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.edge' invalid."))
				return None

			thickness = box.get("thickness", 0)
			if not isinstance(thickness, int) or thickness < 0 or thickness > SCENE_W or thickness > SCENE_H:
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.thickness' invalid."))
				return None

			if edge == "left": return (0, 0, thickness, SCENE_H)
			elif edge == "right": return (SCENE_W - thickness, 0, thickness, SCENE_H)
			elif edge == "top": return (0, 0, SCENE_W, thickness)
			elif edge == "bottom": return (0, SCENE_H - thickness, SCENE_W, thickness)

		else:
			x = box.get("x", None)
			if not isinstance(x, int):
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.x' missing or invalid."))
				return None
			elif x < 0 or x > SCENE_W:
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.x' out of bounds (must be less than {SCENE_W})."))
				return None

			y = box.get("y", None)
			if not isinstance(y, int):
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.y' missing or invalid."))
				return None
			elif y < 0 or y > SCENE_H:
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.y' out of bounds (must be less than {SCENE_H})."))
				return None

			width = box.get("width", None)
			if not isinstance(width, int):
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.width' missing or invalid."))
				return None
			elif width < 0 or width > SCENE_W - x:
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.width' out of bounds (must be less than {SCENE_W})."))
				return None

			height = box.get("height", None)
			if not isinstance(height, int):
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.height' missing or invalid."))
				return None
			elif height < 0 or height > SCENE_H - y:
				_errors.append(ValidationError("E", filename, f"Value '{obj_name}.box.height' out of bounds (must be less than {SCENE_H})."))
				return None

			return (x, y, width, height)

	@staticmethod
	def __read_file(file_path: str)-> dict | None:
		try:
			with open(file_path, "rb") as file:
				data = tomllib.load(file)
			return data
		except Exception as ex:
			_errors.append(ValidationError("E", file_path, f"Error reading TOML file: {ex}"))
			return None
	
	@staticmethod
	def __build_scene_actions(data: dict, filename: str, obj_name: str, scene_name: str) -> list[SceneAction]:
		scene_actions = []
		scene_actions_list = data.get("scene_actions", [])
		if not isinstance(scene_actions_list, list):
			_errors.append(ValidationError("E", filename, f"Value '{obj_name}' invalid."))
		elif len(scene_actions_list):
			for scene_action in scene_actions_list:
				scene_actions_name = scene_action.get("name", None)
				if not isinstance(scene_actions_name, str) or not len(scene_actions_name):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.scene_action.name' missing or invalid."))

				repeat = scene_action.get("repeat", None)
				if not isinstance(repeat, bool):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.scene_action.repeat' missing or invalid."))

				actions = GameBuilder.__build_actions(scene_action, filename, "scene_action", True)

				conditions = GameBuilder.__build_conditions(scene_action, filename, "scene_action")

				conditions_use_or = scene_action.get("conditions_use_or", False)
				if not isinstance(conditions_use_or, bool):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.scene_action.conditions_use_or' invalid."))
					conditions_use_or = False

				if scene_actions_name and actions:
					scene_actions.append(SceneAction(
						f"{scene_name}_{scene_actions_name}",
						repeat,
						actions,
						conditions,
						conditions_use_or,
					))

		return scene_actions

	@staticmethod
	def __build_scene_items(data: dict, filename: str, obj_name: str, inventory_items: list[InventoryItem]) -> list[SceneItem]:
		items = []
		item_list = data.get("items", [])
		if not isinstance(item_list, list):
			_errors.append(ValidationError("E", filename, f"Value '{obj_name}' invalid."))
		elif len(item_list):
			for item in item_list:
				item_name = item.get("name", None)
				if not isinstance(item_name, str) or not len(item_name):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.name' missing or invalid."))
				
				box = GameBuilder.__build_box(item, filename, f"{obj_name}.item")

				item_image = item.get("image", None)
				if not isinstance(item_image, str) or not len(item_image):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.item_image' missing or invalid."))

				inventory_item = next((x for x in inventory_items if x.name == item_name), None)
				if not inventory_item:
					_errors.append(ValidationError("E", filename, f"Value '{item_name}' for '{obj_name}.item' not a valid item."))

				if inventory_item:
					image_file_names = [x[0] for x in inventory_item.images]
					image_name = next((x for x in image_file_names if x.endswith(item["image"])), None)
					if not image_name:
						_errors.append(ValidationError("E", filename, f"Item for '{obj_name}' '{item_name}' does not have image '{item_image}'."))
				else:
					image_name = None

				can_pick_up = item.get("can_pick_up", True)
				if not isinstance(can_pick_up, bool):
					_errors.append(ValidationError("W", filename, "Value 'can_pick_up' invalid."))
					can_pick_up = True
			
				if box and inventory_item and image_name:
					x, y, width, height = box
					image = next(x for x in inventory_item.images if x[0] == image_name)[1]
					items.append(SceneItem(
						x,
						y,
						width,
						height,
						item_name,
						image,
						inventory_item.pickup_message,
						inventory_item.pickup_sound,
						can_pick_up,
					))

		return items

	@staticmethod
	def __build_actions(data: dict, filename: str, obj_name: str, needs_scene_refresh: bool = False) -> list[Action]:
		actions = []
		action_list = data.get("actions", [])
		if not isinstance(action_list, list):
			_errors.append(ValidationError("E", filename, f"Value '{obj_name}.actions' invalid."))
		elif len(action_list):
			for action in action_list:
				type = action.get("type", None)
				if type not in Action.types:
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.type' '{type}' invalid."))

				key = action.get("key", None)
				if not isinstance(key, str | None) or (isinstance(key, str) and not len(key)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.key' '{key}' invalid."))

				value = action.get("value", None)
				if not isinstance(value, bool | int | str | None) or (isinstance(value, str) and not len(value)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.value' '{value}' invalid."))

				params = action.get("params", None)
				if not isinstance(params, list | None) or (isinstance(params, list) and not len(params)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' '{params}' invalid."))
				elif params != None and len(params):
					for param in params:
						if not isinstance(param, bool | int | str | None) or (isinstance(param, str) and not len(param)):
							_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' '{param}' invalid."))
							break
					if type not in [ACTION_UPDATE_RANDOM, ACTION_TRANSITION_SCENE, ACTION_START_ANIMATION, ACTION_SHOW_MESSAGE, ACTION_END_GAME]:
						_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' not used for Action Type '{type}'."))
					elif type == ACTION_UPDATE_RANDOM:
						if len(params) != 2:
							_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' invalid."))
						else:
							for param in params:
								if not isinstance(param, int):
									_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' invalid."))
									break
					elif type == ACTION_TRANSITION_SCENE:
						if len(params) == 1:
							params.append("fast")
						if len(params) > 2 \
							or params[0] not in SceneTransition.types \
							or params[1] not in ["slow", "fast"]:
							_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' invalid."))
					elif type == ACTION_START_ANIMATION:
						if 5 < len(params) > 7:
							_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' invalid."))
						else:
							if len(params) == 5: params.append(255)
							if len(params) == 6: params.append(False)
							# Hack to get animations from scene_actions working, only these require the scene to be refreshed
							params.append(needs_scene_refresh)
							x, y, width, height, duration, alpha, hold_final_frame, _ = params
							if not isinstance(x, int) or (isinstance(x, int) and 0 >= x > 576) \
								or not isinstance(y, int) or (isinstance(y, int) and 0 >= y > 320) \
								or not isinstance(width, int) or (isinstance(width, int) and 0 >= width + x > 320) \
								or not isinstance(height, int) or (isinstance(height, int) and 0 >= height + y > 320) \
								or not isinstance(duration, int) or (isinstance(duration, int) and duration <= 0) \
								or not isinstance(alpha, int) or (isinstance(alpha, int) and 0 >= alpha > 255 ) \
								or not isinstance(hold_final_frame, bool | None):
								_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' invalid."))
					elif type == ACTION_SHOW_MESSAGE:
						if not value and not params:
							_errors.append(ValidationError("E", filename, f"Action 'show_message' invalid, requires either `value` or `params`."))
						if params:
							for param in params:
								if not isinstance(param, str):
									_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' '{str(param)}' invalid, params must be a str[]."))
									break
					elif type == ACTION_END_GAME:
						if params:
							for param in params:
								if not isinstance(param, str):
									_errors.append(ValidationError("E", filename, f"Value '{obj_name}.action.params' '{str(param)}' invalid, params must be a str[]."))
									break

				conditions = GameBuilder.__build_conditions(action, filename, "action")

				conditions_use_or = action.get("conditions_use_or", False)
				if not isinstance(conditions_use_or, bool):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.action.conditions_use_or' invalid."))
					conditions_use_or = False

				if type:
					actions.append(Action(type, key, value, params, conditions, conditions_use_or))

		return actions

	@staticmethod
	def __build_conditions(data: dict, filename: str, obj_name: str, prop_name: str = "conditions") -> list[Condition]:
		conditions = []
		condition_list = data.get(prop_name, [])
		if not isinstance(condition_list, list):
			_errors.append(ValidationError("E", filename, "Value 'interactions.conditions' invalid."))
		elif len(condition_list):
			for condition in condition_list:
				type = condition.get("type", None)
				if type not in Condition.types:
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.condition.type' '{type}' invalid."))

				key = condition.get("key", None)
				if not isinstance(key, str | None) or (isinstance(key, str) and not len(key)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.condition.key' '{key}' invalid."))

				value = condition.get("value", None)
				if not isinstance(value, bool | int | str | None) or (isinstance(value, str) and not len(value)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.condition.value' '{value}' invalid."))

				negate = condition.get("negate", False)
				if not isinstance(negate, bool):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.condition.negate' '{negate}' invalid."))

				if type:
					conditions.append(Condition(type, key, value, negate))

		return conditions

	@staticmethod
	def __build_interactions(data: dict, filename: str, obj_name: str) -> list[Interaction]:
		interactions = []
		interaction_list = data.get("interactions", [])
		if not isinstance(interaction_list, list):
			_errors.append(ValidationError("E", filename, f"Value '{obj_name}.interactions' invalid."))
		elif len(interaction_list):
			for interaction in interaction_list:
				box = GameBuilder.__build_box(interaction, filename, "interaction")

				message = interaction.get("message", None)
				if not isinstance(message, str | list | None) or (isinstance(message, str | list) and not len(message)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.interaction.message' invalid."))
				elif isinstance(message, list):
					for x in message:
						if not isinstance(x, str):
							_errors.append(ValidationError("E", filename, f"Value '{obj_name}.interaction.message' invalid."))
							break

				actions = GameBuilder.__build_actions(interaction, filename, "interaction")

				conditions = GameBuilder.__build_conditions(interaction, filename, "interaction")

				conditions_use_or = interaction.get("conditions_use_or", False)
				if not isinstance(conditions_use_or, bool):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.interaction.conditions_use_or' invalid."))
					conditions_use_or = False

				if box and (message or len(actions)):
					x, y, width, height = box
					interactions.append(Interaction(
						x,
						y,
						width,
						height,
						message,
						actions,
						conditions,
						conditions_use_or,
					))

		return interactions

	@staticmethod
	def __build_navs(data: dict, filename: str, obj_name: str) -> list[Navigation]:
		navs = []
		nav_list = data.get("navs", [])
		if not isinstance(nav_list, list):
			_errors.append(ValidationError("E", filename, f"Value '{obj_name}.navs' invalid."))
		elif len(nav_list):
			for nav in nav_list:
				box = GameBuilder.__build_box(nav, filename, f"{obj_name}.nav")

				to_scene_name = nav.get("to_scene_name", None)
				if not isinstance(to_scene_name, str) or (isinstance(to_scene_name, str) and not len(to_scene_name)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.nav.to_scene_name' invalid."))

				sound = nav.get("sound", None)
				if not isinstance(sound, str | None) or (isinstance(sound, str) and not len(sound)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.nav.sound' invalid."))

				transition = nav.get("transition", None)
				if not isinstance(transition, str | None) or (isinstance(transition, str) and not len(transition)):
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.nav.transition' invalid."))
				elif transition != None and transition not in SceneTransition.types:
					_errors.append(ValidationError("E", filename, f"Value '{obj_name}.nav.transition' '{transition}' is not a valid transition."))

				transition_speed = nav.get("transition_speed", None)
				if not isinstance(transition_speed, str | None) or (isinstance(transition_speed, str) and transition_speed not in ["slow", "fast"]):
					_errors.append(ValidationError("W", filename, f"Value '{obj_name}.nav.transition_speed' invalid."))
				if transition_speed != "slow":
					transition_speed = "fast"

				if box and to_scene_name:
					x, y, width, height = box
					navs.append(Navigation(x, y, width, height, to_scene_name, sound, transition, transition_speed))

		return navs

	@staticmethod
	def __build_theme(data: dict, filename: str, root_dir: str) -> Theme:
		print("Building theme...")

		theme_dict = data.get("theme", None)
		if not isinstance(theme_dict, dict) and theme_dict != None:
			_errors.append(ValidationError("E", filename, "Value 'theme' invalid."))
		elif theme_dict == None:
			_errors.append(ValidationError("W", filename, "Value 'theme' missing."))
			theme_dict = dict()

		img_dir = os.path.join(root_dir, "img")

		game_bg_color  = GameBuilder.__get_color(theme_dict, "game_bg_color", filename, DEFAULT_BG_COLOR)
		game_bg_image = GameBuilder.__get_theme_image(theme_dict, "game_bg_image", filename, img_dir)

		main_menu_bg_color = GameBuilder.__get_color(theme_dict, "main_menu_bg_color", filename, game_bg_color)
		main_menu_bg_image = GameBuilder.__get_theme_image(theme_dict, "main_menu_bg_image", filename, img_dir)
		main_menu_title_inline = theme_dict.get("main_menu_title_inline", DEFAULT_TITLE_INLINE)
		if not isinstance(main_menu_title_inline, bool):
			_errors.append(ValidationError("W", filename, f"Value 'main_menu_title_inline' in 'theme' invalid. Must be a boolean."))
		main_menu_titlebar_style = GameBuilder.__get_menubar_style(theme_dict, "main_menu_titlebar_style", filename, DEFAULT_TITLEBAR_STYLE)
		main_menu_title_bg_color = GameBuilder.__get_color(theme_dict, "main_menu_title_bg_color", filename, DEFAULT_TITLE_BG_COLOR)
		main_menu_title_font_color = GameBuilder.__get_color(theme_dict, "main_menu_title_font_color", filename, DEFAULT_TITLE_FONT_COLOR)
		main_menu_title_font = GameBuilder.__get_font(theme_dict, "main_menu_title_font", filename, DEFAULT_TITLE_FONT)
		main_menu_font_color = GameBuilder.__get_color(theme_dict, "main_menu_font_color", filename, DEFAULT_WIDGET_FONT_COLOR)
		main_menu_font = GameBuilder.__get_font(theme_dict, "main_menu_font", filename, DEFAULT_TITLE_FONT)

		game_controls_bg_color = GameBuilder.__get_color(theme_dict, "game_controls_bg_color", filename, main_menu_bg_color)
		game_controls_bg_image = GameBuilder.__get_theme_image(theme_dict, "game_controls_bg_image", filename, img_dir)
		game_controls_font_color = GameBuilder.__get_color(theme_dict, "game_controls_font_color", filename, main_menu_font_color)
		game_controls_font = GameBuilder.__get_font(theme_dict, "game_controls_font", filename, main_menu_font)

		pause_menu_bg_color = GameBuilder.__get_color(theme_dict, "pause_menu_bg_color", filename, main_menu_bg_color)
		pause_menu_bg_image = GameBuilder.__get_theme_image(theme_dict, "pause_menu_bg_image", filename, img_dir)
		pause_menu_titlebar_style = GameBuilder.__get_menubar_style(theme_dict, "pause_menu_titlebar_style", filename, main_menu_titlebar_style)
		pause_menu_title_bg_color = GameBuilder.__get_color(theme_dict, "pause_menu_title_bg_color", filename, main_menu_title_bg_color)
		pause_menu_title_font_color = GameBuilder.__get_color(theme_dict, "pause_menu_title_font_color", filename, main_menu_title_font_color)
		pause_menu_title_font = GameBuilder.__get_font(theme_dict, "pause_menu_title_font", filename, main_menu_title_font)
		pause_menu_font_color = GameBuilder.__get_color(theme_dict, "pause_menu_font_color", filename, main_menu_font_color)
		pause_menu_font = GameBuilder.__get_font(theme_dict, "pause_menu_font", filename, main_menu_font)

		dialog_bg_color = GameBuilder.__get_color(theme_dict, "dialog_bg_color", filename, main_menu_bg_color)
		dialog_bg_image = GameBuilder.__get_theme_image(theme_dict, "dialog_bg_image", filename, img_dir)
		dialog_titlebar_style = GameBuilder.__get_menubar_style(theme_dict, "dialog_titlebar_style", filename, main_menu_titlebar_style)
		dialog_title_bg_color = GameBuilder.__get_color(theme_dict, "dialog_title_bg_color", filename, main_menu_title_bg_color)
		dialog_title_font_color = GameBuilder.__get_color(theme_dict, "dialog_title_font_color", filename, main_menu_title_font_color)
		dialog_title_font = GameBuilder.__get_font(theme_dict, "dialog_title_font", filename, main_menu_title_font)
		dialog_font_color = GameBuilder.__get_color(theme_dict, "dialog_font_color", filename, main_menu_font_color)
		dialog_font_color_alt = GameBuilder.__get_color(theme_dict, "dialog_font_color_alt", filename, Theme.darken_color(main_menu_font_color))
		dialog_font = GameBuilder.__get_font(theme_dict, "dialog_font", filename, main_menu_font)

		inventory_bg_color = GameBuilder.__get_color(theme_dict, "inventory_bg_color", filename, main_menu_bg_color)
		inventory_bg_color_alt = GameBuilder.__get_color(theme_dict, "inventory_bg_color_alt", filename, Theme.darken_color(inventory_bg_color))
		inventory_bg_image = GameBuilder.__get_theme_image(theme_dict, "inventory_bg_image", filename, img_dir)
		inventory_title_bg_color = GameBuilder.__get_color(theme_dict, "inventory_title_bg_color", filename, main_menu_title_bg_color)
		inventory_title_font_color = GameBuilder.__get_color(theme_dict, "inventory_title_font_color", filename, main_menu_title_font_color)
		inventory_title_font = GameBuilder.__get_font(theme_dict, "inventory_title_font", filename, main_menu_title_font)
		inventory_font_color = GameBuilder.__get_color(theme_dict, "inventory_font_color", filename, main_menu_font_color)
		inventory_font = GameBuilder.__get_font(theme_dict, "inventory_font", filename, main_menu_font)

		cursors = GameBuilder.__build_cursor_set(theme_dict, filename, img_dir)

		return Theme(
			game_bg_color,
			game_bg_image,
			main_menu_bg_color,
			main_menu_bg_image,
			main_menu_title_inline,
			main_menu_titlebar_style,
			main_menu_title_bg_color,
			main_menu_title_font_color,
			main_menu_title_font,
			main_menu_font_color,
			main_menu_font,
			game_controls_bg_color,
			game_controls_bg_image,
			game_controls_font_color,
			game_controls_font,
			pause_menu_bg_color,
			pause_menu_bg_image,
			pause_menu_titlebar_style,
			pause_menu_title_bg_color,
			pause_menu_title_font_color,
			pause_menu_title_font,
			pause_menu_font_color,
			pause_menu_font,
			dialog_bg_color,
			dialog_bg_image,
			dialog_titlebar_style,
			dialog_title_bg_color,
			dialog_title_font_color,
			dialog_title_font,
			dialog_font_color,
			dialog_font_color_alt,
			dialog_font,
			inventory_bg_color,
			inventory_bg_color_alt,
			inventory_bg_image,
			inventory_title_bg_color,
			inventory_title_font_color,
			inventory_title_font,
			inventory_font_color,
			inventory_font,
			cursors,
		)

	@staticmethod
	def __build_translations(root_dir: str) -> dict[str, dict[str, str]]:
		print("Building translations...")

		translations = dict()
		translation_count = 0

		dir_path = os.path.join(root_dir, "translations")
		if not os.path.exists(dir_path):
			return translations

		translation_files = [y for x in os.walk(dir_path) for y in glob(os.path.join(x[0], "*.toml"))]

		for translation_file in translation_files:
			data = GameBuilder.__read_file(translation_file)
			if (isinstance(data, dict)):
				for string_key, translation_dict in data.items():
					if not isinstance(translation_dict, dict):
						_errors.append(ValidationError("W", translation_file, f"Value '{string_key}' is not a valid translation."))
					else:
						for locale_key, translation in translation_dict.items():
							if not isinstance(translation, str):
								_errors.append(ValidationError("W", translation_file, f"Value '{string_key}.{locale_key}' is not a valid translation."))
							else:
								if string_key not in translations:
									translations[string_key] = dict()
								translations[string_key][locale_key] = translation
								translation_count += 1

		print(f"{len(translations.keys())} strings with {translation_count} translations!")
		return translations

	@staticmethod
	def __get_color(theme_dict: dict, key: str, filename: str, default: tuple) -> tuple:
		value = theme_dict.get(key, None)
		if value == None:
			return default
		if not isinstance(value, list) or (isinstance(value, list) and (len(value) < 3 or len(value) > 4)):
			_errors.append(ValidationError("W", filename, f"Value '{key}' in 'theme' invalid. Must be an array of length 3 or 4."))
			return default
		for x in value:
			if not isinstance(x, int) or (isinstance(x, int) and (x < 0 or x > 255)):
				_errors.append(ValidationError("W", filename, f"Value '{key}' in 'theme' invalid. Must be an array of integers, range 0-255."))
				return default
		return tuple(value)

	@staticmethod
	def __get_font(theme_dict: dict, key: str, filename: str, default: str) -> str:
		value = theme_dict.get(key, None)
		if value == None:
			return default
		if value not in Theme.fonts:
			try:
				pygame_menu.font.get_font(value, 1)
			except:
				_errors.append(ValidationError("W", filename, f"Value '{key}' in 'theme' not a valid font."))
				return default
		return value

	@staticmethod
	def __get_menubar_style(theme_dict: dict, key: str, filename: str, default: str) -> str:
		value = theme_dict.get(key, None)
		if value != None and isinstance(value, str) and value not in Theme.menubar_styles:
			_errors.append(ValidationError("W", filename, f"Value '{key}' in 'theme' not a valid MENUBAR_STYLE."))
			return default
		return value

	@staticmethod
	def __build_cursor_set(theme_dict: dict, filename: str, img_dir: str) -> CursorSet:
		cursor_default = theme_dict.get("cursor_default", DEFAULT_CURSOR_DEFAULT)
		if not isinstance(cursor_default, str) or (isinstance(cursor_default, str) and not len(cursor_default)):
			_errors.append(ValidationError("W", filename, f"Value 'cursor_default' in 'theme' invalid."))
		if not cursor_default.startswith("SYSTEM"):
			cursor_default = os.path.join(img_dir, cursor_default)
			if not os.path.exists(cursor_default):
				_errors.append(ValidationError("W", filename, f"Image '{cursor_default}' for 'cursor_default' in 'theme' does not exist."))

		cursor_hover = theme_dict.get("cursor_hover", DEFAULT_CURSOR_HOVER)
		if not isinstance(cursor_hover, str) or (isinstance(cursor_hover, str) and not len(cursor_hover)):
			_errors.append(ValidationError("W", filename, f"Value 'cursor_hover' in 'theme' invalid."))
		if not cursor_hover.startswith("SYSTEM"):
			cursor_hover = os.path.join(img_dir, cursor_hover)
			if not os.path.exists(cursor_hover):
				_errors.append(ValidationError("W", filename, f"Image '{cursor_hover}' for 'cursor_hover' in 'theme' does not exist."))

		cursor_click = theme_dict.get("cursor_click", DEFAULT_CURSOR_CLICK)
		if not isinstance(cursor_click, str) or (isinstance(cursor_click, str) and not len(cursor_click)):
			_errors.append(ValidationError("W", filename, f"Value 'cursor_click' in 'theme' invalid."))
		if not cursor_click.startswith("SYSTEM"):
			cursor_click = os.path.join(img_dir, cursor_click)
			if not os.path.exists(cursor_click):
				_errors.append(ValidationError("W", filename, f"Image '{cursor_click}' for 'cursor_click' in 'theme' does not exist."))

		cursor_size = theme_dict.get("cursor_size", 32)
		if not isinstance(cursor_size, int) or (isinstance(cursor_size, int) and (cursor_size < 1 or cursor_size >= 200)):
			_errors.append(ValidationError("E", filename, f"Value 'cursor_size' invalid, must be between 0 and 200."))

		return CursorSet(cursor_default, cursor_hover, cursor_click, cursor_size)

	@staticmethod
	def __get_theme_image(theme_dict: dict, key: str, filename: str, img_dir: str) -> bytearray | None:
		file_name = theme_dict.get(key, None)
		if file_name == None: return None
		if not isinstance(file_name, str) or (isinstance(file_name, str) and not len(file_name)):
			_errors.append(ValidationError("W", filename, f"Value '{key}' in 'theme' invalid."))
			return None
		file_path = os.path.join(img_dir, file_name)
		if not os.path.exists(file_path):
			_errors.append(ValidationError("W", filename, f"Image '{file_path}' for '{key}' in 'theme' does not exist."))
			return None

		with open(file_path, "rb") as file:
			data = bytearray(file.read())

		return data

	@staticmethod
	def __unpack_gif(image_path: str) -> AnimationFrames:
		frames = AnimationFrames(os.path.basename(image_path))
		with Image.open(image_path) as file:
			for frame in ImageSequence.Iterator(file):
				has_white = False

				frame = frame.convert("RGBA")
				frame.apply_transparency()

				for x in range(frame.width):
					if has_white: break
					for y in range(frame.height):
						pixel = frame.getpixel((x, y))
						if isinstance(pixel, tuple):
							if (pixel[0], pixel[1], pixel[2]) == (255, 255, 255):
								has_white = True
								break

				frames.append(AnimationFrame(frame.tobytes(), frame.size, has_white))

		return frames

	@staticmethod
	def __get_icon_image(assets_dir: str) -> bytearray | None:
		icon_files = glob(os.path.join(assets_dir, "icon.*"))
		icon_file = icon_files[0] if len(icon_files) > 0 else None
		if not icon_file:
			return None
		else:
			with open(icon_file, "rb") as file:
				data = bytearray(file.read())
			return data
