import typer

from .commands import init_game, build_game, run_game, test_game



app = typer.Typer(add_completion=False)

@app.command()
def init(name: str | None = None) -> None:
	"""
	Initialize a new Pacab project. This will create the necessary directory structure and files to begin creting a game.
	If 'name' is provided, a new directory will be created for your game. Else, it will use the current directory name as the name of the game.
	"""
	init_game(name)

@app.command()
def build(filename: str, debug: bool = False) -> None:
	"""
	Test and build game defined in FILENAME and produce and executable under `_build/dist/`.
	If --debug is used, logging will be enabled, and objects will be drawn with colored borders on screen.
	"""
	build_game(filename, debug)

@app.command()
def run(filename: str, debug: bool = False) -> None:
	"""
	Test and run game defined in FILENAME.
	If --debug is used, logging will be enabled, and objects will be drawn with colored borders on screen.
	"""
	run_game(filename, debug)

@app.command()
def test(filename: str) -> None:
	"""
	Run tests against game defined in FILENAME.
	"""
	test_game(filename)

if __name__ == "__main__":
	app()
