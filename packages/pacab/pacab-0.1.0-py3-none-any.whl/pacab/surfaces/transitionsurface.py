import pygame
from pygame.locals import (
	RLEACCEL,
)

from pacab.constants import FPS, SCENE_TRANSITION_END
from pacab.displayinfo import DisplayInfo
from pacab.surfaces.scenesurface import SceneSurface
from pacab.types.scene import Scene
from pacab.types.scenetransition import *


class TransitionSurface(pygame.sprite.Sprite):
	def __init__(
			self,
			display_info: DisplayInfo,
			transition: SceneTransition,
			cur_scene_surface: SceneSurface,
			cur_static_surfaces: pygame.sprite.Group,
			cur_animation_surfaces: pygame.sprite.Group,
			next_scene: Scene,
			next_static_surfaces: pygame.sprite.Group,
			next_animation_surfaces: pygame.sprite.Group,
		):
		super(TransitionSurface, self).__init__()
		
		self.next_scene = SceneSurface(next_scene, display_info)
		self.next_animation_surfaces = next_animation_surfaces

		self.__display_info = display_info
		self.__transition = transition
		self.__cur_scene = cur_scene_surface
		self.__cur_static_surfaces = cur_static_surfaces
		self.__cur_animation_surfaces = cur_animation_surfaces
		self.__next_static_surfaces = next_static_surfaces
		self.__step_counter = 0
		
		rect = pygame.Rect(display_info.window.x, display_info.window.y, display_info.window.width, display_info.window.height)
		self.image = pygame.Surface((display_info.window.width, display_info.window.height))
		self.image.fill((255, 255, 255))
		self.image.set_colorkey((255, 255, 255), RLEACCEL)
		self.rect = self.image.get_rect()
		self.rect.topleft = rect.topleft

		if not self.__cur_scene.image or not self.next_scene.image: return

		if self.__transition.type == SCENE_TRANSITION_BLACK \
			or self.__transition.type == SCENE_TRANSITION_BLEND \
			or self.__transition.type == SCENE_TRANSITION_BLUR \
			or self.__transition.type == SCENE_TRANSITION_FADE_IN \
			or self.__transition.type == SCENE_TRANSITION_FADE_OUT \
			or self.__transition.type == SCENE_TRANSITION_FADE_OUT_IN:
			self.__cur_scene.image.set_alpha(255)
			self.next_scene.image.set_alpha(0)

	def update(self, *args: list, **kwargs: dict) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return
		super().update(args, kwargs)

		time = args[0] if isinstance(args[0], float) else 1
		cur_alpha = self.__cur_scene.image.get_alpha() or 255
		next_alpha = self.next_scene.image.get_alpha() or 0
		draw_cur_sprites = False
		draw_next_sprites = False

		if self.__transition.type == SCENE_TRANSITION_BLACK:
			self.__update_black()
		elif self.__transition.type == SCENE_TRANSITION_BLEND:
			draw_cur_sprites = True
			draw_next_sprites = True
			self.__update_blend(cur_alpha, next_alpha)
		elif self.__transition.type == SCENE_TRANSITION_BLUR:
			draw_cur_sprites = True
			draw_next_sprites = True
			self.__update_blur()
		elif self.__transition.type == SCENE_TRANSITION_FADE_IN:
			draw_next_sprites = True
			self.__update_fade_in(cur_alpha, next_alpha)
		elif self.__transition.type == SCENE_TRANSITION_FADE_OUT:
			draw_cur_sprites = True
			self.__update_fade_out(cur_alpha, next_alpha)
		elif self.__transition.type == SCENE_TRANSITION_FADE_OUT_IN:
			draw_cur_sprites = True
			draw_next_sprites = True
			self.__update_fade_out_in(cur_alpha, next_alpha)
		elif self.__transition.type == SCENE_TRANSITION_LEFT:
			draw_cur_sprites = True
			draw_next_sprites = True
			self.__update_left()
		elif self.__transition.type == SCENE_TRANSITION_RIGHT:
			draw_cur_sprites = True
			draw_next_sprites = True
			self.__update_right()
		elif self.__transition.type == SCENE_TRANSITION_UP:
			draw_cur_sprites = True
			draw_next_sprites = True
			self.__update_up()
		elif self.__transition.type == SCENE_TRANSITION_DOWN:
			draw_cur_sprites = True
			draw_next_sprites = True
			self.__update_down()

		if draw_cur_sprites:
			for sprite in self.__cur_static_surfaces:
				self.__cur_scene.image.blit(sprite.image, sprite.rect.move(0, -self.__display_info.game_window.y))
			for animation in self.__cur_animation_surfaces:
				animation.update(time, animation.rect)
				self.__cur_scene.image.blit(animation.image, animation.rect.move(0, -self.__display_info.game_window.y))

		if draw_next_sprites:
			for sprite in self.__next_static_surfaces:
				self.next_scene.image.blit(sprite.image, sprite.rect.move(0, -self.__display_info.game_window.y))
			for animation in self.next_animation_surfaces:
				animation.update(time)
				self.next_scene.image.blit(animation.image, animation.rect.move(0, -self.__display_info.game_window.y))

		self.image.blit(self.__cur_scene.image, self.__cur_scene.rect) # type: ignore
		self.image.blit(self.next_scene.image, self.next_scene.rect) # type: ignore

	def __update_black(self) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return

		num_frames = int(FPS / 2) if self.__transition.speed == "fast" else int(FPS * 1.3)

		if self.__step_counter < num_frames:
			self.__step_counter += 1
			self.__cur_scene.image.fill((0, 0, 0))
		else:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))
	
	def __update_blend(self, cur_alpha: int, next_alpha: int) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return

		num_frames = FPS * 2 if self.__transition.speed == "fast" else int(FPS * 0.8)

		self.__cur_scene.redraw()
		self.__cur_scene.image.set_alpha(cur_alpha)

		self.next_scene.redraw()
		self.next_scene.image.set_alpha(next_alpha)

		cur_alpha -= num_frames
		if cur_alpha < 0: cur_alpha = 0
		next_alpha += num_frames
		if next_alpha > 255: next_alpha = 255

		self.__cur_scene.image.set_alpha(cur_alpha)
		self.next_scene.image.set_alpha(next_alpha)
		
		if next_alpha == 255:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_blur(self) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return

		if self.__transition.speed == "fast":
			blur_radius = int(self.__step_counter * 1.5)
			blur_radius_reverse = 31 - blur_radius
			num_frames = 10
		else:
			blur_radius = self.__step_counter
			blur_radius_reverse = 31 - blur_radius
			num_frames = 15

		if self.__step_counter < num_frames:
			self.__step_counter += 1
			self.__cur_scene.redraw()
			self.__cur_scene.image = pygame.transform.box_blur(self.__cur_scene.image, blur_radius)
			for animation in self.__cur_animation_surfaces:
				animation.image = pygame.transform.box_blur(animation.image, blur_radius)
		elif self.__step_counter == num_frames + 1:
			self.__step_counter += 1
			self.__cur_scene.image.set_alpha(0)
			self.next_scene.redraw()
			self.next_scene.image.set_alpha(255)
			self.next_scene.image = pygame.transform.box_blur(self.next_scene.image, blur_radius)
			for animation in self.next_animation_surfaces:
				animation.blur_radius = blur_radius
		elif self.__step_counter < (num_frames * 2) + 1:
			self.__step_counter += 1
			self.next_scene.redraw()
			self.next_scene.image = pygame.transform.box_blur(self.next_scene.image, blur_radius_reverse)
			for animation in self.next_animation_surfaces:
				animation.blur_radius = blur_radius_reverse
		elif self.__step_counter == (num_frames * 2) + 1:
			for animation in self.next_animation_surfaces:
				animation.blur_radius = 0
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_fade_in(self, cur_alpha: int, next_alpha: int) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return

		num_frames = FPS * 2 if self.__transition.speed == "fast" else int(FPS * 0.5)

		self.__cur_scene.image.fill((0, 0, 0))

		self.next_scene.redraw()
		self.next_scene.image.set_alpha(next_alpha)

		cur_alpha -= num_frames
		if cur_alpha < 0: cur_alpha = 0
		next_alpha += num_frames
		if next_alpha > 255: next_alpha = 255

		self.__cur_scene.image.set_alpha(cur_alpha)
		self.next_scene.image.set_alpha(next_alpha)
		
		if next_alpha == 255:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_fade_out(self, cur_alpha: int, next_alpha: int) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return

		num_frames = FPS * 2 if self.__transition.speed == "fast" else int(FPS * 0.5)

		self.__cur_scene.redraw()
		self.__cur_scene.image.set_alpha(cur_alpha)

		if not cur_alpha == 0 and not next_alpha == 255:
			self.next_scene.image.fill((0, 0, 0))

		cur_alpha -= num_frames
		if cur_alpha < 0: cur_alpha = 0
		next_alpha += num_frames
		if next_alpha > 255: next_alpha = 255

		self.__cur_scene.image.set_alpha(cur_alpha)
		self.next_scene.image.set_alpha(next_alpha)
		
		if next_alpha == 255:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_fade_out_in(self, cur_alpha: int, next_alpha: int) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return

		num_frames = FPS * 4 if self.__transition.speed == "fast" else FPS

		if self.__step_counter == 0:
			self.__cur_scene.redraw()
			self.__cur_scene.image.set_alpha(cur_alpha)
			self.next_scene.image.fill((0, 0, 0))
			for animation in self.next_animation_surfaces:
				animation.is_disabled = True
		elif self.__step_counter == 1:
			self.__cur_scene.image.fill((0, 0, 0))
			self.next_scene.redraw()
			self.next_scene.image.set_alpha(next_alpha)
			for animation in self.__cur_animation_surfaces:
				animation.is_disabled = True
			for animation in self.next_animation_surfaces:
				animation.is_disabled = False

		cur_alpha -= num_frames
		if cur_alpha < 0: cur_alpha = 0
		next_alpha += num_frames
		if next_alpha > 255: next_alpha = 255

		self.__cur_scene.image.set_alpha(cur_alpha)
		self.next_scene.image.set_alpha(next_alpha)
		
		if next_alpha == 255:
			if self.__step_counter == 0:
				self.__step_counter += 1
				self.next_scene.image.set_alpha(0)
			elif self.__step_counter == 1:
				pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_left(self) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return
		if not self.__cur_scene.rect or not self.next_scene.rect: return

		num_frames = int(FPS / 2.5) if self.__transition.speed == "fast" else int(FPS * 1.5)

		if self.__step_counter < num_frames:
			self.__step_counter += 1

			offset = int((self.__display_info.game_window.width / num_frames) * self.__step_counter)

			self.__cur_scene.rect = self.__cur_scene.rect.move_to(
				x=self.__display_info.game_window.x + offset,
				y=self.__cur_scene.rect.y,
			)
			self.__cur_scene.image = self.__cur_scene.image.subsurface((
				0,
				0,
				self.__display_info.game_window.width - offset,
				self.__display_info.game_window.height,
			))

			self.next_scene.redraw()
			self.next_scene.rect = self.next_scene.rect.move_to(
				x=self.__display_info.game_window.x + offset - self.__display_info.game_window.width,
				y=self.next_scene.rect.y,
			)
		else:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_right(self) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return
		if not self.__cur_scene.rect or not self.next_scene.rect: return

		num_frames = int(FPS / 2.5) if self.__transition.speed == "fast" else int(FPS * 1.5)

		if self.__step_counter < num_frames:
			self.__step_counter += 1

			offset = int((self.__display_info.game_window.width / num_frames) * self.__step_counter)

			self.__cur_scene.rect = self.__cur_scene.rect.move_to(
				x=self.__display_info.game_window.x - offset,
				y=self.__cur_scene.rect.y,
			)

			self.next_scene.redraw()
			self.next_scene.rect = self.next_scene.rect.move_to(
				x=self.__display_info.game_window.x - offset + self.__display_info.game_window.width,
				y=self.next_scene.rect.y,
			)
			self.next_scene.image = self.next_scene.image.subsurface((
				0,
				0,
				offset,
				self.__display_info.game_window.height,
			))
		else:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_up(self) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return
		if not self.__cur_scene.rect or not self.next_scene.rect: return

		num_frames = int(FPS / 2.5) if self.__transition.speed == "fast" else int(FPS * 1.5)

		if self.__step_counter < num_frames:
			self.__step_counter += 1

			offset = int((self.__display_info.game_window.height / num_frames) * self.__step_counter)

			self.__cur_scene.redraw()
			self.__cur_scene.rect = self.__cur_scene.rect.move_to(
				x=self.__cur_scene.rect.x,
				y=self.__display_info.game_window.y + offset,
			)
			self.__cur_scene.image = self.__cur_scene.image.subsurface((
				0,
				0,
				self.__display_info.game_window.width,
				self.__display_info.game_window.height - offset,
			))

			self.next_scene.redraw()
			self.next_scene.image = self.next_scene.image.subsurface((
				0,
				0,
				self.__display_info.game_window.width,
				offset,
			))
		else:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))

	def __update_down(self) -> None:
		if not self.image or not self.__cur_scene.image or not self.next_scene.image: return
		if not self.__cur_scene.rect or not self.next_scene.rect: return

		num_frames = int(FPS / 2.5) if self.__transition.speed == "fast" else int(FPS * 1.1)
		frame_move = int(self.__display_info.game_window.height / num_frames)

		if self.__step_counter < num_frames:
			self.__step_counter += 1

			offset = frame_move * self.__step_counter

			self.__cur_scene.redraw()
			self.__cur_scene.image = self.__cur_scene.image.subsurface((
				0,
				offset,
				self.__display_info.game_window.width,
				self.__display_info.game_window.height - offset,
			))

			# Because the cur_scene doesn't move and only "squishes" towards the top, the sprites on it don't know to move, either.
			# So for __update_down() only, we need to move the sprites manually upwards
			sprites = pygame.sprite.Group()
			sprites.add(self.__cur_animation_surfaces)
			sprites.add(self.__cur_static_surfaces)
			for sprite in sprites:
				sprite.rect = sprite.rect.move(0, -frame_move)

			self.next_scene.redraw()
			self.next_scene.rect = self.next_scene.rect.move_to(
				x=self.next_scene.rect.x,
				y=self.__display_info.game_window.y + self.__display_info.game_window.height - offset,
			)
			self.next_scene.image = self.next_scene.image.subsurface((
				0,
				0,
				self.__display_info.game_window.width,
				offset,
			))
		else:
			pygame.event.post(pygame.event.Event(SCENE_TRANSITION_END))
