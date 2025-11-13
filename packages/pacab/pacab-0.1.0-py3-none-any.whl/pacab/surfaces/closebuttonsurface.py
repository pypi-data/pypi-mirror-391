import pygame
from pygame.locals import (
	RLEACCEL,
)


class CloseButtonSurface(pygame.sprite.Sprite):
	def __init__(self, width: int) -> None:
		super().__init__()

		self.image = pygame.Surface((width, width))
		self.image.fill((255, 255, 255))
		self.image.set_colorkey((255, 255, 255), RLEACCEL)
		pygame.draw.line(self.image, (255, 0, 0), (0, 0), (width, width), 2)
		pygame.draw.line(self.image, (255, 0, 0), (width, 0), (0, width), 2)
		self.rect = self.image.get_rect(topleft=(0, 0))
