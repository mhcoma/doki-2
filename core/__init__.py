import os

import core.setting
import core.editor_data

base_dir = os.path.split(os.path.dirname(__file__))[0]

settings = core.setting.Setting()
editor_data = core.editor_data.EditorData()