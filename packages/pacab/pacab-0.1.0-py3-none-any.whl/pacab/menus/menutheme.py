import io
import pygame
import pygame_menu

from pacab.types.theme import Theme


def get_menu_theme(
		bg_color: tuple,
		bg_image: bytearray | None,
		title_bar_style: int,
		title_bg_color: tuple,
		title_font_color: tuple,
		title_font: str,
		widget_cursor: int | pygame.Cursor,
		widget_font_color: tuple,
		widget_font: str,
		widget_padding: int,
	) -> pygame_menu.Theme:

	background = pygame_menu.BaseImage(io.BytesIO(bg_image)) if bg_image else bg_color

	return pygame_menu.Theme(
		background_color = background,
		title_bar_style = title_bar_style,
		title_background_color = title_bg_color,
		title_close_button = False,
		title_font_color = title_font_color,
		title_font = Theme.get_font(title_font),
		widget_cursor = widget_cursor,
		widget_font_color = widget_font_color,
		widget_font = Theme.get_font(widget_font),
		widget_padding = widget_padding,
	)
