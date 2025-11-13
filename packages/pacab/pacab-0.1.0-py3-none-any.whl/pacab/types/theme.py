import math

import pygame_menu
import pygame_menu.font

from pacab.types.cursorset import CursorSet


DEFAULT_BG_COLOR = (0, 0, 0)
DEFAULT_MENU_BORDER_WIDTH = 0
DEFAULT_TITLE_BG_COLOR = (0, 0, 0)
DEFAULT_TITLE_FONT_COLOR = (255, 255, 255)
DEFAULT_TITLE_FONT = "Courier"
DEFAULT_TITLE_INLINE = True
DEFAULT_TITLEBAR_STYLE = "MENUBAR_STYLE_NONE"
DEFAULT_WIDGET_FONT_COLOR = (220, 220, 220)
DEFAULT_WIDGET_FONT = "Courier"
DEFAULT_CURSOR_DEFAULT = "SYSTEM_CURSOR_ARROW"
DEFAULT_CURSOR_HOVER = "SYSTEM_CURSOR_HAND"
DEFAULT_CURSOR_CLICK = "SYSTEM_CURSOR_ARROW"

class Theme:
	fonts = [
		"FONT_8BIT",
		"FONT_BEBAS",
		"FONT_COMIC_NEUE",
		"FONT_DIGITAL",
		"FONT_FRANCHISE",
		"FONT_FIRACODE",
		"FONT_FIRACODE_BOLD",
		"FONT_FIRACODE_BOLD_ITALIC",
		"FONT_FIRACODE_ITALIC",
		"FONT_HELVETICA",
		"FONT_MUNRO",
		"FONT_NEVIS",
		"FONT_OPEN_SANS",
		"FONT_OPEN_SANS_BOLD",
		"FONT_OPEN_SANS_ITALIC",
		"FONT_OPEN_SANS_LIGHT",
		"FONT_PT_SERIF",
	]

	menubar_styles = [
		"MENUBAR_STYLE_ADAPTIVE",
		"MENUBAR_STYLE_SIMPLE",
		"MENUBAR_STYLE_TITLE_ONLY",
		"MENUBAR_STYLE_TITLE_ONLY_DIAGONAL",
		"MENUBAR_STYLE_UNDERLINE",
		"MENUBAR_STYLE_UNDERLINE_TITLE",
		"MENUBAR_STYLE_NONE",
	]

	def __init__(
		self,
		game_bg_color: tuple,
		game_bg_image: bytearray | None,

		main_menu_bg_color: tuple,
		main_menu_bg_image: bytearray | None,
		main_menu_title_inline: bool,
		main_menu_titlebar_style: str,
		main_menu_title_bg_color: tuple,
		main_menu_title_font_color: tuple,
		main_menu_title_font: str,
		main_menu_font_color: tuple,
		main_menu_font: str,

		game_controls_bg_color: tuple,
		game_controls_bg_image: bytearray | None,
		game_controls_font_color: tuple,
		game_controls_font: str,

		pause_menu_bg_color: tuple,
		pause_menu_bg_image: bytearray | None,
		pause_menu_titlebar_style: str,
		pause_menu_title_bg_color: tuple,
		pause_menu_title_font_color: tuple,
		pause_menu_title_font: str,
		pause_menu_font_color: tuple,
		pause_menu_font: str,

		dialog_bg_color: tuple,
		dialog_bg_image: bytearray | None,
		dialog_titlebar_style: str,
		dialog_title_bg_color: tuple,
		dialog_title_font_color: tuple,
		dialog_title_font: str,
		dialog_font_color: tuple,
		dialog_font_color_alt: tuple,
		dialog_font: str,

		inventory_bg_color: tuple,
		inventory_bg_color_alt: tuple,
		inventory_bg_image: bytearray | None,
		inventory_title_bg_color: tuple,
		inventory_title_font_color: tuple,
		inventory_title_font: str,
		inventory_font_color: tuple,
		inventory_font: str,

		cursors: CursorSet,
	) -> None:
		self.game_bg_color = game_bg_color
		self.game_bg_image = game_bg_image

		self.main_menu_bg_color = main_menu_bg_color
		self.main_menu_bg_image = main_menu_bg_image
		self.main_menu_title_inline = main_menu_title_inline
		self.main_menu_titlebar_style = get_pygame_menu_menubar_style(main_menu_titlebar_style)
		self.main_menu_title_bg_color = main_menu_title_bg_color
		self.main_menu_title_font_color = main_menu_title_font_color
		self.main_menu_title_font = main_menu_title_font
		self.main_menu_font_color = main_menu_font_color
		self.main_menu_font = main_menu_font

		self.game_controls_bg_color = game_controls_bg_color
		self.game_controls_bg_image = game_controls_bg_image
		self.game_controls_titlebar_style = get_pygame_menu_menubar_style("MENUBAR_STYLE_NONE")
		self.game_controls_font_color = game_controls_font_color
		self.game_controls_font = game_controls_font

		self.pause_menu_bg_color = pause_menu_bg_color
		self.pause_menu_bg_image = pause_menu_bg_image
		self.pause_menu_titlebar_style = get_pygame_menu_menubar_style(pause_menu_titlebar_style)
		self.pause_menu_title_bg_color = pause_menu_title_bg_color
		self.pause_menu_title_font_color = pause_menu_title_font_color
		self.pause_menu_title_font = pause_menu_title_font
		self.pause_menu_font_color = pause_menu_font_color
		self.pause_menu_font = pause_menu_font

		self.dialog_bg_color = dialog_bg_color
		self.dialog_bg_image = dialog_bg_image
		self.dialog_titlebar_style = get_pygame_menu_menubar_style(dialog_titlebar_style)
		self.dialog_title_bg_color = dialog_title_bg_color
		self.dialog_title_font_color = dialog_title_font_color
		self.dialog_title_font = dialog_title_font
		self.dialog_font_color = dialog_font_color
		self.dialog_font_color_alt = dialog_font_color_alt
		self.dialog_font = dialog_font

		self.inventory_bg_color = inventory_bg_color
		self.inventory_bg_color_alt = inventory_bg_color_alt
		self.inventory_bg_image = inventory_bg_image
		self.inventory_titlebar_style = get_pygame_menu_menubar_style("MENUBAR_STYLE_NONE")
		self.inventory_title_bg_color = inventory_title_bg_color
		self.inventory_title_font_color = inventory_title_font_color
		self.inventory_title_font = inventory_title_font
		self.inventory_font_color = inventory_font_color
		self.inventory_font = inventory_font

		self.cursors = cursors

	@staticmethod
	def get_font(font_name: str) -> str:
		if font_name == "FONT_8BIT": return pygame_menu.font.FONT_8BIT
		elif font_name == "FONT_BEBAS": return pygame_menu.font.FONT_BEBAS
		elif font_name == "FONT_COMIC_NEUE": return pygame_menu.font.FONT_COMIC_NEUE
		elif font_name == "FONT_DIGITAL": return pygame_menu.font.FONT_DIGITAL
		elif font_name == "FONT_FRANCHISE": return pygame_menu.font.FONT_FRANCHISE
		elif font_name == "FONT_FIRACODE": return pygame_menu.font.FONT_FIRACODE
		elif font_name == "FONT_FIRACODE_BOLD": return pygame_menu.font.FONT_FIRACODE_BOLD
		elif font_name == "FONT_FIRACODE_BOLD_ITALIC": return pygame_menu.font.FONT_FIRACODE_BOLD_ITALIC
		elif font_name == "FONT_FIRACODE_ITALIC": return pygame_menu.font.FONT_FIRACODE_ITALIC
		elif font_name == "FONT_HELVETICA": return pygame_menu.font.FONT_HELVETICA
		elif font_name == "FONT_MUNRO": return pygame_menu.font.FONT_MUNRO
		elif font_name == "FONT_NEVIS": return pygame_menu.font.FONT_NEVIS
		elif font_name == "FONT_OPEN_SANS": return pygame_menu.font.FONT_OPEN_SANS
		elif font_name == "FONT_OPEN_SANS_BOLD": return pygame_menu.font.FONT_OPEN_SANS_BOLD
		elif font_name == "FONT_OPEN_SANS_ITALIC": return pygame_menu.font.FONT_OPEN_SANS_ITALIC
		elif font_name == "FONT_OPEN_SANS_LIGHT": return pygame_menu.font.FONT_OPEN_SANS_LIGHT
		elif font_name == "FONT_PT_SERIF": return pygame_menu.font.FONT_PT_SERIF
		else: return font_name

	@staticmethod
	def darken_color(color: tuple) -> tuple:
		(r, g, b) = color
		a = 255 if len(color) < 4 else color[3]
		return (
			math.floor(r * .7),
			math.floor(g * .7),
			math.floor(b * .7),
			a,
		)

def get_pygame_menu_menubar_style(input: str | int) -> int:
	if isinstance(input, int): return input
	elif input == "MENUBAR_STYLE_ADAPTIVE": return pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE # type: ignore
	elif input == "MENUBAR_STYLE_SIMPLE": return pygame_menu.widgets.MENUBAR_STYLE_SIMPLE # type: ignore
	elif input == "MENUBAR_STYLE_TITLE_ONLY": return pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY # type: ignore
	elif input == "MENUBAR_STYLE_TITLE_ONLY_DIAGONAL": return pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL # type: ignore
	elif input == "MENUBAR_STYLE_UNDERLINE": return pygame_menu.widgets.MENUBAR_STYLE_UNDERLINE # type: ignore
	elif input == "MENUBAR_STYLE_UNDERLINE_TITLE": return pygame_menu.widgets.MENUBAR_STYLE_UNDERLINE_TITLE # type: ignore
	return pygame_menu.widgets.MENUBAR_STYLE_NONE # type: ignore
