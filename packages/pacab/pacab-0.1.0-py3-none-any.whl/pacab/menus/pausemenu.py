from typing import Callable

import pygame
import pygame_menu

from pacab.constants import *
from pacab.displayinfo import DisplayInfo
from pacab.menus.menutheme import get_menu_theme
from pacab.menus.optionsmenu import OptionsMenu
from pacab.menus.savemenu import SaveMenu
from pacab.text import get_string as _
from pacab.types.pacabgame import PacabGame


class PauseMenu(pygame_menu.Menu):
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
			_("menu_paused", "Paused"),
			display_info.pause_menu.width,
			display_info.pause_menu.height,
			position=(display_info.pause_menu.x, display_info.pause_menu.y, False),
			theme=theme,
			enabled=False,
			verbose=False,
		)

		self.__save_menu = SaveMenu(pacab_game, display_info, get_game_state)
		self.__options_menu = OptionsMenu(pacab_game, display_info, True)

		self.add.button(_("menu_resume", "Resume"), self.__on_resume_clicked, font_size=display_info.font_size.normal)
		self.save_button = self.add.button(_("menu_save_game", "Save Game"), self.__save_menu, font_size=display_info.font_size.normal)
		self.options_button = self.add.button(_("menu_options", "Options"), self.__options_menu, font_size=display_info.font_size.normal)
		self.add.button(_("menu_quit", "Quit"), self.__on_quit_clicked, font_size=display_info.font_size.normal)

	def __on_resume_clicked(self) -> None:
		pygame.event.post(pygame.event.Event(PAUSE_MENU_RESUME_CLICKED))

	def __on_quit_clicked(self) -> None:
		pygame.event.post(pygame.event.Event(PAUSE_MENU_QUIT_CLICKED))
