from pacab.types.box import Box


class SceneItem(Box):
	def __init__(
		self,
		x: int,
		y: int,
		width: int,
		height: int,
		name: str,
		image: bytearray,
		pickup_message: str | None,
		pickup_sound: str | None,
		can_pick_up: bool,
	) -> None:
		super().__init__(x, y, width, height)
		self.name = name
		self.image = image
		self.pickup_message = pickup_message
		self.pickup_sound = pickup_sound
		self.can_pick_up = can_pick_up
