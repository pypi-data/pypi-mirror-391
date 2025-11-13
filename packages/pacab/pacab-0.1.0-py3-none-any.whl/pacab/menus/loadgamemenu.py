from datetime import datetime
from typing import Callable

import pygame.event
import pygame_menu
import pygame_menu.events
from pygame_menu.locals import ALIGN_CENTER, ALIGN_RIGHT
from pygame_menu.widgets.widget.label import Label

from pacab.constants import PROG_STATE_LOADMENU, PROG_STATE_MAINMENU, UPDATE_PROGRAM_STATE
from pacab.displayinfo import DisplayInfo
from pacab.gamesave import GameSave
from pacab.menus.menutheme import get_menu_theme
from pacab.text import get_string as _
from pacab.types.pacabgame import PacabGame


class LoadGameMenu(pygame_menu.Menu):
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

		super().__init__("", display_info.window.width, display_info.window.height, theme=theme, verbose=False)

		self.__pacab_game = pacab_game
		self.__display_info = display_info
		self.__is_loading_game = False
		self.__new_game_callback = new_game_callback
		self.__num_saves = 0
		self.__selected_game_save: GameSave | None = None
		self.__page_size = self.__display_info.load_menu.page_size
		self.__page_skip = 0

		self._onbeforeopen = lambda *_: self.refresh()
		self._onreset = lambda *_: self.__onclose()

		self.__saves_frame = self.add.frame_v(display_info.window.width, display_info.load_menu.frame_height, cursor=pacab_game.theme.cursors.cursor_default)

		self.__page_frame = self.add.frame_h(display_info.load_menu.page_frame_width, 1, padding=0)
		self.__page_frame._relax = True
		self.__page_down_button = self.add.button("▼", self.__on_page_down_click, font_name="Monospace", font_size=display_info.font_size.small)
		self.__page_up_button = self.add.button("▲", self.__on_page_up_click, font_name="Monospace", font_size=display_info.font_size.small)
		self.__page_frame.pack(self.__page_down_button, ALIGN_RIGHT)
		self.__page_frame.pack(self.__page_up_button, ALIGN_RIGHT)

		self.__empty_label: Label = self.add.label("", font_size=display_info.font_size.normal) # type: ignore

		self.__load_button = self.add.button(_("menu_load", "Load"), self.__load_game, font_size=display_info.font_size.normal)
		self.__load_button.hide()

		self.add.button(_("back", "Back"), pygame_menu.events.BACK, font_size=display_info.font_size.normal)

	def refresh(self) -> None:
		pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_LOADMENU }))

		self.disable_render()

		self.__clear_saves_frame()

		game_saves = GameSave.load_saved_games(self.__pacab_game.short_name)
		self.__num_saves = len(game_saves)

		button_total_height = 0

		for row_index in range(self.__page_size):
			save_index = self.__page_skip + row_index
			if save_index >= len(game_saves): break

			game_save = game_saves[save_index]
			button = self.add.button(
				f"{game_save.name} • {datetime.fromisoformat(str(game_save.date)).strftime("%Y-%m-%d %H:%M")}",
				self.__select_game_save,
				game_save,
				font_size=self.__display_info.font_size.normal,
				wordwrap=True,
			)
			self.__saves_frame.pack(button, ALIGN_CENTER)

			# It's possible that the buttons can get too tall, so we need to check and decrease `self.__page_size` if that happens
			if row_index + 1 < self.__page_size:
				button_total_height += button.get_height()
				
				# Adding button height again to check for the next button to be added. The 10 is there because it helps somehow.
				if (button_total_height + button.get_height()) > self.__display_info.load_menu.frame_height - 10: 
					self.__page_size -= 1
					break
	
		if self.__num_saves > self.__page_size:
			self.__page_frame.show()
		else:
			self.__page_frame.hide()

		self.__unselect_game_save()

		self.enable_render()

	def __clear_saves_frame(self) -> None:
		old_rows = self.__saves_frame.clear()
		for old_row in old_rows:
			self.remove_widget(old_row)

	def __load_game(self) -> None:
		if not self.__selected_game_save: return
		self.__is_loading_game = True
		self.reset(1)
		self.__is_loading_game = False
		self.__new_game_callback(self.__selected_game_save.game_state)

	def __onclose(self) -> None:
		if not self.__is_loading_game:
			pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_MAINMENU }))

	def __on_page_up_click(self) -> None:
		if self.__page_skip > 0:
			self.__page_skip -= 1
			self.refresh()

	def __on_page_down_click(self) -> None:
		if self.__page_skip + self.__page_size < self.__num_saves:
			self.__page_skip += 1
			self.refresh()

	def __select_game_save(self, game_save: GameSave) -> None:
		self.__selected_game_save = game_save
		self.__load_button.show()
		self.__empty_label.hide()

	def __unselect_game_save(self) -> None:
		self.__selected_game_save = None
		self.__load_button.hide()
		self.__empty_label.show()
