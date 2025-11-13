import io
import pygame
from pygame.locals import (
	RLEACCEL,
)

from pacab.displayinfo import DisplayInfo
from pacab.types.pacabgame import PacabGame
from pacab.types.sceneitem import SceneItem


class ItemSurface(pygame.sprite.Sprite):
	def __init__(self, item: SceneItem, display_info: DisplayInfo, pacab_game: PacabGame):
		super(ItemSurface, self).__init__()

		self.item = item

		image = pygame.image.load(io.BytesIO(item.image)).convert_alpha()

		item._scale(display_info)
		rect = pygame.Rect(item.x, item.y, item.width, item.height)
		self.image = pygame.transform.scale(image, (item.width, item.height))
		self.image.set_colorkey((255, 255, 255), RLEACCEL)
		self.rect = self.image.get_rect()

		# Draw borders for debugging
		if pacab_game.debug_mode:
			pygame.draw.rect(self.image, (0, 0, 255), self.rect, 2)

		self.rect.topleft = rect.topleft
