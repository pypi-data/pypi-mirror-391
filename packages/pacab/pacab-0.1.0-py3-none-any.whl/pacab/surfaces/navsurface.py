import pygame
from pygame.locals import (
	RLEACCEL,
)

from pacab.displayinfo import DisplayInfo
from pacab.types.navigation import Navigation
from pacab.types.pacabgame import PacabGame


class NavSurface(pygame.sprite.Sprite):
	def __init__(self, navigation: Navigation, display_info: DisplayInfo, pacab_game: PacabGame):
		super(NavSurface, self).__init__()

		self.nav = navigation

		navigation._scale(display_info)
		rect = pygame.Rect(navigation.x, navigation.y, navigation.width, navigation.height)
		self.image = pygame.Surface((navigation.width, navigation.height))
		self.image.fill((255, 255, 255))
		self.image.set_colorkey((255, 255, 255), RLEACCEL)
		self.rect = self.image.get_rect()

		# Draw borders for debugging
		if pacab_game.debug_mode:
			pygame.draw.rect(self.image, (255, 0, 0), self.rect, 2)

		self.rect.topleft = rect.topleft
