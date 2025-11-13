from typing import Callable

import pygame_menu
import pygame_menu.events

from pacab.displayinfo import DisplayInfo
from pacab.menus.loadgamemenu import LoadGameMenu
from pacab.menus.menutheme import get_menu_theme
from pacab.menus.optionsmenu import OptionsMenu
from pacab.text import get_string as _
from pacab.types.pacabgame import PacabGame


class MainMenu(pygame_menu.Menu):
	def __init__(self, pacab_game: PacabGame, display_info: DisplayInfo, new_game_callback: Callable) -> None:
		theme = get_menu_theme(
			pacab_game.theme.main_menu_bg_color,
			pacab_game.theme.main_menu_bg_image,
			pacab_game.theme.main_menu_titlebar_style,
			pacab_game.theme.main_menu_title_bg_color,
			pacab_game.theme.main_menu_title_font_color,
			pacab_game.theme.main_menu_title_font,
			pacab_game.theme.cursors.cursor_hover,
			pacab_game.theme.main_menu_font_color,
			pacab_game.theme.main_menu_font,
			display_info.widget_padding,
		)
		top_title = pacab_game.name if not pacab_game.theme.main_menu_title_inline else ""
		
		super().__init__(
			top_title,
			display_info.window.width,
			display_info.window.height,
			theme=theme,
			verbose=False,
		)

		if pacab_game.theme.main_menu_title_inline:
			self.add.label(
				pacab_game.name,
				background_color=pacab_game.theme.main_menu_title_bg_color,
				font_name=pacab_game.theme.main_menu_title_font,
				font_color=pacab_game.theme.main_menu_title_font_color,
				font_size=display_info.font_size.title,
				margin=(0, 32),
			)

		load_game_menu = LoadGameMenu(pacab_game, display_info, new_game_callback)
		options_menu = OptionsMenu(pacab_game, display_info, False)

		self.add.button(_("menu_play_game", "Play"), new_game_callback, font_size=display_info.font_size.normal)
		self.load_game_button = self.add.button(_("menu_load_game", "Load Game"), load_game_menu, font_size=display_info.font_size.normal)
		self.options_button = self.add.button(_("menu_options", "Options"), options_menu, font_size=display_info.font_size.normal)
		self.add.button(_("menu_quit", "Quit"), pygame_menu.events.EXIT, font_size=display_info.font_size.normal)
