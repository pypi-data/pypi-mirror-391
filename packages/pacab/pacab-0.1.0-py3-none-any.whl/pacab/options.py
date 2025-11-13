import os
import sys
from typing import Self


if sys.platform == "win32":
	CACHE_DIR = os.getenv("LOCALAPPDATA") or os.path.join(os.getenv("USERPROFILE") or "~/", "AppData", "Local")
else:
	CACHE_DIR = os.getenv("XDG_CACHE_HOME") or os.path.join(os.getenv("HOME") or "~/", ".cache")

class Options:
	def __init__(self, enable_music: bool, enable_sound: bool) -> None:
		self.enable_music = enable_music
		self.enable_sound = enable_sound

	def save_options(self, game_name: str) -> None:
		file_path = Options.__get_cache_file_path(game_name)
		os.makedirs(os.path.dirname(file_path), exist_ok=True)
		with open(file_path, "w") as file:
			file.write(f"music={1 if self.enable_music else 0}\nsound={1 if self.enable_sound else 0}\n")

	@classmethod
	def load_options(cls, game_name: str) -> Self:
		file_path = Options.__get_cache_file_path(game_name)

		enable_music = True
		enable_sound = True

		if os.path.exists(file_path):
			with open(file_path, "r") as file:
				for line in file.readlines():
					line = line.strip()
					if line.startswith("music="):
						enable_music = line.endswith("1")
					elif line.startswith("sound="):
						enable_sound = line.endswith("1")

		return cls(enable_music, enable_sound)

	@staticmethod
	def __get_cache_file_path(game_name: str) -> str:
		return os.path.join(CACHE_DIR, game_name, "options.txt")
