import os

import pygments.styles

for style in pygments.styles.get_all_styles():
	command = f"pygmentize -S {style} -f html -a .codehilite > static/codehilite/{style}.css"
	os.system(command)