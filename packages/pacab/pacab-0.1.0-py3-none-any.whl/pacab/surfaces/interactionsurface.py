import pygame
from pygame.locals import (
	RLEACCEL,
)

from pacab.actionrunner import ActionRunner
from pacab.constants import *
from pacab.displayinfo import DisplayInfo
from pacab.gamestate import GameState
from pacab.types.action import *
from pacab.types.condition import Condition
from pacab.types.interaction import Interaction
from pacab.types.pacabgame import PacabGame


class InteractionSurface(pygame.sprite.Sprite):
	def __init__(self, interaction: Interaction, display_info: DisplayInfo, pacab_game: PacabGame):
		super(InteractionSurface, self).__init__()

		self.interaction = interaction

		interaction._scale(display_info)
		rect = pygame.Rect(interaction.x, interaction.y, interaction.width, interaction.height)
		self.image = pygame.Surface((interaction.width, interaction.height))
		self.image.fill((255, 255, 255))
		self.image.set_colorkey((255, 255, 255), RLEACCEL)
		self.rect = self.image.get_rect()

		# Draw borders for debugging
		if pacab_game.debug_mode:
			pygame.draw.rect(self.image, (0, 255, 0), self.rect, 2)

		self.rect.topleft = rect.topleft
	
	def is_interactable(self, game_state: GameState) -> bool:
		return Condition.check_conditions(game_state, self.interaction.conditions, self.interaction.conditions_use_or)

	def interact(self, game_state: GameState) -> None:
		ActionRunner.execute_actions(game_state, self.interaction.actions)
		if self.interaction.message:
			pygame.event.post(pygame.event.Event(DIALOG_FROM_STR, { "text": self.interaction.message }))
		if len(self.interaction.actions):
			pygame.event.post(pygame.event.Event(REFRESH_SCENE))
