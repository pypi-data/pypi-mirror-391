import io
import math
from typing import Callable

import pygame
import pygame_menu
from pygame_menu.widgets.widget.button import Button

from pacab.constants import *
from pacab.displayinfo import DisplayInfo
from pacab.menus.menutheme import get_menu_theme
from pacab.surfaces.closebuttonsurface import CloseButtonSurface
from pacab.text import get_string as _
from pacab.types.pacabgame import PacabGame


class GameControlsMenu(pygame_menu.Menu):
	def __init__(self, pacab_game: PacabGame, display_info: DisplayInfo, get_game_state: Callable) -> None:
		theme = get_menu_theme(
			pacab_game.theme.game_controls_bg_color,
			pacab_game.theme.game_controls_bg_image,
			pacab_game.theme.game_controls_titlebar_style,
			pacab_game.theme.game_controls_bg_color,
			pacab_game.theme.main_menu_title_font_color,
			pacab_game.theme.main_menu_title_font,
			pacab_game.theme.cursors.cursor_hover,
			pacab_game.theme.game_controls_font_color,
			pacab_game.theme.game_controls_font,
			display_info.widget_padding,
		)

		super().__init__(
			"",
			display_info.game_controls.width,
			display_info.game_controls.height,
			center_content=False,
			position=(display_info.game_controls.x, display_info.game_controls.y, False),
			theme=theme,
			verbose=False,
		)

		self.__pacab_game = pacab_game
		self.__display_info = display_info
		self.__get_game_state = get_game_state
		self.__item_discard_button: Button | None = None

		self.add.label("", font_size=display_info.font_size.normal) # type: ignore
		self.add.button(
			_("menu_menu", "Menu"),
			self.__on_menu_click,
			font_size=display_info.font_size.normal,
			margin=(0, display_info.font_size.small),
			selection_effect=None,
		)
		self.add.button(
			_("menu_inventory", "Inventory"),
			self.__on_inventory_click,
			font_size=display_info.font_size.normal,
			margin=(0, display_info.font_size.title),
			selection_effect=None,
		)

	def refresh(self) -> None:
		if self.__item_discard_button:
			self.remove_widget(self.__item_discard_button)
			self.__item_discard_button = None
			self.remove_widget(self.__close_button)

		game_state = self.__get_game_state()
		if game_state.selected_item:
			selected_item = self.__pacab_game.get_item(game_state.selected_item)

			image = pygame_menu.BaseImage(io.BytesIO(selected_item.images[0][1]))
			image_wh = (image.get_width() if image.get_width() > image.get_height() else image.get_height())
			if self.__display_info.inventory_menu.is_portrait:
				image_wh *= 2
			scale = self.__display_info.game_controls.width / image_wh
			image = image.scale(scale, scale)

			self.__item_discard_button = self.add.banner(image, self.__on_discard_item_click)

			close_button_width = math.floor(self.__item_discard_button.get_width() * 0.2)
			close_button_surface = CloseButtonSurface(close_button_width)

			self.__close_button = self.add.surface(close_button_surface.image, float=True) # type: ignore
			self.__close_button.translate(
				math.floor((self.__item_discard_button.get_width() / 2) - (close_button_width / 2)),
				math.floor(close_button_width / 6),
			)
		
		self.force_surface_update()

	def __on_discard_item_click(self) -> None:
		pygame.event.post(pygame.event.Event(DISCARD_SELECTED_ITEM))

	def __on_inventory_click(self) -> None:
		pygame.event.post(pygame.event.Event(GAME_CONTROL_INVENTORY_CLICKED))

	def __on_menu_click(self) -> None:
		pygame.event.post(pygame.event.Event(GAME_CONTROL_PAUSE_CLICKED))
