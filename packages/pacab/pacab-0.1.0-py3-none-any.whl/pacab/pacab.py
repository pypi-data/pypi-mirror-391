import io
from copy import copy
from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

from pacab.actionrunner import ActionRunner
from pacab.audio import Audio
from pacab.constants import *
from pacab.dialogrunner import DialogRunner
from pacab.displayinfo import DisplayInfo
from pacab.gamestate import GameState
from pacab.logger import Logger
from pacab.menus.dialogmenu import DialogMenu
from pacab.menus.gamecontrolsmenu import GameControlsMenu
from pacab.menus.inventorymenu import InventoryMenu
from pacab.menus.mainmenu import MainMenu
from pacab.menus.pausemenu import PauseMenu
from pacab.options import Options
from pacab.surfaces.animationsurface import AnimationSurface
from pacab.surfaces.interactionsurface import InteractionSurface
from pacab.surfaces.itemsurface import ItemSurface
from pacab.surfaces.navsurface import NavSurface
from pacab.surfaces.overlaysurface import OverlaySurface
from pacab.surfaces.scenesurface import SceneSurface
from pacab.surfaces.transitionsurface import TransitionSurface
from pacab.text import Text, get_string as _
from pacab.types.animation import Animation
from pacab.types.condition import Condition
from pacab.types.inventoryitem import InventoryItem
from pacab.types.pacabgame import PacabGame
from pacab.types.prompt import Prompt
from pacab.types.scene import Scene
from pacab.types.sceneaction import SceneAction
from pacab.types.scenetransition import SceneTransition


