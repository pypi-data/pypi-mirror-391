import io
import math
from typing import Callable

import pygame
import pygame_menu
import pygame_menu.events
from pygame_menu.baseimage import BaseImage
from pygame_menu.locals import ALIGN_CENTER, ALIGN_RIGHT, ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL
from pygame_menu.widgets.widget.image import Image
from pacab.actionrunner import ActionRunner

from pacab.constants import DISCARD_SELECTED_ITEM, PROG_STATE_INVENTORY, PROG_STATE_INVINSPECT, REFRESH_INVENTORY, UPDATE_PROGRAM_STATE
from pacab.displayinfo import DisplayInfo
from pacab.menus.menutheme import get_menu_theme
from pacab.text import get_string as _
from pacab.types.condition import Condition
from pacab.types.inventoryitem import InventoryItem
from pacab.types.pacabgame import PacabGame


class InspectMenu(pygame_menu.Menu):
	def __init__(self, pacab_game: PacabGame, display_info: DisplayInfo, get_game_state: Callable) -> None:
		theme = get_menu_theme(
			pacab_game.theme.inventory_bg_color,
			pacab_game.theme.inventory_bg_image,
			pacab_game.theme.inventory_titlebar_style,
			pacab_game.theme.inventory_title_bg_color,
			pacab_game.theme.inventory_title_font_color,
			pacab_game.theme.inventory_title_font,
			pacab_game.theme.cursors.cursor_default,
			pacab_game.theme.inventory_font_color,
			pacab_game.theme.inventory_font,
			display_info.widget_padding,
		)
		theme.title_floating = True

		super().__init__(
			"",
			display_info.inventory_menu.width,
			display_info.inventory_menu.height,
			position=(display_info.inventory_menu.x, display_info.inventory_menu.y, False),
			theme=theme,
			enabled=False,
			verbose=False,
		)

		self.__display_info = display_info
		self.__get_game_state = get_game_state
		self.__image: Image | None = None
		self.__item: InventoryItem | None = None

		self._onbeforeopen = lambda *_: self.__refresh()
		self._onreset = lambda *_: self.__onclose()
		self.get_scrollarea().hide_scrollbars(ORIENTATION_HORIZONTAL)
		self.get_scrollarea().hide_scrollbars(ORIENTATION_VERTICAL)

		self.__back_button = self.add.button(
			_("menu_back", "Back"),
			pygame_menu.events.BACK,
			cursor=pacab_game.theme.cursors.cursor_hover,
			font_size=display_info.font_size.normal,
		)

		self.__deconstruct_button = self.add.button(
			_("menu_inventory_take_apart", "Take Apart"),
			self.__deconstruct_item,
			cursor=pacab_game.theme.cursors.cursor_hover,
			font_size=display_info.font_size.normal,
		)

		menu_frame = self.add.frame_h(display_info.inventory_menu.width, self.__back_button.get_height(), padding=0)
		menu_frame.pack(self.__back_button, ALIGN_RIGHT)
		menu_frame.pack(self.__deconstruct_button, ALIGN_RIGHT)

		self.__content_frame = self.add.frame_v(
			display_info.inventory_menu.width,
			display_info.inventory_menu.height - self.__back_button.get_height(),
			padding=0,
		)

	def set_selected_item(self, item: InventoryItem) -> None:
		if self.__image:
			self.remove_widget(self.__image)
			self.__image = None

		self.__item = item

		self.__deconstruct_button.set_title(_(item.deconstruct_label))

		max_width = math.floor(self.__display_info.inventory_menu.width * 0.98)
		max_height = self.__display_info.inventory_menu.height - self.__back_button.get_height()

		image = pygame_menu.BaseImage(io.BytesIO(item.images[0][1]))
		scale = max_height / image.get_height()
		image = image.scale(scale, scale)
		if image.get_width() > max_width:
			scale = max_width / image.get_width()
			image = image.scale(scale, scale)

		self.__image = self.add.image(image, padding=self.__get_content_padding(image))
		self.__content_frame.pack(self.__image, ALIGN_CENTER)

	def __get_content_padding(self, image: BaseImage) -> tuple[int, int, int, int]:
		t = r = b = l = 0
		width = self.__content_frame.get_width()
		height = self.__content_frame.get_height()
		if image.get_width() < width:
			r = l = math.floor((width - image.get_width()) / 2)
		if image.get_height() < height:
			t = b = math.floor((height - image.get_height()) / 2)
		return (t, r, b ,l)

	def __onclose(self) -> None:
		pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_INVENTORY }))
	
	def __refresh(self) -> None:
		self.__run_inspect_actions()
		pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_INVINSPECT }))

		if self.__item:
			if len(self.__item.deconstruct_to):
				self.__deconstruct_button.show()
			else:
				self.__deconstruct_button.hide()
	
	def __deconstruct_item(self) -> None:
		if self.__item:
			game_state = self.__get_game_state()

			game_state.items.remove(self.__item.name)
			game_state.dead_items.append(self.__item.name)
			for item in self.__item.deconstruct_to:
				game_state.items.append(item)

			if game_state.selected_item == self.__item.name:
				pygame.event.post(pygame.event.Event(DISCARD_SELECTED_ITEM))

		pygame.event.post(pygame.event.Event(REFRESH_INVENTORY))

		self.reset(1)

	def __run_inspect_actions(self) -> None:
		if self.__item and self.__item.inspect_actions:
			game_state = self.__get_game_state()
			for inspect_action in self.__item.inspect_actions:
				if Condition.check_conditions(game_state, inspect_action.conditions, inspect_action.conditions_use_or):
					ActionRunner.execute_actions(game_state, inspect_action.actions)
