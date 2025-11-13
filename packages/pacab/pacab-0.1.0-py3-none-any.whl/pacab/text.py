import locale

class Text:
	
	strings: dict[str, str] = dict()

	@staticmethod
	def init(translations: dict[str, dict[str, str]]) -> None:
		locale_key = locale.getlocale()[0] or "en"

		for string_key, translation_dict in translations.items():
			string = ""
			
			if locale_key in translation_dict:
				string = translation_dict[locale_key]
			elif locale_key[:2] in translation_dict:
				string = translation_dict[locale_key[:2]]
			elif "en" in translation_dict:
				string = translation_dict["en"]
			else:
				string = string_key

			Text.strings[string_key] = string

def get_string(key: str, default: str | None = None) -> str:
	string = Text.strings.get(key, key)
	if string == key and default:
		return default
	else:
		return string
