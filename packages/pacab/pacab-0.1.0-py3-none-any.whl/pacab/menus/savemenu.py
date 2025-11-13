from datetime import datetime
from typing import Callable

import pygame
import pygame_menu
import pygame_menu.events
from pygame_menu.locals import ALIGN_CENTER
from pygame_menu.widgets.widget.label import Label

from pacab.constants import *
from pacab.displayinfo import DisplayInfo
from pacab.gamesave import GameSave
from pacab.gamestate import GameState
from pacab.menus.menutheme import get_menu_theme
from pacab.text import get_string as _
from pacab.types.pacabgame import PacabGame


class SaveMenu(pygame_menu.Menu):
	def __init__(self, pacab_game: PacabGame, display_info: DisplayInfo, get_game_state: Callable) -> None:
		theme = get_menu_theme(
			pacab_game.theme.pause_menu_bg_color,
			pacab_game.theme.pause_menu_bg_image,
			pacab_game.theme.pause_menu_titlebar_style,
			pacab_game.theme.pause_menu_title_bg_color,
			pacab_game.theme.pause_menu_title_font_color,
			pacab_game.theme.pause_menu_title_font,
			pacab_game.theme.cursors.cursor_hover,
			pacab_game.theme.pause_menu_font_color,
			pacab_game.theme.pause_menu_font,
			display_info.widget_padding,
		)

		super().__init__(
			_("menu_save_game", "Save Game"),
			display_info.pause_menu.width,
			display_info.pause_menu.height,
			position=(display_info.pause_menu.x, display_info.pause_menu.y, False),
			theme=theme,
			enabled=False,
			verbose=False,
		)

		self.__pacab_game = pacab_game
		self.__get_game_state = get_game_state
		self.__is_saving_game = False

		self._onbeforeopen = lambda *_: self.__refresh()
		self._onreset = lambda *_: self.__onclose()

		self.__name_input = self.add.text_input(_("menu_save_name", "Name: "), maxchar=30, font_size=display_info.font_size.normal)
		save_button = self.add.button(_("menu_save_game", "Save Game"), self.__on_save_click, font_size=display_info.font_size.normal)
		self.__input_frame = self.add.frame_v(
			display_info.pause_menu.width,
			self.__name_input.get_height() + save_button.get_height(),
			margin=(0, display_info.font_size.title),
		)
		self.__input_frame._relax = True
		self.__input_frame.pack(self.__name_input, align=ALIGN_CENTER)
		self.__input_frame.pack(save_button, align=ALIGN_CENTER)

		self.__error_label: Label = self.add.label("", font_size=display_info.font_size.normal) # type: ignore
		yes_button = self.add.button(_("menu_yes", "Yes"), self.__on_confirm_save_click, font_size=display_info.font_size.normal)
		no_button = self.add.button(_("menu_no", "No"), self.__on_cancel_save_click, font_size=display_info.font_size.normal)
		self.__error_frame = self.add.frame_v(
			display_info.pause_menu.width,
			self.__error_label.get_height() + yes_button.get_height() + no_button.get_height(), # type: ignore
			margin=(0, display_info.font_size.title),
		)
		self.__error_frame._relax = True
		self.__error_frame.pack(self.__error_label, align=ALIGN_CENTER)
		self.__error_frame.pack(yes_button, align=ALIGN_CENTER)
		self.__error_frame.pack(no_button, align=ALIGN_CENTER)
		self.__error_frame.hide()

		self.add.button(_("menu_cancel", "Cancel"), pygame_menu.events.BACK, font_size=display_info.font_size.normal)

	def __on_cancel_save_click(self) -> None:
		self.__name_input.set_value("")
		self.__input_frame.show()
		self.__error_frame.hide()

	def __on_confirm_save_click(self) -> None:
		self.__save_game()

	def __on_save_click(self) -> None:
		name = self.__name_input.get_value().strip()
		if not name: return

		game_saves = GameSave.load_saved_games(self.__pacab_game.short_name)
		exists = False
		for game_save in game_saves:
			if name == game_save.name:
				exists = True
				break

		if exists:
			self.__error_label.set_title(_("menu_save_confirm", "Saved game exists! Overwrite?"))
			self.__error_frame.show()
			self.__input_frame.hide()
		else:
			self.__save_game()

	def __onclose(self) -> None:
		if not self.__is_saving_game:
			pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_PAUSED }))
	
	def __refresh(self) -> None:
		pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_SAVEMENU }))

	def __save_game(self) -> None:
		game_state: GameState = self.__get_game_state()
		name = self.__name_input.get_value().strip()

		game_save = GameSave(self.__pacab_game.short_name, name, datetime.now(), game_state)
		game_save.save()

		self.__name_input.set_value("")
		self.__input_frame.show()
		self.__error_frame.hide()
		pygame.event.post(pygame.event.Event(SAVE_MENU_GAME_SAVED))
		self.__is_saving_game = True
		self.reset(1) # Somehow this works to close the SaveMenu so that when the PauseMenu is re-opened, it doesn't re-open the SaveMenu too.
		self.__is_saving_game = False
