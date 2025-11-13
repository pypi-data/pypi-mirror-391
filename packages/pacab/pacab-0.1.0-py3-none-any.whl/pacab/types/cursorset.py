import io
import pygame


class CursorSet:
	def __init__(self, cursor_default: str | None, cursor_hover: str | None, cursor_click: str | None, cursor_size: int) -> None:
		if cursor_default == None: cursor_default = "SYSTEM_CURSOR_ARROW"
		if cursor_default.startswith("SYSTEM"):
			self.__cursor_default_is_system = True
			self.cursor_default = self.__get_system_cursor(cursor_default)
		else:
			self.__cursor_default_is_system = False
			with open(cursor_default, "rb") as file:
				self.__cursor_default_bytes = bytearray(file.read())

		if cursor_hover == None: cursor_hover = "SYSTEM_CURSOR_HAND"
		if cursor_default.startswith("SYSTEM"):
			self.__cursor_hover_is_system = True
			self.cursor_hover = self.__get_system_cursor(cursor_hover)
		else:
			self.__cursor_hover_is_system = False
			with open(cursor_hover, "rb") as file:
				self.__cursor_hover_bytes = bytearray(file.read())

		if cursor_click == None: cursor_click = "SYSTEM_CURSOR_ARROW"
		if cursor_click.startswith("SYSTEM"):
			self.__cursor_click_is_system = True
			self.cursor_click = self.__get_system_cursor(cursor_click)
		else:
			self.__cursor_click_is_system = False
			with open(cursor_click, "rb") as file:
				self.__cursor_click_bytes = bytearray(file.read())

		self.__cursor_default_name = cursor_default
		self.__cursor_hover_name = cursor_hover
		self.__cursor_click_name = cursor_click
		self.__cursor_size = cursor_size

	def init_cursors(self) -> None:
		if self.__cursor_default_is_system:
			self.cursor_default = self.__get_system_cursor(self.__cursor_default_name)
		else:
			self.cursor_default = self.__create_img_cursor(self.__cursor_default_bytes)

		if self.__cursor_hover_is_system:
			self.cursor_hover = self.__get_system_cursor(self.__cursor_hover_name)
		else:
			self.cursor_hover = self.__create_img_cursor(self.__cursor_hover_bytes)

		if self.__cursor_click_is_system:
			self.cursor_click = self.__get_system_cursor(self.__cursor_click_name)
		else:
			self.cursor_click = self.__create_img_cursor(self.__cursor_click_bytes)
	
	def __create_img_cursor(self, _bytes: bytearray) -> pygame.Cursor:
		surface = pygame.transform.scale(pygame.image.load(io.BytesIO(_bytes)).convert_alpha(), (self.__cursor_size, self.__cursor_size))
		return pygame.cursors.Cursor((0, 0), surface)
			
	def __get_system_cursor(self, cursor_name: str) -> int:
		if cursor_name == "SYSTEM_CURSOR_IBEAM": return pygame.SYSTEM_CURSOR_IBEAM
		elif cursor_name == "SYSTEM_CURSOR_WAIT": return pygame.SYSTEM_CURSOR_WAIT
		elif cursor_name == "SYSTEM_CURSOR_CROSSHAIR": return pygame.SYSTEM_CURSOR_CROSSHAIR
		elif cursor_name == "SYSTEM_CURSOR_WAITARROW": return pygame.SYSTEM_CURSOR_WAITARROW
		elif cursor_name == "SYSTEM_CURSOR_SIZENWSE": return pygame.SYSTEM_CURSOR_SIZENWSE
		elif cursor_name == "SYSTEM_CURSOR_SIZENESW": return pygame.SYSTEM_CURSOR_SIZENESW
		elif cursor_name == "SYSTEM_CURSOR_SIZEWE": return pygame.SYSTEM_CURSOR_SIZEWE
		elif cursor_name == "SYSTEM_CURSOR_SIZENS": return pygame.SYSTEM_CURSOR_SIZENS
		elif cursor_name == "SYSTEM_CURSOR_SIZEALL": return pygame.SYSTEM_CURSOR_SIZEALL
		elif cursor_name == "SYSTEM_CURSOR_NO": return pygame.SYSTEM_CURSOR_NO
		elif cursor_name == "SYSTEM_CURSOR_HAND": return pygame.SYSTEM_CURSOR_HAND
		return pygame.SYSTEM_CURSOR_ARROW
