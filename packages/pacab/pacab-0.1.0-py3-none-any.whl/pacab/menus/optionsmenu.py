import pygame
import pygame.event
import pygame_menu
import pygame_menu.events
from pygame_menu.locals import ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL
from pygame_menu.widgets.widget.toggleswitch import ToggleSwitch

from pacab.constants import OPT_UPDATE_ENABLE_MUSIC, OPT_UPDATE_ENABLE_SOUND, PROG_STATE_MAINMENU, PROG_STATE_OPTIONSMENU, PROG_STATE_PAUSED, PROG_STATE_PAUSEOPTIONS, UPDATE_PROGRAM_STATE
from pacab.displayinfo import DisplayInfo
from pacab.menus.menutheme import get_menu_theme
from pacab.options import Options
from pacab.text import get_string as _
from pacab.types.pacabgame import PacabGame


class OptionsMenu(pygame_menu.Menu):
	def __init__(self, pacab_game: PacabGame, display_info: DisplayInfo, is_paused: bool) -> None:
		if is_paused:
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
				_("menu_options", "Options"),
				display_info.pause_menu.width,
				display_info.pause_menu.height,
				position=(display_info.pause_menu.x, display_info.pause_menu.y, False),
				theme=theme,
				enabled=False,
				verbose=False,
			)
		else:
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
			if pacab_game.theme.main_menu_title_inline: theme.title_floating = True
			top_title = _("menu_options", "Options") if not pacab_game.theme.main_menu_title_inline else ""

			super().__init__(top_title, display_info.window.width, display_info.window.height, theme=theme, verbose=False)

			if pacab_game.theme.main_menu_title_inline:
				self.add.label(
					_("menu_options", "Options"),
					background_color=pacab_game.theme.main_menu_title_bg_color,
					font_name=pacab_game.theme.main_menu_title_font,
					font_color=pacab_game.theme.main_menu_title_font_color,
					font_size=display_info.font_size.title,
				)

		self.__pacab_game = pacab_game
		self.__options = Options.load_options(self.__pacab_game.short_name)
		self.__is_paused = is_paused

		self._onbeforeopen = lambda *_: self.__refresh()
		self._onreset = lambda *_: self.__on_back_clicked()
		self.get_scrollarea().hide_scrollbars(ORIENTATION_HORIZONTAL)
		self.get_scrollarea().hide_scrollbars(ORIENTATION_VERTICAL)

		self.__music_toggle: ToggleSwitch = self.add.toggle_switch(
			_("menu_options_music", "Music"),
			self.__options.enable_music,
			self.__on_update,
			font_size=display_info.font_size.normal,
		)
		self.__music_toggle.set_selection_effect(None)
		self.__sound_toggle: ToggleSwitch = self.add.toggle_switch(
			_("menu_options_sound", "Sound"),
			self.__options.enable_sound,
			self.__on_update,
			font_size=display_info.font_size.normal,
		)
		self.__sound_toggle.set_selection_effect(None)
		self.__back_button = self.add.button(_("menu_back", "Back"), pygame_menu.events.BACK, font_size=display_info.font_size.normal)

	def __on_back_clicked(self) -> None:
		enable_music = self.__music_toggle.get_value()
		enable_sound = self.__sound_toggle.get_value()

		Options(enable_music, enable_sound).save_options(self.__pacab_game.short_name)

		if self.__is_paused:
			pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_PAUSED }))
			if self.__options.enable_music != enable_music:
				pygame.event.post(pygame.event.Event(OPT_UPDATE_ENABLE_MUSIC, { "enable_music": enable_music }))
			if self.__options.enable_sound != enable_sound:
				pygame.event.post(pygame.event.Event(OPT_UPDATE_ENABLE_SOUND, { "enable_sound": enable_sound }))
		else:
			pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_MAINMENU }))
	
	def __on_update(self, _) -> None:
		enable_music = self.__music_toggle.get_value()
		enable_sound = self.__sound_toggle.get_value()
		if self.__options.enable_music != enable_music or self.__options.enable_sound != enable_sound:
			self.__back_button.set_title(_("menu_apply", "Apply"), )
		else:
			self.__back_button.set_title(_("menu_back", "Back"))

	def __refresh(self) -> None:
		if self.__is_paused:
			pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_PAUSEOPTIONS }))
		else:
			pygame.event.post(pygame.event.Event(UPDATE_PROGRAM_STATE, { "state": PROG_STATE_OPTIONSMENU }))

		self.__options = Options.load_options(self.__pacab_game.short_name)
		self.__music_toggle.set_value(self.__options.enable_music)
		self.__sound_toggle.set_value(self.__options.enable_sound)
		self.__back_button.set_title(_("menu_back", "Back"))