class Pacab:
	def __init__(self, pacab_game: PacabGame) -> None:
		pygame.init()
		pygame.font.init()

		if pacab_game.debug_mode:
			Logger.print_logs = True

		self.__program_state = PROG_STATE_MAINMENU
		self.__pacab_game = pacab_game
		Text.init(self.__pacab_game.translations)
		self.__audio = Audio(self.__pacab_game.audio_files)
		self.__clock = pygame.time.Clock()
		self.__is_input_blocked = False
		self.__is_dialog_timeout = False
		self.__is_mouse_in_game_bounds = False
		self.__transition_surface: TransitionSurface | None = None
		self.__queued_animations = []
		self.__prev_dialog_timeout = 0

		pygame.display.set_caption(pacab_game.name)

		self.__display_info = DisplayInfo()
		self.__window = pygame.display.set_mode(
			(self.__display_info.window.width, self.__display_info.window.height),
			pygame.FULLSCREEN|pygame.NOFRAME|pygame.HWSURFACE|pygame.SCALED,
			display=0,
		)
		self.__screen = pygame.Surface((self.__display_info.window.width, self.__display_info.window.height))

		if pacab_game.icon:
			pygame.display.set_icon(pygame.image.load(io.BytesIO(pacab_game.icon)).convert_alpha())

		self.__pacab_game.theme.cursors.init_cursors()
		self.__set_cursor("default")
		self.__bg_image = pygame.image.load(io.BytesIO(self.__pacab_game.theme.game_bg_image)).convert_alpha() \
			if self.__pacab_game.theme.game_bg_image else None

		self.__main_menu = MainMenu(self.__pacab_game, self.__display_info, self.__new_game)
		self.__dialog_menu: DialogMenu | None = None
		self.__game_controls_menu = GameControlsMenu(self.__pacab_game, self.__display_info, self.__get_game_state)
		self.__inventory_menu = InventoryMenu(self.__pacab_game, self.__display_info, self.__get_game_state)
		self.__pause_menu = PauseMenu(self.__pacab_game, self.__display_info, self.__get_game_state)

		self.__item_surfaces = pygame.sprite.Group()
		self.__nav_surfaces = pygame.sprite.Group()
		self.__overlay_surfaces = pygame.sprite.Group()
		self.__interaction_surfaces = pygame.sprite.Group()
		self.__animation_surfaces = pygame.sprite.Group()
		self.__all_sprites = pygame.sprite.Group()

	def run(self) -> None:
		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == UPDATE_PROGRAM_STATE:
					self.__program_state = event.dict["state"]
				elif event.type == pygame.VIDEORESIZE:
					self.__redo_layout()

			if self.__main_menu.is_enabled():
				self.__main_menu.draw(self.__window)
				self.__main_menu.update(events)

			pygame.display.update()

	def __new_game(self, game_state: GameState | None = None) -> None:
		is_loading = True if game_state else False
		Logger.log(f"{"Loading" if is_loading else "Starting"} game")

		self.game_state = game_state if game_state else GameState.new_game_state(self.__pacab_game.init_scene_name, self.__pacab_game.game_globals)
		self.__program_state = PROG_STATE_GAME

		if not is_loading:
			if self.__pacab_game.init_items:
				for item in self.__pacab_game.init_items:
					self.game_state.items.append(item)

		self.__change_scene(self.game_state.scene_name)

		self.__audio.set_options(
			Options.load_options(self.__pacab_game.short_name),
			self.scene.music,
			self.scene.music_2,
			self.scene.music_2_loops,
			self.scene.music_2_repeat,
			self.game_state.dead_music_2,
			self.game_state,
			self.scene,	
		)

		if not is_loading and self.__pacab_game.start_game_message:
			pygame.event.post(pygame.event.Event(DIALOG_FROM_STR, { "text": self.__pacab_game.start_game_message, "timeout": None }))

		self.__run_game()

	def __redo_layout(self) -> None:
		inv_selected_item = None

		# Before resizing, Pause/Inventory menus must be closed
		if self.__is_state_paused():
			self.__pause_menu.disable()
		elif self.__is_state_inventory():
			inv_selected_item = self.__inventory_menu.selected_item
			self.__inventory_menu.disable()

		# Resize
		self.__display_info = DisplayInfo()
		self.__screen = pygame.Surface((self.__display_info.window.width, self.__display_info.window.height))
		self.__main_menu = MainMenu(self.__pacab_game, self.__display_info, self.__new_game)
		self.__game_controls_menu = GameControlsMenu(self.__pacab_game, self.__display_info, self.__get_game_state)
		self.__inventory_menu = InventoryMenu(self.__pacab_game, self.__display_info, self.__get_game_state)
		self.__pause_menu = PauseMenu(self.__pacab_game, self.__display_info, self.__get_game_state)
		
		# After resizing, check program state to re-open any menus. If on the Main Menu, no extra steps are needed.
		if self.__program_state == PROG_STATE_LOADMENU:
			self.__main_menu.load_game_button.apply()

		elif self.__program_state == PROG_STATE_OPTIONSMENU:
			self.__main_menu.options_button.apply()

		elif self.__is_state_gameplay():
			self.__main_menu.disable()

			if hasattr(self, "scene_surface"): self.scene_surface.kill()
			self.scene_surface = SceneSurface(self.scene, self.__display_info)
			self.__all_sprites.add(self.scene_surface)

			# Animations have a lot of data and don't take well to being `copy()`d.
			# This resets the x/y/w/h on the animations so that it can get re-scaled against the new resolution.
			animations = self.scene.animations
			if self.scene.overlays:
				for overlay in self.scene.overlays:
					animations = overlay.animations + animations
			if animations:
				for animation in animations:
					animation.reset()

			self.__refresh_scene()

			if self.__is_state_paused():
				self.__pause_menu.enable()
				if self.__program_state == PROG_STATE_SAVEMENU:
					self.__pause_menu.save_button.apply()
				elif self.__program_state == PROG_STATE_PAUSEOPTIONS:
					self.__pause_menu.options_button.apply()
			elif self.__is_state_inventory():
				self.__inventory_menu.enable()
				self.__inventory_menu.refresh()
				if inv_selected_item:
					self.__inventory_menu.select_item(self.__pacab_game.get_item(inv_selected_item))
				if self.__program_state == PROG_STATE_INVINSPECT:
					self.__inventory_menu.inspect_button.apply()

	def __run_game(self) -> None:
		time_ms_last_frame = 0
		self.__running = True
		while self.__running:
			self.__handle_events()
			self.__update_surfaces(time_ms_last_frame)
			self.__paint()
			time_ms_last_frame = self.__clock.tick(FPS) / 1000
		self.__audio.stop_music()
		if self.scene.music_2: self.__audio.stop_music_2(self.scene.music_2)
	
	def __change_scene(self, scene_name: str, transition_animation_surfaces: pygame.sprite.Group | None = None) -> None:
		Logger.log(f"Changing Scene to '{scene_name}'")

		cur_scene = self.__pacab_game.get_scene(self.game_state.scene_name)
		new_scene = self.__pacab_game.get_scene(scene_name)
		self.__update_song(cur_scene, new_scene, self.game_state)

		self.game_state.scene_name = scene_name
		self.scene = new_scene
		
		if hasattr(self, "scene_surface"): self.scene_surface.kill()
		self.scene_surface = SceneSurface(self.scene, self.__display_info)
		self.__all_sprites.empty()
		self.__all_sprites.add(self.scene_surface)
		self.__refresh_scene(transition_animation_surfaces)
		self.__execute_scene_actions(self.scene.scene_actions)

	def __refresh_scene(self, transition_animation_surfaces: pygame.sprite.Group | None = None) -> None:
		# Surfaces with images in them need to be killed
		for overlay_surface in self.__overlay_surfaces: overlay_surface.kill()
		for item_surface in self.__item_surfaces: item_surface.kill()
		for animation_surface in self.__animation_surfaces: animation_surface.kill()
		# ... then we can empty the Sprite Groups
		self.__overlay_surfaces.empty()
		self.__nav_surfaces.empty()
		self.__item_surfaces.empty()
		self.__interaction_surfaces.empty()
		self.__animation_surfaces.empty()

		navs = self.scene.navs
		items = self.scene.items
		interactions = self.scene.interactions
		animations = self.scene.animations if not transition_animation_surfaces else []

		if self.scene.overlays:
			for overlay in self.scene.overlays:
				if overlay.should_show(self.game_state):
					self.__overlay_surfaces.add(OverlaySurface(copy(overlay), self.__display_info, self.__pacab_game))
					navs = overlay.navs + navs
					items = overlay.items + items
					interactions = overlay.interactions + interactions
					animations = overlay.animations + animations if not transition_animation_surfaces else []

		for nav in navs:
			self.__nav_surfaces.add(NavSurface(copy(nav), self.__display_info, self.__pacab_game))

		for item in items:
			if not item.name in self.game_state.items and not item.name in self.game_state.dead_items:
				self.__item_surfaces.add(ItemSurface(copy(item), self.__display_info, self.__pacab_game))

		for interaction in interactions:
			self.__interaction_surfaces.add(InteractionSurface(copy(interaction), self.__display_info, self.__pacab_game))

		if transition_animation_surfaces:
			for animation in transition_animation_surfaces:
				self.__add_animation_surface(animation)
		elif animations:
			for animation in animations:
				if animation.should_show(self.game_state):
					self.__add_animation_surface(AnimationSurface(animation, self.__display_info, self.__pacab_game))
		if len(self.__queued_animations):
			for animation in self.__queued_animations:
				self.__add_animation_surface(animation)
			self.__queued_animations = []

		self.__all_sprites.add(self.__overlay_surfaces)
		self.__all_sprites.add(self.__nav_surfaces)
		self.__all_sprites.add(self.__item_surfaces)
		self.__all_sprites.add(self.__interaction_surfaces)
		self.__all_sprites.add(self.__animation_surfaces)

	def __update_surfaces(self, time_ms_last_frame: float) -> None:
		if self.__transition_surface:
			self.__transition_surface.update(time_ms_last_frame) # type: ignore
		else:
			self.__animation_surfaces.update(time_ms_last_frame)

	def __start_transition(self, transition: SceneTransition) -> None:
		self.__transition_surface = self.__create_transition_surface(transition)
		self.__all_sprites.add(self.__transition_surface)
		pygame.mouse.set_visible(False)

	def __end_transition(self) -> None:
		if self.__transition_surface:
			self.__change_scene(self.__transition_surface.next_scene.name, self.__transition_surface.next_animation_surfaces)
			self.__transition_surface = None
			pygame.mouse.set_visible(True)

	def __paint(self) -> None:
		if self.__bg_image:
			self.__screen.blit(
				pygame.transform.scale(self.__bg_image, (self.__display_info.window.width, self.__display_info.window.height)),
				(0, 0)
			)
		else:
			self.__screen.fill(self.__pacab_game.theme.game_bg_color)

		for sprite in self.__all_sprites:
			self.__screen.blit(sprite.image, sprite.rect)

		self.__paint_mask()

		self.__game_controls_menu.draw(self.__screen)
		if self.__is_state_paused() and self.__pause_menu.is_enabled():
			self.__pause_menu.draw(self.__screen)
		elif self.__is_state_inventory() and self.__inventory_menu.is_enabled():
			self.__inventory_menu.draw(self.__screen)
		elif self.__dialog_menu:
			self.__dialog_menu.draw(self.__screen)

		self.__window.blit(self.__screen, self.__screen.get_rect())

		pygame.display.flip()
	
	def __paint_mask(self) -> None:
		# For the SCENE_TRANSITION_DOWN only, since the cur_scene doesn't move and it "squishes" up to the top until it disappears,
		# it's tricky to make the animations slide up but then *not* draw themselves above the game window.
		# If there is a transition, and if there is a gap above the game window, this will draw the background over the top of that
		# area in order to hide the animation as it slides up and out of the game window area.
		if self.__transition_surface and self.__display_info.game_window.y > 0:
			mask = pygame.Surface((self.__display_info.game_window.width, self.__display_info.game_window.y))
			rect = pygame.Rect((0, 0, self.__display_info.game_window.width, self.__display_info.game_window.y))
			if self.__bg_image:
				mask.blit(
					pygame.transform.scale(self.__bg_image, (self.__display_info.window.width, self.__display_info.window.height)),
					(0, 0)
				)
			else:
				mask.fill(self.__pacab_game.theme.game_bg_color)

			self.__screen.blit(mask, rect)

	def __handle_events(self) -> None:
		events = pygame.event.get()

		is_input_blocked = (self.__dialog_menu and self.__dialog_menu.is_blocking) or self.__is_input_blocked

		for event in events:
			# End game events
			if event.type == pygame.QUIT:
				Logger.log("Game exiting!")
				self.__running = False
				continue
			if event.type == END_GAME:
				if "message" in event.dict and event.dict["message"]:
					after_event = pygame.event.Event(END_GAME)
					DialogRunner.create_from_str(event.dict["message"], None, after_event)
				else:
					self.__end_game()
				continue

			# Game events
			if self.__program_state == PROG_STATE_GAME and not is_input_blocked and not self.__transition_surface:
				self.__game_controls_menu.update([event])
				pos = pygame.mouse.get_pos()

				# Mouse
				if event.type == pygame.MOUSEBUTTONDOWN and event.dict["button"] == 1:
					if self.scene_surface.rect:
						if self.scene_surface.rect.collidepoint(pos):
							if not (self.__dialog_menu and self.__dialog_menu.get_rect().collidepoint(pos)):
								self.__set_cursor("click")
								self.__handle_game_mouse_click(pos)
				elif event.type == pygame.MOUSEBUTTONUP:
					self.__set_cursor("default")
				elif event.type == pygame.MOUSEMOTION:
					self.__update_cursor(pos)

				# Game Controls menu
				if event.type == GAME_CONTROL_PAUSE_CLICKED:
					Logger.log("Pausing game")
					self.__program_state = PROG_STATE_PAUSED
					self.__pause_menu.enable()
					continue
				if event.type == GAME_CONTROL_INVENTORY_CLICKED:
					Logger.log("Opening Inventory")
					self.__program_state = PROG_STATE_INVENTORY
					self.__inventory_menu.refresh()
					self.__inventory_menu.enable()
					continue
				if event.type == DISCARD_SELECTED_ITEM:
					self.game_state.selected_item = None
					self.__game_controls_menu.refresh()
					self.__inventory_menu.unselect_item()
					continue

				# Scenes
				if event.type == GOTO_SCENE:
					self.__change_scene(event.dict["scene_name"])
					continue
				if event.type == REFRESH_SCENE:
					if event.dict.get("keep_animations", False):
						self.__keep_animations_for_scene_refresh()
					self.__refresh_scene()
					continue

				# Misc
				if event.type == START_ANIMATION:
					Logger.log(f"Starting Animation '{event.dict["animation_name"]}'")
					self.__queue_animation_surface(event)
					if event.dict.get("needs_scene_refresh", False):
						self.__refresh_scene()
					continue
				
			# Pause menu
			elif self.__is_state_paused():
				if self.__pause_menu.is_enabled(): self.__pause_menu.update([event])
				if event.type == PAUSE_MENU_RESUME_CLICKED:
					Logger.log(f"Unpausing game")
					self.__program_state = PROG_STATE_GAME
					self.__pause_menu.disable()
					continue
				if event.type == SAVE_MENU_GAME_SAVED:
					Logger.log(f"Game saved, unpausing game")
					self.__program_state = PROG_STATE_GAME
					self.__pause_menu.disable()
					continue
				if event.type == PAUSE_MENU_QUIT_CLICKED:
					self.__end_game()
					continue
				if event.type == OPT_UPDATE_ENABLE_MUSIC:
					enable_music = event.dict["enable_music"]
					Logger.log(f"Options 'enable_music' change: {enable_music}")
					self.__audio.set_enable_music(
						enable_music,
						self.scene.music,
						self.scene.music_2,
						self.scene.music_2_loops,
						self.scene.music_2_repeat,
						self.game_state.dead_music_2,
						self.game_state,
						self.scene,
					)
					continue
				if event.type == OPT_UPDATE_ENABLE_SOUND:
					enable_sound = event.dict["enable_sound"]
					Logger.log(f"Options 'enable_sound' change: {enable_sound}")
					self.__audio.set_enable_sound(enable_sound)
					continue

			# Inventory menu
			elif self.__is_state_inventory():
				if self.__inventory_menu.is_enabled(): self.__inventory_menu.update([event])
				if event.type == INVENTORY_MENU_CLOSE_CLICKED:
					self.__program_state = PROG_STATE_GAME
					self.__inventory_menu.disable()
					if self.game_state.selected_item:
						self.__game_controls_menu.refresh()
					# The Inventory Menu gets slower the more you use it. This is a quick hack to reload it each time it closes.
					# Not sure if the root of the problem is in pygame-menu or how pacab is using it.
					self.__inventory_menu = InventoryMenu(self.__pacab_game, self.__display_info, self.__get_game_state)
					continue
				if event.type == REFRESH_INVENTORY:
					self.__inventory_menu.unselect_item()
					self.__inventory_menu.refresh()
					continue
				if event.type == DISCARD_SELECTED_ITEM:
					self.game_state.selected_item = None
					self.__game_controls_menu.refresh()
					self.__inventory_menu.unselect_item()
					continue

			# Dialog events
			if self.__program_state == PROG_STATE_GAME:
				if event.type == DIALOG_FROM_STR:
					Logger.log("Opening Dialog:")
					Logger.log(event.dict["text"])
					if "timeout" in event.dict: timeout = event.dict["timeout"]
					else: timeout = 4000
					DialogRunner.create_from_str(event.dict["text"], timeout)
					continue
				if event.type == DIALOG_SHOW:
					if event.dict["prompt"].name: Logger.log(f"Opening Dialog Prompt '{event.dict["prompt"].name}'")
					self.__show_dialog_menu(
						event.dict["prompt"],
						event.dict["timeout"] if "timeout" in event.dict else None,
						event.dict["is_blocking"] if "is_blocking" in event.dict else True,
						event.dict["title"] if "title" in event.dict else "",
						event.dict["after_event"] if "after_event" in event.dict else None,
					)
					continue
				if event.type == DIALOG_START:
					Logger.log(f"Starting Dialog '{event.dict["dialog_name"]}'")
					DialogRunner.start_dialog(self.__pacab_game.get_dialog(event.dict["dialog_name"]))
					continue
				if event.type == DIALOG_CLEAR_TIMEOUT:
					self.__is_dialog_timeout = False
					continue

			# Dialog Menu events
			if self.__dialog_menu:
				self.__dialog_menu.update([event])
				if event.type == DIALOG_CONTINUE or event.type == DIALOG_TIMEOUT:
					if event.type == DIALOG_TIMEOUT and not self.__is_dialog_timeout: continue # Prevent old timeout events from closing new Dialogs
					if self.__dialog_menu.has_next_page:
						self.__dialog_menu.on_continue_text_click()
						pygame.time.set_timer(DIALOG_TIMEOUT, self.__prev_dialog_timeout, loops=1)
					else:
						after_event = self.__dialog_menu.after_event
						self.__clear_dialog_menu()
						DialogRunner.continue_dialog()
						if after_event: pygame.event.post(after_event)
					continue
				if event.type == DIALOG_REPLY:
					Logger.log(f"Replied '{event.dict["reply"].name}'")
					self.__clear_dialog_menu()
					DialogRunner.reply_dialog(event.dict["reply"], self.game_state)
					continue
			if event.type == DIALOG_PAUSE_START:
				Logger.log(f"Dialog pausing for {event.dict["timeout"]} ms")
				self.__is_input_blocked = True
				pygame.time.set_timer(pygame.event.Event(DIALOG_PAUSE_END, { "reply": event.dict["reply"] }), event.dict["timeout"], 1)
				continue
			if event.type == DIALOG_PAUSE_END:
				Logger.log(f"Dialog resuming")
				self.__is_input_blocked = False
				DialogRunner.reply_dialog_finish(event.dict["reply"])
				continue

			# Other events
			if event.type == UPDATE_PROGRAM_STATE:
				self.__program_state = event.dict["state"]
				continue
			if event.type == pygame.VIDEORESIZE:
				# This is needed as for some reason the video isn't fully updated unless we wait one more frame
				pygame.event.post(pygame.event.Event(REDO_LAYOUT))
				continue
			if event.type == REDO_LAYOUT:
				self.__redo_layout()
				continue
			if event.type == PLAY_SOUND:
				Logger.log(f"Playing sound '{event.dict["sound"]}'")
				self.__audio.play_sound(event.dict["sound"])
				continue
			if event.type == ANIMATION_COMPLETE:
				animation = event.dict["animation"]
				Logger.log(f"Animation '{animation}' completed.")
				self.game_state.dead_animations.append(animation)
				continue
			if event.type == MUSIC_2_COMPLETE:
				music_2 = event.dict["music_2"]
				Logger.log(f"Music '{music_2}' completed.")
				self.game_state.dead_music_2.append(music_2)
				self.__audio.stop_music_2(music_2)
				continue
			if event.type == SCENE_TRANSITION_START:
				transition = SceneTransition(event.dict["transition_type"], event.dict["scene_name"], event.dict["speed"])
				self.__start_transition(transition)
				continue
			if event.type == SCENE_TRANSITION_END:
				if ActionRunner.queue: ActionRunner.resume(self.game_state)
				self.__end_transition()
				continue
			if event.type == BLOCK_INPUT_START:
				Logger.log(f"Input pausing for {event.dict["timeout"]} ms")
				self.__is_input_blocked = True
				pygame.time.set_timer(pygame.event.Event(BLOCK_INPUT_END), event.dict["timeout"], 1)
				continue
			if event.type == BLOCK_INPUT_END:
				Logger.log(f"Input resuming")
				if ActionRunner.queue: ActionRunner.resume(self.game_state)
				self.__is_input_blocked = False
				continue
			if event.type == PAUSE_ACTIONS_START:
				Logger.log(f"Pausing action execution for {event.dict["timeout"]} ms")
				ActionRunner.paused = True
				pygame.time.set_timer(pygame.event.Event(PAUSE_ACTIONS_END), event.dict["timeout"], 1)
				continue
			if event.type == PAUSE_ACTIONS_END:
				Logger.log(f"Action execution resuming")
				ActionRunner.paused = False
				if ActionRunner.queue: ActionRunner.resume(self.game_state)
				continue
			if event.type == INVENTORY_MENU_RESET_PAGE:
				self.__inventory_menu.reset_page()
				continue

	def __handle_game_mouse_click(self, pos: tuple[int, int]) -> None:
		if not self.__dialog_menu or not self.__dialog_menu.is_blocking:
			# Item
			if not self.game_state.selected_item:
				for item_surface in self.__item_surfaces:
					if not item_surface.item.can_pick_up: continue
					if item_surface.rect.collidepoint(pos):
						self.__pick_up_item(item_surface.item)
						item_surface.kill()
						return

			# Interaction
			for interaction_surface in self.__interaction_surfaces:
				if interaction_surface.rect.collidepoint(pos):
					if interaction_surface.is_interactable(self.game_state):
						interaction_surface.interact(self.game_state)
						return

			# Navigation
			for nav_surface in self.__nav_surfaces:
				if nav_surface.rect.collidepoint(pos):
					if ActionRunner.paused: ActionRunner.queue = []
					if nav_surface.nav.transition:
						self.__start_transition(nav_surface.nav.transition)
					else:
						self.__change_scene(nav_surface.nav.to_scene_name)

					if nav_surface.nav.sound:
						self.__audio.play_sound(nav_surface.nav.sound)

					return

			# Using an item on empty background
			if self.game_state.selected_item:
				DialogRunner.create_from_str(_("cant_use_item_here", "You can't use that here."), 4000)
				return

	def __update_cursor(self, pos: tuple[int, int]) -> None:
		was_mouse_in_bounds = self.__is_mouse_in_game_bounds
		is_mouse_in_bounds = self.scene_surface.rect and self.scene_surface.rect.collidepoint(pos)

		# If in game area, but not over a dialog menu, check if the mouse is over something and set the cursor.
		if was_mouse_in_bounds and is_mouse_in_bounds:
			dialog_rect = self.__dialog_menu and self.__dialog_menu.get_rect()
			over_dialog = dialog_rect and dialog_rect.collidepoint(pos)
			if not over_dialog:
				cursor = "default"
				surfaces = list(self.__item_surfaces) + list(self.__interaction_surfaces) + list(self.__nav_surfaces)
				for surface in surfaces:
					if surface.rect.collidepoint(pos):
						cursor = "hover"
						break
				self.__set_cursor(cursor)

		# Upon leaving the game area, must set the cursor to default once.
		elif was_mouse_in_bounds and not is_mouse_in_bounds:
			self.__set_cursor("default")

		self.__is_mouse_in_game_bounds = is_mouse_in_bounds

	def __get_game_state(self) -> GameState:
		return self.game_state

	def __pick_up_item(self, item: InventoryItem) -> None:
		Logger.log(f"Picked up item '{item.name}'")

		self.game_state.items.append(item.name)
		if item.pickup_message:
			DialogRunner.create_from_str(item.pickup_message, 2500)
		if item.pickup_sound:
			self.__audio.play_sound(item.pickup_sound)
	
	def __show_dialog_menu(self, prompt: Prompt, timeout: int | None, is_blocking: bool, title: str = "", after_event: pygame.event.Event | None = None) -> None:
		dialog_name = DialogRunner.current_dialog.name if DialogRunner.current_dialog else ""
		self.__dialog_menu = DialogMenu(title, dialog_name, prompt, self.game_state, self.__pacab_game, self.__display_info, is_blocking, after_event)
		self.__dialog_menu.enable()
		if timeout:
			self.__is_dialog_timeout = True
			pygame.time.set_timer(DIALOG_TIMEOUT, timeout, loops=1)
			self.__prev_dialog_timeout = timeout
	
	def __clear_dialog_menu(self) -> None:
		if isinstance(self.__dialog_menu, DialogMenu):
			self.__dialog_menu.disable()
			self.__dialog_menu = None
	
	def __set_cursor(self, cursor_name: str) -> None:
		if cursor_name == "click" and self.__pacab_game.theme.cursors.cursor_click:
			pygame.mouse.set_cursor(self.__pacab_game.theme.cursors.cursor_click)
		elif cursor_name == "hover" and self.__pacab_game.theme.cursors.cursor_hover:
			pygame.mouse.set_cursor(self.__pacab_game.theme.cursors.cursor_hover)
		elif self.__pacab_game.theme.cursors.cursor_default:
			pygame.mouse.set_cursor(self.__pacab_game.theme.cursors.cursor_default)
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

	def __update_song(self, cur_scene: Scene, new_scene: Scene, game_state: GameState) -> None:
		if cur_scene.music != new_scene.music: Logger.log(f"Music switching from '{cur_scene.music}' to '{new_scene.music}'")
		if (cur_scene.music_2 != new_scene.music_2) \
			or (cur_scene.music_2 == new_scene.music_2 and not self.__audio.is_playing_2()):
			if cur_scene.music_2 or new_scene.music_2:
				Logger.log(f"Music 2 switching from '{cur_scene.music_2}' to '{new_scene.music_2}'")

		if cur_scene.music and not new_scene.music:
			self.__audio.pause_music()
		elif (cur_scene.music != new_scene.music) and new_scene.music:
			self.__audio.play_music(new_scene.music)
		elif new_scene.music and not self.__audio.is_playing():
			self.__audio.play_music(new_scene.music)

		if cur_scene.music_2 and not new_scene.music_2:
			self.__audio.stop_music_2(cur_scene.music_2)
		elif ((cur_scene.music_2 != new_scene.music_2) or (cur_scene.music_2 == new_scene.music_2 and not self.__audio.is_playing_2())) \
			and new_scene.music_2:
			if cur_scene.music_2: self.__audio.stop_music_2(cur_scene.music_2)
			if Condition.check_conditions(game_state, new_scene.music_2_conditions, new_scene.music_2_conditions_use_or):
				self.__audio.play_music_2(new_scene.music_2, new_scene.music_2_loops, new_scene.music_2_repeat, self.game_state.dead_music_2)
			else:
				Logger.log("Music 2 will not play, Conditions not met.")

	def __create_transition_surface(self, transition: SceneTransition) -> TransitionSurface:
		next_scene = self.__pacab_game.get_scene(transition.to_scene_name)

		cur_static_surfaces = pygame.sprite.Group()
		cur_static_surfaces.add(self.__overlay_surfaces)
		cur_static_surfaces.add(self.__item_surfaces)
		cur_animation_surfaces = self.__animation_surfaces
		next_static_surfaces = pygame.sprite.Group()
		next_animation_surfaces = pygame.sprite.Group()
		item_surfaces = pygame.sprite.Group()
		animation_surfaces = pygame.sprite.Group()
		overlay_surfaces = pygame.sprite.Group()

		items = next_scene.items
		animations = next_scene.animations

		if next_scene.overlays:
			for overlay in next_scene.overlays:
				if overlay.should_show(self.game_state):
					overlay_surfaces.add(OverlaySurface(copy(overlay), self.__display_info, self.__pacab_game))
					items = overlay.items + items
					animations = overlay.animations + animations
		for item in items:
			if not item.name in self.game_state.items and not item.name in self.game_state.dead_items:
				item_surfaces.add(ItemSurface(copy(item), self.__display_info, self.__pacab_game))
		if animations:
			for animation in animations:
				if animation.should_show(self.game_state):
					animation_surfaces.add(AnimationSurface(animation, self.__display_info, self.__pacab_game))

		next_static_surfaces.add(item_surfaces)
		next_static_surfaces.add(overlay_surfaces)
		next_animation_surfaces.add(animation_surfaces)

		transition_surface = TransitionSurface(
			self.__display_info,
			transition,
			self.scene_surface,
			cur_static_surfaces,
			cur_animation_surfaces,
			next_scene,
			next_static_surfaces,
			next_animation_surfaces,
		)

		return transition_surface

	def __add_animation_surface(self, animation_surface: AnimationSurface) -> None:
		found = False
		for surface in self.__animation_surfaces:
			if surface.animation.id == animation_surface.animation.id:
				found = True
				break
		if not found:
			self.__animation_surfaces.add(animation_surface)
		
	def __queue_animation_surface(self, event: pygame.event.Event) -> None:
		animation_frames = self.__pacab_game.get_animation_frames(event.dict["animation_name"])
		animation = Animation(
			event.dict["x"],
			event.dict["y"],
			event.dict["width"],
			event.dict["height"],
			self.scene.name + "_" + animation_frames.filename,
			animation_frames.filename,
			1,
			True,
			event.dict["duration"],
			event.dict["alpha"],
			event.dict["hold_final_frame"],
			[],
			False,
		)
		animation_surface = AnimationSurface(animation, self.__display_info, self.__pacab_game)
		self.__queued_animations.append(animation_surface)

	def __keep_animations_for_scene_refresh(self) -> None:
		for animation_surface in self.__animation_surfaces:
			should_show = animation_surface.animation.should_show(self.game_state)
			if self.scene.overlays:
				for overlay in self.scene.overlays:
					if not overlay.should_show(self.game_state):
						if animation_surface.animation.id in [x.id for x in overlay.animations]:
							should_show = False
			if should_show:
				self.__queued_animations.append(animation_surface)
			else:
				animation_surface.kill()

	def __execute_scene_actions(self, scene_actions: list[SceneAction]) -> None:
		if not len(scene_actions): return
		for scene_action in scene_actions:
			if scene_action.should_execute(self.game_state):
				if not scene_action.repeat:
					self.game_state.dead_scene_actions.append(scene_action.name)
				ActionRunner.execute_actions(self.game_state, scene_action.actions)

	def __end_game(self) -> None:
		Logger.log("Game exiting!")

		self.game_state.selected_item = None
		self.__game_controls_menu.refresh()
		self.__inventory_menu.unselect_item()

		self.__program_state = PROG_STATE_MAINMENU

		self.__running = False
	
	def __is_state_gameplay(self) -> bool:
		return self.__program_state == PROG_STATE_GAME or self.__is_state_inventory() or self.__is_state_paused()

	def __is_state_inventory(self) -> bool:
		return self.__program_state == PROG_STATE_INVENTORY or self.__program_state == PROG_STATE_INVINSPECT

	def __is_state_paused(self) -> bool:
		return self.__program_state == PROG_STATE_PAUSED or self.__program_state == PROG_STATE_SAVEMENU or self.__program_state == PROG_STATE_PAUSEOPTIONS
