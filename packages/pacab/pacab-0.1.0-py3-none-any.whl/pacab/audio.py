import io
import pygame

from pacab.constants import MUSIC_2_COMPLETE
from pacab.gamestate import GameState
from pacab.options import Options
from pacab.types.condition import Condition
from pacab.types.scene import Scene


MUSIC_STATE_STOPPED = 1
MUSIC_STATE_PLAYING = 2
MUSIC_STATE_PAUSED = 3

class Audio():
	def __init__(self, audio_files: list[tuple[str, bytearray]]) -> None:
		pygame.mixer.init()

		self.__enable_music = True
		self.__enable_sound = True

		self.__files: dict[str, bytearray] = {}
		self.__sounds: dict[str, pygame.mixer.Sound] = {}

		self.__music_current = ""
		self.__music_state = MUSIC_STATE_STOPPED
		self.__music_2_state = MUSIC_STATE_STOPPED
		self.__music_tracker: dict[str, int] = {}

		for audio_file in audio_files:
			self.__files[audio_file[0]] = audio_file[1]
			self.__sounds[audio_file[0]] = pygame.mixer.Sound(io.BytesIO(audio_file[1]))
			self.__music_tracker[audio_file[0]] = 0
	
	def is_playing(self) -> bool:
		return self.__music_state == MUSIC_STATE_PLAYING

	def is_playing_2(self) -> bool:
		return self.__music_2_state == MUSIC_STATE_PLAYING

	def set_options(
			self,
			options: Options,
			music_name: str | None,
			music_2_name: str | None,
			music_2_loops: int,
			music_2_repeat: bool,
			dead_music_2: list[str],
			game_state: GameState,
			scene: Scene,
		) -> None:
		self.set_enable_music(options.enable_music, music_name, music_2_name, music_2_loops, music_2_repeat, dead_music_2, game_state, scene)
		self.set_enable_sound(options.enable_sound)

	def set_enable_music(
			self,
			on: bool,
			music_name: str | None,
			music_2_name: str | None,
			music_2_loops: int,
			music_2_repeat: bool,
			dead_music_2: list[str],
			game_state: GameState,
			scene: Scene,
		) -> None:
		self.__enable_music = on

		if on and music_name and self.__music_state != MUSIC_STATE_PLAYING:
			self.play_music(music_name)
		elif on and not music_name:
			self.__music_state = MUSIC_STATE_STOPPED
		elif not on:
			self.__music_state = MUSIC_STATE_STOPPED
			pygame.mixer.music.stop()

		if music_2_name:
			if on and music_2_name and self.__music_2_state != MUSIC_STATE_PLAYING:
				if Condition.check_conditions(game_state, scene.music_2_conditions, scene.music_2_conditions_use_or):
					self.play_music_2(music_2_name, music_2_loops, music_2_repeat, dead_music_2)
			elif on and not music_2_name:
				self.__music_2_state = MUSIC_STATE_STOPPED
			elif not on:
				self.__music_2_state = MUSIC_STATE_STOPPED
				self.stop_music_2(music_2_name)

	def set_enable_sound(self, on: bool) -> None:
		self.__enable_sound = on

	def pause_music(self) -> None:
		self.__music_state = MUSIC_STATE_PAUSED
		self.__music_tracker[self.__music_current] = pygame.mixer.music.get_pos()
		pygame.mixer.music.pause()

	def play_music(self, name: str) -> None:
		if not self.__enable_music: return

		if self.__music_state == MUSIC_STATE_PAUSED and name == self.__music_current:
			pygame.mixer.music.unpause()
		else:
			self.stop_music()
			self.__music_current = name

			pygame.mixer.music.load(io.BytesIO(self.__files[name]), name.split(".").pop())
			pygame.mixer.music.play(loops=-1)
		self.__music_state = MUSIC_STATE_PLAYING

	def play_music_2(self, name: str, loops: int, repeat: bool, dead_music_2: list[str]) -> None:
		if not self.__enable_music: return
		if name in dead_music_2: return

		if loops > 0: loops -= 1
		self.__sounds[name].play(loops)
		self.__music_2_state = MUSIC_STATE_PLAYING

		if not repeat:
			pygame.event.post(pygame.event.Event(MUSIC_2_COMPLETE, { "music_2": name }))
	
	def play_sound(self, name: str) -> None:
		if not self.__enable_sound: return
		self.__sounds[name].play()

	def stop_music(self) -> None:
		self.__music_state = MUSIC_STATE_STOPPED
		self.__music_tracker[self.__music_current] = 0
		pygame.mixer.music.stop()

	def stop_music_2(self, name: str) -> None:
		self.__music_2_state = MUSIC_STATE_STOPPED
		self.__sounds[name].stop()
