import base64
import os
import pickle
import platform
import shutil
import subprocess
import sys
from glob import glob

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

from pacab.cli import gamebuilder
from pacab import Pacab


pygame.font.init()

PICKLE_FILENAME = "game.pickle"
SCRIPT_FILENAME = "main.py"
SCRIPT_TEMPLATE = """
import pickle
import os
import sys

import pacab as pacab_


def main() -> None:
    with open(os.path.join(sys._MEIPASS, "game.pickle", "game.pickle"), "rb") as file: # type: ignore
        pacab_game: pacab_.PacabGame = pickle.load(file)
    pacab = pacab_.Pacab(pacab_game).run()

if __name__ == "__main__":
    main()
"""

def init_game(name: str | None) -> None:
	dir = os.getcwd()
	if name:
		dir = os.path.join(dir, name)
		if os.path.exists(dir):
			print(f"Directory '{dir}' already exists!")
			return
		os.makedirs(dir)
		os.chdir(dir)
	else:
		name = os.path.basename(dir)

	os.makedirs(os.path.join(dir, "animations"))
	os.makedirs(os.path.join(dir, "assets"))
	os.makedirs(os.path.join(dir, "audio"))
	os.makedirs(os.path.join(dir, "dialogs"))
	os.makedirs(os.path.join(dir, "img"))
	os.makedirs(os.path.join(dir, "items"))
	os.makedirs(os.path.join(dir, "overlays"))
	os.makedirs(os.path.join(dir, "scenes"))
	os.makedirs(os.path.join(dir, "translations"))
	
	with open(os.path.join(dir, f"{name}.toml"), "w") as file:
		file.write(get_game_toml(name))

	with open(os.path.join(dir, ".gitignore"), "w") as file:
		file.writelines(["_build/"])
	
	icon_b64 = get_default_icon_b64()
	icon_bytes = base64.b64decode(icon_b64)
	with open(os.path.join(dir, "assets", f"icon.png"), "wb") as file:
		file.write(icon_bytes)
	with open(os.path.join(dir, "assets", f"{name}.desktop"), "w") as file:
		file.write(get_game_desktop_file(name))

def build_game(filename: str, debug: bool = False) -> None:
	cwd = os.getcwd()
	game_toml_path = os.path.join(cwd, filename)
	if not os.path.exists(game_toml_path):
		sys.exit((f"Filename '{filename}' not found in '{cwd}'"))
	
	game_dir = os.path.dirname(game_toml_path)
	build_dir = os.path.join(game_dir, "_build")

	is_pacab_example_game = os.path.exists(os.path.join(cwd, "pacab")) and os.path.exists(os.path.join(cwd, "example"))

	desktop_files = glob(os.path.join(game_dir, "assets", "*.desktop"))
	desktop_file = desktop_files[0] if len(desktop_files) > 0 else None
	icon_files = glob(os.path.join(game_dir, "assets", "icon.*"))
	icon_file = icon_files[0] if len(icon_files) > 0 else None

	try:
		pacab_game = gamebuilder.GameBuilder.build(game_toml_path, debug)
		pass
	except Exception as error:
		print(error)
		exit()
	
	print(f"\nPackaging {pacab_game.name} for {platform.system()} {platform.machine()}!\n")

	os.makedirs(build_dir, exist_ok=True)
	with open(os.path.join(build_dir, SCRIPT_FILENAME), "w") as file:
		file.write(SCRIPT_TEMPLATE)
	with open(os.path.join(build_dir, PICKLE_FILENAME), "wb") as file:
		pickle.dump(pacab_game, file)

	args = [
		"pipenv",
		"run",
		"pyinstaller",
		"--name", pacab_game.short_name,
		# If building the example game, we need to include the pacab dir manually. Else it will be installed by pipenv.
		f"{"" if not is_pacab_example_game else f"--add-data={os.path.join(cwd, "pacab")}:pacab"}",
		f"--add-binary={os.path.join(build_dir, "game.pickle")}:game.pickle",
		"--exclude-module", "PIL",
		"--icon", f"{icon_file if icon_file else "NONE"}",
		"--hidden-import=pygame",
		"--hidden-import=pygame_menu",
		"--noconsole",
		"--onefile",
		os.path.join(build_dir, SCRIPT_FILENAME),
	]
	args[:] = [x for x in args if x != ""]

	subprocess.run(args, -1, None, None, None, None, None, True, False, build_dir)

	dist_dir = os.path.join(build_dir, "dist")
	if sys.platform == "linux":
		if desktop_file:
			shutil.copyfile(desktop_file, os.path.join(dist_dir, f"{pacab_game.short_name}.desktop"))
		if icon_file:
			dest_file = shutil.copyfile(icon_file, os.path.basename(icon_file))
			ext = dest_file.split(".").pop()
			os.rename(dest_file, os.path.join(dist_dir, f"{pacab_game.short_name}.{ext}"))
	
	print()
	print("------------------------------")
	print("".join(e for e in filename[filename.rfind("/"):].replace(".toml", "") if e.isalnum() or e == "-"))
	print(f"Built '{pacab_game.name}' successfully! Executable can be found at '{os.path.join(build_dir, "dist").replace("./", "")}'")
	print()

def run_game(filename: str, debug: bool = False) -> None:
	cwd = os.getcwd()
	game_toml_path = os.path.join(cwd, filename)
	if not os.path.exists(game_toml_path):
		sys.exit((f"Filename '{filename}' not found in '{cwd}'"))

	try:
		pacab_game = gamebuilder.GameBuilder.build(game_toml_path, debug)
	except Exception as error:
		print(error)
		exit()

	Pacab(pacab_game).run()

def test_game(filename: str) -> None:
	cwd = os.getcwd()
	game_toml_path = os.path.join(cwd, filename)
	if not os.path.exists(game_toml_path):
		sys.exit((f"Filename '{filename}' not found in '{cwd}'"))

	try:
		gamebuilder.GameBuilder.build(game_toml_path, False)
	except Exception as error:
		print(error)
		exit()

def get_game_toml(name: str) -> str:
	return f"""name = \"{name}\"
init_scene = "my_first_scene"

start_game_message = "Welcome to {name}!"
"""

def get_game_desktop_file(name: str) -> str:
	return f"""[Desktop Entry]
Type=Application
Version=1.0
Name={name}
Exec={name}
Comment=Play {name}
Icon={name}
Terminal=false
Categories=Game
X-Purism-FormFactor=Workstation;Mobile;
"""

def get_default_icon_b64() -> str:
	return "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"
