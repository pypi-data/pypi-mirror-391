import pygame
from pygame.locals import (
	RLEACCEL,
)

from pacab.constants import ANIMATION_COMPLETE
from pacab.displayinfo import DisplayInfo
from pacab.types.animation import Animation
from pacab.types.pacabgame import PacabGame


class AnimationSurface(pygame.sprite.Sprite):
	def __init__(self, animation: Animation, display_info: DisplayInfo, pacab_game: PacabGame):
		super(AnimationSurface, self).__init__()

		self.animation = animation
		self.blur_radius = 0
		self.start_y = None
		self.__clock = 0
		self.__display_info = display_info
		self.__frame_index = 0
		self.__pacab_game = pacab_game
		self.__play_count = 0

		if not animation.frames:
			animation.set_frames(self.__pacab_game.get_animation_frames(animation.filename))

		self.__create_surface()
		
		if not self.animation.repeat:
			pygame.event.post(pygame.event.Event(ANIMATION_COMPLETE, { "animation": self.animation.id }))
	
	def update(self, *args: list, **kwargs: dict) -> None:
		super().update(args, kwargs)

		time = args[0] if isinstance(args[0], float) else 1
		self.__clock += time
		if self.__clock > self.animation.duration:
			self.__clock = 0
			rect = args[1] if len(args) > 1 and isinstance(args[1], pygame.Rect) else None
			self.__create_surface(rect)
	
	def __create_surface(self, rect: pygame.Rect | None = None) -> None:
		self.image = self.__load_next_frame()
		rect = rect if rect else pygame.Rect(self.animation.x, self.animation.y, self.animation.width, self.animation.height)
		self.rect = self.image.get_rect()

		# Draw borders for debugging
		if self.__pacab_game.debug_mode:
			pygame.draw.rect(self.image, (0, 0, 0), self.image.get_rect(), 2)
		
		self.rect.topleft = rect.topleft
	
	def __load_next_frame(self) -> pygame.Surface:
		assert(isinstance(self.animation.frames, list))
		frame = self.animation.frames[self.__frame_index]
		colorkey = (0, 0, 0) if frame.has_white else (255, 255, 255)
		
		self.__frame_index += 1
		if self.__frame_index >= len(self.animation.frames):
			if self.animation.hold_final_frame:
				self.__frame_index = len(self.animation.frames) - 1
			else:
				self.__frame_index = 0
				self.__play_count += 1
				if self.animation.loops != -1 and (self.__play_count >= self.animation.loops):
					self.kill()

		surface = pygame.image.frombytes(frame[0], frame[1], "RGBA").convert_alpha()
		self.animation._scale(self.__display_info)
		surface = pygame.transform.scale(surface, (self.animation.width, self.animation.height))
		surface.set_colorkey(colorkey, RLEACCEL)
		surface.set_alpha(self.animation.alpha)

		if self.blur_radius:
			surface = pygame.transform.box_blur(surface, self.blur_radius)

		return surface
