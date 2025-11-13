from pacab.gamestate import GameState
from pacab.types.gamestatevalue import GameStateValue


COND_KEY_VALUE = "key_value"
COND_ITEM = "item"
COND_INVENTORY_ITEM = "inventory_item"

class Condition:
	def __init__(self, type: str, key: str | None, value: GameStateValue | None, negate: bool) -> None:
		self.type = type
		self.key = key
		self.value = value
		self.__eq_func = not_equals if negate else equals
	
	types = [
		COND_KEY_VALUE,
		COND_ITEM,
		COND_INVENTORY_ITEM,
	]

	@staticmethod
	def check_conditions(game_state: GameState, conditions: list, use_or: bool) -> bool:
		# No Conditions
		if not len(conditions):
			return True

		# OR the Conditions together
		elif use_or:
			is_satisfied = False
			for condition in conditions:
				if condition.is_satisfied(game_state):
					is_satisfied = True
			return is_satisfied

		# AND the Condtions together
		else:
			is_satisfied = True
			for condition in conditions:
				if not condition.is_satisfied(game_state):
					is_satisfied = False
			return is_satisfied

	def is_satisfied(self, game_state: GameState) -> bool:
		if self.type == COND_KEY_VALUE:
			return self.__eq_func(game_state.game_globals[self.key], self.value)
		elif self.type == COND_ITEM:
			return self.__eq_func(game_state.selected_item, self.value)
		elif self.type == COND_INVENTORY_ITEM:
			return self.__eq_func(self.value in game_state.items, True)
		else:
			return False

def equals(value1, value2) -> bool:
	return value1 == value2

def not_equals(value1, value2) -> bool:
	return value1 != value2
