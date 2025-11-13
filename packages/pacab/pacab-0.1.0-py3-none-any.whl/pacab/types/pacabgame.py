import sys

from pacab.types.animationframes import AnimationFrames
from pacab.types.dialog import Dialog
from pacab.types.inventoryitem import InventoryItem
from pacab.types.scene import Scene
from pacab.types.theme import Theme


class PacabGame:
	def __init__(
			self,
			name: str,
			short_name: str,
			init_scene_name: str,
			start_game_message: str | list[str] | None,
			init_items: list[str],
			icon: bytearray | None,
			theme: Theme,
			scenes: list[Scene],
			translations: dict[str, dict[str, str]],
			items: list[InventoryItem],
			animation_frames: list[AnimationFrames],
			dialogs: list[Dialog],
			game_globals: dict,
			audio_files: list[tuple[str, bytearray]],
			debug_mode: bool,
		) -> None:
		self.name = name
		self.short_name = short_name
		self.init_scene_name = init_scene_name
		self.start_game_message = start_game_message
		self.init_items = init_items
		self.icon = icon
		self.theme = theme
		self.scenes = scenes
		self.translations = translations
		self.items = items
		self.animation_frames = animation_frames
		self.dialogs = dialogs
		self.game_globals = game_globals
		self.audio_files = audio_files
		self.debug_mode = debug_mode

	def get_animation_frames(self, filename: str) -> AnimationFrames:
		for animation_frames in self.animation_frames:
			if animation_frames.filename == filename:
				return animation_frames
		sys.exit(f"Error loading animation '{filename}'!")

	def get_dialog(self, dialog_name: str) -> Dialog:
		for dialog in self.dialogs:
			if dialog.name == dialog_name:
				return dialog
		sys.exit(f"Error loading dialog '{dialog_name}'!")

	def get_item(self, item_name: str) -> InventoryItem:
		for item in self.items:
			if item.name == item_name:
				return item
		sys.exit(f"Error loading item '{item_name}'!")

	def get_scene(self, scene_name: str) -> Scene:
		for scene in self.scenes:
			if scene.name == scene_name:
				return scene
		sys.exit(f"Error loading scene '{scene_name}'!")
