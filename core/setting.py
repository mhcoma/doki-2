import json
import os
import secrets

import core

class Setting:
	mainpage: str
	wikiname: str
	skin: str
	codehilite: str
	secret_key: str

	def __init__(self):
		settings_path = os.path.join(core.base_dir, "settings");
		settings_filename = os.path.join(settings_path, "settings.json")
		if os.path.isfile(settings_filename):
			settings_file = open(settings_filename, 'r', encoding = "utf-8")
			settings = json.load(settings_file)
			settings_file.close()
		else:
			secret_key = secrets.token_hex()

			settings = {
				'wikiname' : "WikiName",
				'mainpage' : "MainPage",
				'skin' : "modern",
				'codehilite' : "github-dark",
				'secret_key' : secret_key
			}
			if not os.path.isdir(settings_path):
				os.mkdir(settings_path)
			settings_file = open(settings_filename, 'w', encoding = "utf-8")
			json.dump(settings, settings_file, indent = '\t')
			settings_file.close()

		self.mainpage = settings['mainpage']
		self.wikiname = settings['wikiname']
		self.skin = settings['skin']
		self.codehilite = settings['codehilite']
		self.secret_key = settings['secret_key']