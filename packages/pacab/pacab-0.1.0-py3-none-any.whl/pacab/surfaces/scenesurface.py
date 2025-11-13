import io

import pygame

from pacab.displayinfo import DisplayInfo
from pacab.types.box import Box
from pacab.types.scene import Scene


class SceneSurface(pygame.sprite.Sprite):
	def __init__(self, scene: Scene, display_info: DisplayInfo, box: Box | None = None):
		super(SceneSurface, self).__init__()

		self.name = scene.name
		self.__display_info = display_info
		self.__scene = scene

		image = pygame.image.load(io.BytesIO(self.__scene.image)).convert_alpha()

		if box == None:
			rect = pygame.Rect(display_info.game_window.x, display_info.game_window.y, display_info.game_window.width, display_info.game_window.height)
			self.image = pygame.transform.scale(image, (display_info.game_window.width, display_info.game_window.height))
		else:
			rect = pygame.Rect(box.x, box.y, box.width, box.height)
			self.image = pygame.transform.scale(image, (box.width, box.height))
		self.rect = rect
		self.rect.topleft = rect.topleft
	
	def redraw(self) -> None:
		image = pygame.image.load(io.BytesIO(self.__scene.image)).convert_alpha()
		self.image = pygame.transform.scale(image, (self.__display_info.game_window.width, self.__display_info.game_window.height))

