import math
from collections import namedtuple

import pygame


# Landscape
# +-------------------------------------+
# |+---------------------------+ +----+ +
# ||                           | | B1 | +
# ||           A               | +----+ +
# ||                           | | B2 | +
# |+---------------------------+ +----+ +
# |                                     +
# +-------------------------------------+
# A = Background images are 576x320, scaled to fill as large of an area as possible.
#     This is meant to take up 80% of the width of a 720x320 screen
# B = Stack buttons vertically in the remaining 20% of the screen.
#
# Portrait
# +---------------+
# |+-------------+|
# ||      A      ||
# ||             ||
# |+-------------+|
# |    | B1 |     |
# |               |
# |    | B2 |     |
# |               |
# +---------------+
# Same as above, but the game area is scaled to the top, buttons underneath

SCENE_W = 576
SCENE_H = 320

Box = namedtuple("Box", ["x", "y", "width", "height"])
DialogMenu = namedtuple("DialogMenu", ["x", "y", "width", "height", "max_height", "bottom", "button_height_increase"])
FontSize = namedtuple("FontSize", ["small", "normal", "title"])
InventoryMenu = namedtuple(
	"InventoryMenu",
	["x", "y", "width", "height", "left_pane_width", "left_pane_width_padded", "right_pane_width",
		"table_width", "table_height", "table_row_height", "table_row_num_cols", "is_portrait"]
)
LoadMenu = namedtuple("LoadMenu", ["frame_height", "page_frame_width", "page_size"])

