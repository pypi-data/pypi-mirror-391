import pygame

from pacab.displayinfo import DisplayInfo
from pacab.surfaces.scenesurface import SceneSurface
from pacab.types.box import Box
from pacab.types.overlay import Overlay
from pacab.types.pacabgame import PacabGame


class OverlaySurface(SceneSurface):
	def __init__(self, overlay: Overlay, display_info: DisplayInfo, pacab_game: PacabGame):
		box = Box(overlay.x, overlay.y, overlay.width, overlay.height)
		box._scale(display_info)
		super().__init__(overlay, display_info, box)

		# Draw borders for debugging
		if pacab_game.debug_mode:
			pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 2) # type: ignore
