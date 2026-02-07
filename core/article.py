import os
import pathlib
import re

import frontmatter
import lxml.html.clean
import markdown
import markdown.extensions.codehilite
import markdown.extensions.fenced_code
import markdown.extensions.toc

import core
import core.toc_plus
import core.perm
import core.wikilinks_plus
import core.heading_level_shifter

class Article:
	article_directory_name = os.path.join(core.base_dir, "articles")
	md: markdown.Markdown
	cleaner: lxml.html.clean.Cleaner

	title: str
	raw_text: str | None
	plain_text: str | None
	existence: bool

	def __init__(self, title: str):
		self.title = title
		self.md_filename = os.path.join(Article.article_directory_name, f"{self.title}.md")
		self.raw_text = None
		self.existence = os.path.isfile(self.md_filename)

	def load(self):
		if self.existence:
			self.title = pathlib.Path(self.md_filename).resolve().stem
			md_file = open(self.md_filename, "r", encoding="utf-8")
			self.raw_text = md_file.read()
			md_file.close()

	def save(self):
		md_file = open(self.md_filename, "w+", encoding="utf-8")
		md_file.write(self.raw_text)
		md_file.close()

	def get_permissions(self, user):
		perm: core.perm.Perm = {
			"is_viewable": True,
			"is_editable": True,
			"is_movable": True,
			"is_deletable": True,
			"can_change_acl": True
		}
		return perm

	@property
	def html(self):
		return Article.convert_markdown_to_html(self.raw_text)

	@property
	def plain_text(self):
		return Article.convert_markdown_to_plain_text(self.raw_text)

	@property
	def metadata(self):
		return Article.get_metadata(self.raw_text)

	@property
	def has_redirect(self):
		if self.raw_text == None: return None
		return 'redirect' in self.metadata

	@property
	def redirect_target(self) -> str:
		if self.raw_text == None: return ""
		return self.metadata['redirect']

	@staticmethod
	def convert_markdown_to_html(raw_text: str):
	# def convert_markdown_to_html(raw_text: str, codehilite: str | None = None):
		fm_content = frontmatter.loads(raw_text).content
		# if codehilite:
		# 	for extension in Article.md.registeredExtensions:
		# 		if type(extension) == markdown.extensions.codehilite.CodeHiliteExtension:
		# 			extension.setConfig('pygments_style', codehilite)
		# 			break
		result = Article.md.convert(fm_content)
		Article.md.reset()
		return result

	@staticmethod
	def convert_markdown_to_plain_text(raw_text: str):
		fm_content = frontmatter.loads(raw_text).content
		html_text = Article.convert_markdown_to_html(fm_content)
		if html_text.strip() == "": return ""
		return re.sub(
			"(&nbsp;| |\t|\r|\n)+", ' ',
			str(Article.cleaner.clean_html(html_text))[5:-6]
		)

	@staticmethod
	def get_metadata(raw_text: str) -> dict[str, object]:
		if frontmatter.checks(raw_text):
			return frontmatter.loads(raw_text).metadata
		return dict()

	@staticmethod
	def get_all_article_names():
		return [filename.replace(".md", "") for filename in os.listdir(Article.article_directory_name) if ".md" in filename]
	
	@staticmethod
	def get_article_existence(title: str) -> bool:
		article = Article(title)
		return article.existence

md = markdown.Markdown(
	output_format="html",
	extensions=[
		core.wikilinks_plus.WikiLinkPlusExtension(
			base_url = "/view/",
			end_url = "",
			find_article = Article.get_article_existence
		),
		markdown.extensions.fenced_code.FencedCodeExtension(),
		# markdown.extensions.codehilite.CodeHiliteExtension(
		# 	noclasses = False,
		# ),
		markdown.extensions.toc.TocExtension(
			title = "Table of Contents",
			slugify = core.toc_plus.do_nothing
		),
		core.heading_level_shifter.HeadingLevelShiftExtension(),
		"legacy_em", "sane_lists", "tables", "footnotes"
	]
)

cleaner = lxml.html.clean.Cleaner(
	style=True,
	allow_tags=[''],
	remove_unknown_tags=False
)

setattr(Article, "md", md)
setattr(Article, "cleaner", cleaner)
