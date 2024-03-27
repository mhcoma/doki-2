import json
import os
import secrets

import core
import core.utils

class Setting:
	mainpage: str
	wikiname: str
	skin: str
	codehilite: str
	secret_key: str
	default_acl: dict[str, core.utils.AccessLevel]

	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		settings_path = os.path.join(core.base_dir, "settings");
		settings_filename = os.path.join(settings_path, "settings.json")
		if os.path.isfile(settings_filename):
			settings_data = core.utils.load_json_file(settings_filename)
			default_acl = settings_data['default_acl']
			for key, val in default_acl.items():
				default_acl[key] = core.utils.AccessLevel(val)
		else:
			secret_key = secrets.token_hex()
			
			default_acl = {
				"edit": str(core.utils.AccessLevel.NOOB),
				"move": str(core.utils.AccessLevel.NOOB),
				"discuss": str(core.utils.AccessLevel.NOOB),
				"delete": str(core.utils.AccessLevel.ADMIN),
				"acl": str(core.utils.AccessLevel.ADMIN)
			}

			settings_data = {
				'wikiname': "WikiName",
				'mainpage': "MainPage",
				'skin': "modern",
				'codehilite': "github-dark",
				'secret_key': secret_key,
				'default_acl': default_acl
			}
			if not os.path.isdir(settings_path):
				os.mkdir(settings_path)

			core.utils.save_json_file(settings_data, settings_filename)

		self.mainpage = settings_data['mainpage']
		self.wikiname = settings_data['wikiname']
		self.skin = settings_data['skin']
		self.codehilite = settings_data['codehilite']
		self.secret_key = settings_data['secret_key']
		self.default_acl = settings_data['default_acl']

instance = Setting()