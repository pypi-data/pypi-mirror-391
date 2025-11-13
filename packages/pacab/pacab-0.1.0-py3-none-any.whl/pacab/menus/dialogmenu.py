import pygame
import pygame_menu
from pygame_menu.locals import ALIGN_CENTER, ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL
from pygame_menu.widgets.widget.label import Label

from pacab.constants import *
from pacab.displayinfo import DisplayInfo
from pacab.gamestate import GameState
from pacab.logger import Logger
from pacab.menus.menutheme import get_menu_theme
from pacab.text import get_string as _
from pacab.types.condition import Condition
from pacab.types.pacabgame import PacabGame
from pacab.types.prompt import Prompt
from pacab.types.reply import Reply


class DialogMenu(pygame_menu.Menu):
	def __init__(
			self,
			title: str,
			dialog_name: str,
			prompt: Prompt,
			game_state: GameState,
			pacab_game: PacabGame,
			display_info: DisplayInfo,
			is_blocking: bool,
			after_event: pygame.event.Event | None = None
		) -> None:
		theme = get_menu_theme(
			pacab_game.theme.dialog_bg_color,
			pacab_game.theme.dialog_bg_image,
			pacab_game.theme.dialog_titlebar_style,
			pacab_game.theme.dialog_title_bg_color,
			pacab_game.theme.dialog_title_font_color,
			pacab_game.theme.dialog_title_font,
			pacab_game.theme.cursors.cursor_hover,
			pacab_game.theme.dialog_font_color,
			pacab_game.theme.dialog_font,
			display_info.widget_padding,
		)
		theme.scrollbar_color = pacab_game.theme.dialog_bg_color # type: ignore
		theme.scrollbar_cursor = pacab_game.theme.cursors.cursor_hover
		theme.scrollbar_slider_color = pacab_game.theme.dialog_font_color # type: ignore
		theme.scrollbar_slider_pad = 5
		theme.title_floating = True

		height = display_info.dialog_menu.height
		height += len(prompt.replies) * display_info.dialog_menu.button_height_increase
		height = display_info.dialog_menu.max_height if height > display_info.dialog_menu.max_height else height
		y = display_info.dialog_menu.bottom - height

		super().__init__(
			"",
			display_info.dialog_menu.width,
			height,
			center_content=(not bool(title)),
			position=(display_info.dialog_menu.x, y, False),
			theme=theme,
			enabled=False,
			verbose=False,
		)
		
		self.after_event = after_event
		self.is_blocking = is_blocking
		self.has_next_page = False

		self.__pacab_game = pacab_game
		self.__dialog_name = dialog_name
		self.__text_list = []
		self.__text_list_index = 0
		self.__reply_frame = None
		self.__show_separator = prompt.show_separator

		self.get_scrollarea().hide_scrollbars(ORIENTATION_HORIZONTAL)

		if title:
			title_label: Label = self.add.label(_(title), font_size=display_info.font_size.normal) # type: ignore
			title_frame = self.add.frame_h(display_info.dialog_menu.width, title_label.get_height(), padding=0)
			title_frame.pack(title_label)

		self.__label: Label = self.add.label("", font_size=display_info.font_size.small, wordwrap=True) # type: ignore

		if isinstance(prompt.text, list):
			self.has_next_page = True
			self.__text_list = prompt.text
			self.__label.set_title(_(prompt.text[self.__text_list_index])) # type: ignore
			self.__continue_text_button = self.add.button(
				_("menu_continue", "Continue"),
				self.on_continue_text_click,
				font_size=display_info.font_size.small,
			)
		else:
			self.__label.set_title(_(prompt.text)) # type: ignore

		if not prompt.replies or not len(prompt.replies):
			self.__continue_button = self.add.button(
				_("menu_continue", "Continue"),
				self.__on_continue_click,
				font_size=display_info.font_size.small,
			)
		else:
			self.__continue_button = None

			self.__separator = self.add.label("• • ● • •", font_size=10, padding=0)

			reply_frame_w = display_info.dialog_menu.width
			reply_frame_h = 10000 # Set to big initial size so Replies don't overflow
			self.__reply_frame = self.add.frame_v(reply_frame_w, reply_frame_h)
			reply_frame_h = 20 # Reset to 20 to give 20px padding under the final Reply

			replies_shown = 0
			for reply in prompt.replies:
				if Condition.check_conditions(game_state, reply.conditions, False):
					font_color = self.__pacab_game.theme.dialog_font_color_alt if self.__is_reply_used(game_state, reply) else self.__pacab_game.theme.dialog_font_color
					button = self.add.button(
						_(reply.text),
						self.__on_reply_click,
						reply,
						font_color=font_color,
						font_size=display_info.font_size.small,
						wordwrap=True,
					)
					self.__reply_frame.pack(button, align=ALIGN_CENTER)

					reply_frame_h += button.get_height()
					replies_shown += 1
				else:
					Logger.log(f"Reply will not be shown: '{reply.text}'.")


			if not self.__show_separator or replies_shown <= 1 or isinstance(prompt.text, list):
				self.__separator.hide() # type: ignore

			self.__reply_frame.resize(reply_frame_w, reply_frame_h) # Finally, resize the frame once we know the actual height

			self.get_scrollarea().scroll_to(ORIENTATION_VERTICAL, 0)

		if self.__text_list:
			if self.__continue_button: self.__continue_button.hide()
			elif self.__reply_frame: self.__reply_frame.hide()

	def on_continue_text_click(self) -> None:
		self.__text_list_index += 1
		self.__label.set_title(_(self.__text_list[self.__text_list_index]))
		if self.__text_list_index == len(self.__text_list) - 1:
			self.has_next_page = False
			self.__continue_text_button.hide()
			if self.__continue_button: self.__continue_button.show()
			elif self.__reply_frame:
				if self.__show_separator:
					self.__separator.show() # type: ignore
				self.__reply_frame.show()

	def __on_continue_click(self) -> None:
		pygame.event.post(pygame.event.Event(DIALOG_CONTINUE))

	def __on_reply_click(self, reply: Reply) -> None:
		pygame.event.post(pygame.event.Event(DIALOG_REPLY, { "reply": reply }))

	def __is_reply_used(self, game_state: GameState, reply: Reply) -> bool:
		reply_key = self.__dialog_name + "." + reply.name
		return reply_key in game_state.dead_replies
