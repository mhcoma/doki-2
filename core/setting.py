import json
import os

import core

class Setting:
	def __init__(self):
		settings_filename = os.path.join(core.base_dir, "settings", "settings.json")
		if os.path.isfile(settings_filename):
			settings_file = open(settings_filename, 'r', encoding = "utf-8")
			settings = json.load(settings_file)
			settings_file.close()
		else:
			settings = {
				'wikiname' : "WikiName",
				'mainpage' : "MainPage",
				'skin' : "modern"
			}
			settings_file = open(settings_filename, 'w', encoding = "utf-8")
			json.dump(settings, settings_file, indent = '\t')
			settings_file.close()

		self.mainpage = settings['mainpage']
		self.wikiname = settings['wikiname']
		self.skin = settings['skin']