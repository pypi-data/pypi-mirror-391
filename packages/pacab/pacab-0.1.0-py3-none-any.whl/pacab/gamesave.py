import base64
import json
import os
import sys
from datetime import datetime
from typing import Self

from pacab.gamestate import GameState


if sys.platform == "win32":
	DATA_DIR = os.getenv("LOCALAPPDATA") or os.path.join(os.getenv("USERPROFILE") or "~/", "AppData", "Local")
else:
	DATA_DIR = os.getenv("XDG_DATA_HOME") or os.path.join(os.getenv("HOME") or "~/", ".cache")

class GameSave:
	def __init__(self, game_name: str, name: str, date: datetime, game_state: GameState) -> None:
		self.game_name = game_name
		self.name = name
		self.date = date
		self.game_state = game_state

	@classmethod
	def load_saved_games(cls, game_name: str) -> list[Self]:
		dir_path = GameSave.__get_save_dir(game_name)
		os.makedirs(dir_path, exist_ok=True)
		filenames = [x for x in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, x))]

		game_saves = []
		for filename in filenames:
			game_save = GameSave.load_saved_game(os.path.join(dir_path, filename))
			if game_save: game_saves.append(game_save)

		game_saves.sort(key=(lambda x: x.date), reverse=True)

		return game_saves

	@classmethod
	def load_saved_game(cls, filename: str) -> Self | None:
		try:
			with open(filename, "r") as file: b64_text = file.read()
			bytes = base64.b64decode(b64_text)
			json_text = bytes.decode("utf-8")
			game_save = GameSave(**json.loads(json_text))
			game_save.game_state = GameState(**game_save.game_state) # type: ignore
			return cls("", game_save.name, game_save.date, game_save.game_state)
		except:
			print(f"Error reading saved game '{filename}'!")

		return None

	def save(self) -> None:
		dir_path = GameSave.__get_save_dir(self.game_name)
		os.makedirs(dir_path, exist_ok=True)
		filename = os.path.join(dir_path, self.name)
		json_text = self.__toJSON()
		bytes = json_text.encode("utf-8")
		b64_text = base64.b64encode(bytes)
		try:
			with open(filename, "wb") as file:
				file.write(b64_text)
		except:
			print(f"Error writing save file '{filename}'!")
	
	@staticmethod
	def __get_save_dir(game_name: str) -> str:
		return os.path.join(DATA_DIR, game_name, "saves")

	def __toJSON(self) -> str:
		return json.dumps(self, default=json_default)

def json_default(value) -> dict | str:
	if isinstance(value, datetime):
		return value.isoformat()
	else:
		return value.__dict__