class DisplayInfo:
	def __init__(self):
		display_info = pygame.display.Info()

		self.window = Box(0, 0, display_info.current_w, display_info.current_h)

		is_portrait = self.window.height > self.window.width

		# Misc
		self.widget_padding = math.floor(self.window.height / 45)

		# Fonts
		normal_font = math.floor((self.window.height if is_portrait else self.window.width) / 46)
		small_font = math.floor(normal_font * 0.75)
		title_font = math.floor(normal_font * 1.5)
		self.font_size = FontSize(small_font, normal_font, title_font)

		# Load Menu
		self.load_menu = LoadMenu(math.floor(self.window.height * 0.6), math.floor(self.window.width * 0.9), 6)

		# Pause Menu
		if is_portrait:
			pause_x = math.floor(self.window.width / 10)
			pause_y = math.floor(self.window.height / 20)
			pause_width = math.floor(self.window.width * 0.8)
			pause_height = math.floor(self.window.height * 0.9)
		else:
			pause_x = math.floor(self.window.width / 10)
			pause_y = math.floor(self.window.height / 10)
			pause_width = math.floor(self.window.width * 0.8)
			pause_height = math.floor(self.window.height * 0.8)
		self.pause_menu = Box(pause_x, pause_y, pause_width, pause_height)

		# Game Window
		if is_portrait:
			game_window_x = 0
			game_window_y = math.floor(self.window.height / 20)
			game_window_w = self.window.width
			self.scale = game_window_w / SCENE_W
			game_window_h = SCENE_H * self.scale
		else:
			game_window_max_w = math.floor(self.window.width * 0.8)
			game_window_max_h = self.window.height
			self.scale = game_window_max_w / SCENE_W
			game_window_w = math.floor(SCENE_W * self.scale)
			game_window_h = math.floor(SCENE_H * self.scale)
			if game_window_h > game_window_max_h:
				game_window_h = game_window_max_h
				self.scale = math.floor(game_window_max_h / SCENE_H)
				game_window_w = math.floor(SCENE_W * self.scale)
			game_window_x = 0
			if game_window_w < game_window_max_w: # Center horizontally
				game_window_x = math.floor((game_window_max_w - game_window_w) / 2)
			game_window_y = 0
			if game_window_h < game_window_max_h: # Center vertically
				game_window_y = math.floor((game_window_max_h - game_window_h) / 2)
		self.game_window = Box(game_window_x, game_window_y, game_window_w, game_window_h)

		# Game Controls Menu
		if is_portrait:
			game_controls_w = self.game_window.width
			game_controls_h = self.window.height - game_window_h
			game_controls_x = 0
			game_controls_y = self.game_window.y + self.game_window.height
		else:
			game_controls_w = self.window.width - self.game_window.width
			game_controls_h = self.window.height
			game_controls_x = self.game_window.width
			game_controls_y = 0
		self.game_controls = Box(game_controls_x, game_controls_y, game_controls_w, game_controls_h)

		# Inventory Menu
		if (is_portrait and self.window.width < 600) or (not is_portrait and self.window.height < 600): # On small screens, make InventoryMenu bigger
			if is_portrait:
				inv_x = math.floor(self.window.width / 20)
				inv_y = math.floor(self.window.height / 50)
				inv_width = math.floor(self.window.width * 0.9)
				inv_height = math.floor(self.window.height * 0.96)
				inv_table_width = inv_width
				inv_table_height = math.floor(inv_height * 0.4)
				inv_table_row_height = math.floor((inv_table_height - 40) * 0.3)
			else:
				inv_x = math.floor(self.window.width / 50)
				inv_y = math.floor(self.window.height / 20)
				inv_width = math.floor(self.window.width * 0.96)
				inv_height = math.floor(self.window.height * 0.9)
				inv_left_pane_width = math.floor(inv_width * 0.75)
				inv_left_pane_width_padded = inv_left_pane_width - 30
				inv_table_width = inv_left_pane_width_padded
				inv_table_height = math.floor((inv_height - 40) * 0.5)
				inv_table_row_height = math.floor((inv_table_height - 40) * 0.5)
		else:
			inv_x = pause_x
			inv_y = pause_y
			inv_width = pause_width
			inv_height = pause_height
			inv_left_pane_width = math.floor(inv_width * 0.75)
			inv_left_pane_width_padded = inv_left_pane_width - 30
			inv_table_width = inv_left_pane_width_padded
			inv_table_height = math.floor((inv_height - 40) * 0.5)
			inv_table_row_height = math.floor((inv_table_height - 40) * 0.5)
		inv_left_pane_width = math.floor((inv_width) * 0.75)
		inv_left_pane_width_padded = inv_left_pane_width - 30
		inv_right_pane_width = math.floor(inv_width * 0.25)
		inv_table_row_num_cols = math.floor((inv_table_width - 40) / inv_table_row_height) # 20 padding on table
		self.inventory_menu = InventoryMenu(
			inv_x,
			inv_y,
			inv_width,
			inv_height,
			inv_left_pane_width,
			inv_left_pane_width_padded,
			inv_right_pane_width,
			inv_table_width,
			inv_table_height,
			inv_table_row_height,
			inv_table_row_num_cols,
			is_portrait,
		)

		# Dialog Menu
		if is_portrait:
			dialog_button_height_increase = 10
			dialog_max_height = math.floor(self.window.height * 0.7)
			dialog_bottom = self.window.height
			dialog_width = self.window.width
			dialog_height = math.floor(self.window.height * 0.3)
			dialog_x = dialog_y = 0
		else:
			dialog_button_height_increase = 5
			dialog_max_height = math.floor(self.window.height * 0.6)
			if self.window.height < 800: # On small screens, make DialogMenu bigger
				dialog_bottom = math.floor(self.window.height * 0.96)
				dialog_width = math.floor(self.window.width * 0.96)
				dialog_height = math.floor(self.window.height * 0.4)
				dialog_x = math.floor(self.window.width * 0.02)
			else:
				dialog_bottom = math.floor(self.window.height * 0.9)
				dialog_width = math.floor(self.window.width * 0.6)
				dialog_height = math.floor(self.window.height * 0.3)
				dialog_x = math.floor(self.window.width * 0.2)
			dialog_y = dialog_bottom - dialog_height
		self.dialog_menu = DialogMenu(
			dialog_x,
			dialog_y,
			dialog_width,
			dialog_height,
			dialog_max_height,
			dialog_bottom,
			dialog_button_height_increase,
		)
