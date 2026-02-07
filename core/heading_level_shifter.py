from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

class HeadingLevelShiftProcessor(Treeprocessor):
	def run(self, root):
		for element in root.iter():
			if element.tag in ["h1", "h2", "h3", "h4", "h5"]:
				level = int(element.tag[1])
				element.tag = f"h{min(level + 1, 6)}"

class HeadingLevelShiftExtension(Extension):
	def extendMarkdown(self, md):
		md.treeprocessors.register(HeadingLevelShiftProcessor(md), "heading_level_shifter", 5)

def makeExtension(**kwargs):  # pragma: no cover
	return HeadingLevelShiftExtension(**kwargs)