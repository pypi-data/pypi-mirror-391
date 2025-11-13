
class Logger:
	print_logs = False

	@staticmethod
	def log(message: str) -> None:
		if Logger.print_logs:
			print(str(message))
