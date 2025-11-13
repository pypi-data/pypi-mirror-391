from pacab.displayinfo import DisplayInfo
from pacab.gamestate import GameState
from pacab.types.animationframes import AnimationFrames
from pacab.types.box import Box
from pacab.types.condition import Condition


class Animation(Box):
	def __init__(
			self,
			x: int,
			y: int,
			width: int,
			height: int,
			id: str,
			filename: str,
			loops: int,
			repeat: bool,
			duration: int,
			alpha: int,
			hold_final_frame: bool,
			conditions: list[Condition],
			conditions_use_or: bool,
		) -> None:
		super().__init__(x, y, width, height)
		self.id = id
		self.filename = filename
		self.loops = loops
		self.repeat = repeat
		self.conditions = conditions
		self.conditions_use_or = conditions_use_or
		self.duration = duration / 1000
		self.alpha = alpha
		self.hold_final_frame = hold_final_frame
		self.is_scaled = False
		self.frames: AnimationFrames | None = None

		self.__init_box = (x, y, width, height)

	def set_frames(self, animation_frames: AnimationFrames) -> None:
		self.frames = animation_frames
		self.duration /= len(self.frames)

	def reset(self) -> None:
		self.x = self.__init_box[0]
		self.y = self.__init_box[1]
		self.width = self.__init_box[2]
		self.height = self.__init_box[3]
		self.is_scaled = False
	
	def should_show(self, game_state: GameState) -> bool:
		if not self.repeat and self.id in game_state.dead_animations:
			return False
		if not Condition.check_conditions(game_state, self.conditions, self.conditions_use_or):
			return False
		return True

	def _scale(self, display_info: DisplayInfo) -> None:
		if self.is_scaled: return
		super()._scale(display_info)
		self.is_scaled = True
