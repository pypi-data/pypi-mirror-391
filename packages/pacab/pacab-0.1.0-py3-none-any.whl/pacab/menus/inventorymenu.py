import io
import math
from typing import Callable

import pygame
import pygame_menu
from pygame_menu.baseimage import BaseImage
from pygame_menu.locals import ALIGN_CENTER, ALIGN_RIGHT, ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL
from pygame_menu.widgets.widget.image import Image
from pygame_menu.widgets.widget.label import Label

from pacab.constants import *
from pacab.displayinfo import DisplayInfo
from pacab.gamestate import GameState
from pacab.menus.inspectmenu import InspectMenu
from pacab.menus.menutheme import get_menu_theme
from pacab.text import get_string as _
from pacab.types.inventoryitem import InventoryItem
from pacab.types.pacabgame import PacabGame


NUM_ROWS = 2

class InventoryMenu(pygame_menu.Menu):
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

		self.selected_item: str | None = None

		self.__pacab_game = pacab_game
		self.__display_info = display_info
		self.__get_game_state = get_game_state
		self.__is_combining = False
		self.__item_image: Image | None = None
		self.__page_skip = 0
		self.__inspect_menu = InspectMenu(pacab_game, display_info, get_game_state)

		self.get_scrollarea().hide_scrollbars(ORIENTATION_HORIZONTAL)
		self.get_scrollarea().hide_scrollbars(ORIENTATION_VERTICAL)
	
		if display_info.inventory_menu.is_portrait:
			outer_frame = self.add.frame_v(display_info.inventory_menu.width, display_info.inventory_menu.height, padding=0)

			page_frame_w = display_info.inventory_menu.table_width
			left_pane_frame = right_pane_frame = None
		else:
			outer_frame = self.add.frame_h(display_info.inventory_menu.width, display_info.inventory_menu.height, padding=0)

			page_frame_w = display_info.inventory_menu.left_pane_width_padded
			left_pane_frame = self.add.frame_v(
				display_info.inventory_menu.left_pane_width,
				display_info.inventory_menu.height,
				"left_pane_frame",
				padding=(20, 10, 20, 20),
			)
			right_pane_frame = self.add.frame_v(
				display_info.inventory_menu.right_pane_width,
				display_info.inventory_menu.height,
				"right_pane_frame",
				padding=(20, 0, 20, 0),
			)
			right_pane_frame._relax = True

		self.__table = self.add.frame_v(
			display_info.inventory_menu.table_width,
			display_info.inventory_menu.table_height,
			"table_frame",
			background_color=pacab_game.theme.inventory_bg_color_alt,
			padding=20,
		)

		self.__page_frame = self.add.frame_h(page_frame_w, 1, padding=0)
		self.__page_frame._relax = True
		self.__page_down_button = self.add.button("▼", self.__on_page_down_click, font_name="Monospace", font_size=display_info.font_size.small)
		self.__page_down_button.set_selection_effect(None)
		self.__page_up_button = self.add.button("▲", self.__on_page_up_click, font_name="Monospace", font_size=display_info.font_size.small)
		self.__page_up_button.set_selection_effect(None)
		self.__page_frame.pack(self.__page_down_button, ALIGN_RIGHT)
		self.__page_frame.pack(self.__page_up_button, ALIGN_RIGHT)

		self.__item_name_label: Label = self.add.label("", font_size=display_info.font_size.normal, wordwrap=True) # type: ignore
		self.__item_desc_label: Label = self.add.label("", font_size=display_info.font_size.small, wordwrap=True) # type: ignore

		self.__close_button = self.add.button(
			_("menu_inventory_close", "Close"),
			self.__on_close_click,
			cursor=self.__pacab_game.theme.cursors.cursor_hover,
			font_size=display_info.font_size.normal,
			wordwrap=True,
		)
		self.inspect_button = self.add.button(
			_("menu_inventory_inspect", "Inspect"),
			self.__inspect_menu,
			cursor=self.__pacab_game.theme.cursors.cursor_hover,
			font_size=display_info.font_size.normal,
		)
		self.__combine_button = self.add.button(
			_("menu_inventory_combine", "Combine"),
			self.__on_combine_click,
			cursor=self.__pacab_game.theme.cursors.cursor_hover,
			font_size=display_info.font_size.normal,
		)

		self.inspect_button.hide()
		self.__combine_button.hide()

		if display_info.inventory_menu.is_portrait:
			image_frame_w = image_frame_h = math.floor(self.__close_button.get_height() * 2.4)
		else:
			image_frame_w = display_info.inventory_menu.right_pane_width
			image_frame_h = math.floor(display_info.inventory_menu.right_pane_width * 0.75)
		self.__image_frame = self.add.frame_h(image_frame_w, image_frame_h, padding=0)

		if display_info.inventory_menu.is_portrait:
			outer_frame.pack(self.__table)
			outer_frame.pack(self.__page_frame)
			outer_frame.pack(self.__item_name_label)
			outer_frame.pack(self.__item_desc_label)
			outer_frame.pack(self.__close_button, align=ALIGN_CENTER)
			outer_frame.pack(self.inspect_button, align=ALIGN_CENTER)
			outer_frame.pack(self.__combine_button, align=ALIGN_CENTER)
			outer_frame.pack(self.__image_frame, align=ALIGN_CENTER)
		elif left_pane_frame and right_pane_frame:
			left_pane_frame.pack(self.__table)
			left_pane_frame.pack(self.__page_frame)
			left_pane_frame.pack(self.__item_name_label)
			left_pane_frame.pack(self.__item_desc_label)
			right_pane_frame.pack(self.__close_button, align=ALIGN_CENTER)
			right_pane_frame.pack(self.inspect_button, align=ALIGN_CENTER)
			right_pane_frame.pack(self.__combine_button, align=ALIGN_CENTER)
			right_pane_frame.pack(self.add.vertical_margin(display_info.font_size.small))
			right_pane_frame.pack(self.__image_frame, align=ALIGN_CENTER)
			outer_frame.pack(left_pane_frame)
			outer_frame.pack(right_pane_frame)

	def refresh(self) -> None:
		self.select_widget(None)
		self.__refresh_table()

		game_state = self.__get_game_state()
		if len(game_state.items) > (self.__display_info.inventory_menu.table_row_num_cols) * 2:
			self.__page_frame.show()
		else:
			self.__page_frame.hide()

		self.force_surface_update()
	
	def select_item(self, item: InventoryItem) -> None:
		game_state = self.__get_game_state()

		self.selected_item = item.name

		self.__close_button.set_title(f"{_("menu_inventory_take", "Take")} {_(item.title)}")
		self.__item_name_label.set_title(_(item.title))
		self.__item_desc_label.set_title(_(item.inventory_message) if item.inventory_message else "")
		self.__item_desc_label.set_background_color(self.__pacab_game.theme.inventory_bg_color_alt) # type: ignore

		if self.__item_image:
			self.remove_widget(self.__item_image)
			self.__item_image = None

		max_width = self.__image_frame.get_width()
		max_height = self.__image_frame.get_height()

		image = pygame_menu.BaseImage(io.BytesIO(item.images[0][1]))
		scale = max_height / image.get_height()
		image = image.scale(scale, scale)
		if image.get_width() > max_width: 
			scale = max_width / image.get_width()
			image = image.scale(scale, scale)

		self.__item_image = self.add.image(image, padding=0)
		self.__image_frame.pack(self.__item_image, align=ALIGN_CENTER)

		self.inspect_button.hide()
		if item.show_inspect:
			self.inspect_button.show()

		self.__combine_button.hide()
		if len(game_state.items) > 1 and (item.combos and len(item.combos)):
			self.__combine_button.show()

		self.__inspect_menu.set_selected_item(item)
		
		self.refresh()

	def unselect_item(self) -> None:
		self.selected_item = None
		self.__close_button.set_title(_("menu_inventory_close", "Close"))
		self.__item_name_label.set_title("")
		self.__item_desc_label.set_title("")
		self.__item_desc_label.set_background_color(None)
		if self.__item_image:
			self.remove_widget(self.__item_image)
			self.__item_image = None
		self.inspect_button.hide()
		self.__combine_button.hide()
		self.__is_combining = False
		self.refresh()

	def reset_page(self) -> None:
		self.__page_skip = 0

	def __clear_table(self) -> None:
		old_rows = self.__table.clear()
		for old_row in old_rows:
			old_frames = old_row.clear()
			for old_frame in old_frames:
				old_buttons = old_frame.clear()
				for old_button in old_buttons:
					self.select_widget(self.__close_button) # Somehow this prevents a stack overflow in the menu where the button re-selects itself over and over
					self.remove_widget(old_button)

	def __combine_items(self, item1: InventoryItem, item2: InventoryItem) -> None:
		self.__is_combining = False

		combo = None
		if item1.combos:
			for c in item1.combos:
				if c.with_item == item2.name:
					combo = c
					break
		if not combo:
			if item2.combos:
				for c in item2.combos:
					if c.with_item == item1.name:
						combo = c
						break
		if combo:
			game_state: GameState = self.__get_game_state()
			game_state.items.remove(item1.name)
			game_state.items.remove(item2.name)
			game_state.items.append(combo.to_item)
			game_state.dead_items.append(item1.name)
			game_state.dead_items.append(item2.name)
			self.refresh()
			if combo.sound:
				pygame.event.post(pygame.event.Event(PLAY_SOUND, { "sound": combo.sound })) 

		self.unselect_item()

	def __on_close_click(self) -> None:
		self.__is_combining = False
		if self.selected_item:
			game_state = self.__get_game_state()
			game_state.selected_item = self.selected_item
		pygame.event.post(pygame.event.Event(INVENTORY_MENU_CLOSE_CLICKED))
	
	def __on_combine_click(self) -> None:
		self.__is_combining = True

	def __on_item_click(self, item: InventoryItem)-> None:
		if self.selected_item == item.name:
			self.unselect_item()
		elif self.__is_combining and self.selected_item:
			selected_item = self.__pacab_game.get_item(self.selected_item)
			self.__combine_items(selected_item, item)
		else:
			self.select_item(item)

	def __on_page_up_click(self) -> None:
		if self.__page_skip > 0:
			self.__page_skip -= self.__display_info.inventory_menu.table_row_num_cols
			self.__refresh_table()

	def __on_page_down_click(self) -> None:
		if self.__page_skip + (NUM_ROWS * self.__display_info.inventory_menu.table_row_num_cols) < len(self.__get_game_state().items):
			self.__page_skip += self.__display_info.inventory_menu.table_row_num_cols
			self.__refresh_table()

	def __refresh_table(self) -> None:
		self.disable_render()

		self.__clear_table()
		game_state = self.__get_game_state()
		cell_index = 0
		found_selected_item = False
		for _ in range(NUM_ROWS):
			row = self.add.frame_h(self.__table.get_width(False), self.__display_info.inventory_menu.table_row_height, padding=0)
			for _ in range(self.__display_info.inventory_menu.table_row_num_cols):
				item_index = self.__page_skip + cell_index
				if item_index >= len(game_state.items): break
				if cell_index > NUM_ROWS * self.__display_info.inventory_menu.table_row_num_cols: break

				item = self.__pacab_game.get_item(game_state.items[item_index])
				image = pygame_menu.BaseImage(io.BytesIO(item.images[0][1]))
				scale = self.__display_info.inventory_menu.table_row_height / image.get_height()
				image = image.scale(scale, scale)
				if image.get_width() > self.__display_info.inventory_menu.table_row_height:
					scale = self.__display_info.inventory_menu.table_row_height / image.get_width()
					image = image.scale(scale, scale)

				image_frame = self.add.frame_h(
					self.__display_info.inventory_menu.table_row_height,
					self.__display_info.inventory_menu.table_row_height,
					padding=0,
				)
				if not found_selected_item and item.name == self.selected_item:
					found_selected_item = True
					image_frame.set_background_color(self.__pacab_game.theme.inventory_bg_color)

				image_button = self.add.banner(
					image,
					self.__on_item_click,
					item,
					cursor=self.__pacab_game.theme.cursors.cursor_hover,
					padding=self.__get_cell_padding(image, self.__display_info.inventory_menu.table_row_height),
					selection_effect=None,
				)

				image_frame.pack(image_button)
				row.pack(image_frame)
				cell_index += 1

			self.__table.pack(row)

		self.enable_render()

	def __get_cell_padding(self, image: BaseImage, cell_width: int) -> tuple[int, int, int, int]:
		t = r = b = l = 0
		if image.get_width() < cell_width:
			r = l = math.floor((cell_width - image.get_width()) / 2)
		elif image.get_height() < cell_width:
			t = b = math.floor((cell_width - image.get_height()) / 2)
		return (t, r, b ,l)
