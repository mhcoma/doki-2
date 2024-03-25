import datetime
import json
import os
import shutil

import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite

import core
import core.wikilinks_plus
import core.toc_plus
import core.pygments_markdown

class Article:
	def __init__(self, title: str):
		self.raw_data: str = ""
		self.existence: bool = False
		self.title: str = title

		self.directory_name = os.path.join(core.base_dir, "articles", self.title)

		self.article_filename = os.path.join(self.directory_name, "article.json")
		self.article_data = {}

		self.history_filename = os.path.join(self.directory_name, "history.json")
		self.history_data = []

	def load(self):
		if os.path.isfile(self.article_filename):
			article_file = open(self.article_filename, 'r', encoding = "utf-8")
			self.article_data = json.load(article_file)
			article_file.close()

			history_file = open(self.history_filename, 'r', encoding = "utf-8")
			self.history_data = json.load(history_file)
			history_file.close()

			edition = self.article_data['edition']
			for i in range(edition, -1, -1):
				edition = i
				md_filename = os.path.join(self.directory_name, f"{i}.md")
				self.existence = True
				if os.path.isfile(md_filename):
					md_file = open(md_filename, 'r', encoding = "utf-8")
					self.raw_data = md_file.read()
					md_file.close()
				break
			self.article_data['edition'] = edition
			article_file = open(self.article_filename, 'w', encoding = "utf-8")
			json.dump(self.article_data, article_file, indent = '\t')
			article_file.close()

	def convert_markdown(self):
		self.data = markdown.markdown(
			self.raw_data,
			output_format = "html",
			extensions = [
				core.wikilinks_plus.WikiLinkPlusExtension(
					base_url = "/view/",
					end_url = "",
					find_article = find_article
				),
				markdown.extensions.fenced_code.FencedCodeExtension(),
				markdown.extensions.codehilite.CodeHiliteExtension(
					noclasses = True,
					pygments_style = core.settings.codehilite
				),
				core.toc_plus.TocPlusExtension(
					title = "Table of Contents",
					slugify = core.toc_plus.do_nothing
				),
				"legacy_em", "sane_lists", "tables"
			]
		)
	
	def save(self, user: str):
		now = datetime.datetime.utcnow().isoformat()
		if not self.existence:
			self.article_data = {
				'edition' : 0,
				'created' : now,
				'last_updated' : now
			}
			self.existence = True
			if not os.path.isdir(self.directory_name):
				os.makedirs(self.directory_name)
		self.article_data['edition'] += 1

		self.history_data.append(
			{
				'edition' : self.article_data['edition'],
				'editor' : user,
				'date' : now
			}
		)

		md_filename = os.path.join(
			self.directory_name,
			f"{self.article_data['edition']}.md"
		)
		md_file = open(md_filename, 'w', encoding = "utf-8")
		md_file.write(self.raw_data)
		md_file.close()

		article_file = open(self.article_filename, 'w', encoding = "utf-8")
		json.dump(self.article_data, article_file, indent = '\t')

		history_file = open(self.history_filename, 'w', encoding = 'utf-8')
		json.dump(self.history_data, history_file, indent = '\t')

	def delete(self):
		if os.path.isdir(self.directory_name):
			shutil.rmtree(self.directory_name)

def find_article(title):
	article = Article(title)
	article.load()
	return article.existence