import math

from pacab.displayinfo import DisplayInfo


class Box:
	def __init__(self, x: int, y: int, width: int, height: int) -> None:
		self.x = x
		self.y = y
		self.width = width
		self.height = height

	def _scale(self, display_info: DisplayInfo):
		self.x = display_info.game_window.x + math.floor(self.x * display_info.scale)
		self.y = display_info.game_window.y + math.floor(self.y * display_info.scale)
		self.width = math.floor(self.width * display_info.scale)
		self.height = math.floor(self.height * display_info.scale)
