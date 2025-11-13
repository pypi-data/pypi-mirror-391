from pacab.types.inspectaction import InspectAction
from pacab.types.itemcombination import ItemCombination


class InventoryItem:
	def __init__(
			self,
			name: str,
			title: str,
			images: list[tuple[str, bytearray]],
			pickup_message: str | None,
			inventory_message: str | None,
			pickup_sound: str | None,
			combos: list[ItemCombination] | None,
			inspect_actions: list[InspectAction] | None,
			show_inspect: bool,
			deconstruct_to: list[str],
			deconstruct_label: str,
		) -> None:
		self.name = name
		self.title = title
		self.images = images
		self.pickup_message = pickup_message
		self.inventory_message = inventory_message
		self.pickup_sound = pickup_sound
		self.combos = combos
		self.inspect_actions = inspect_actions
		self.show_inspect = True \
			if (inspect_actions and len(inspect_actions)) \
			or (len(deconstruct_to)) \
			or show_inspect else False
		self.deconstruct_to = deconstruct_to
		self.deconstruct_label = deconstruct_label
