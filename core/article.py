import datetime
import enum
import json
import os
import shutil

import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
import markdown.extensions.toc

import core
import core.wikilinks_plus
import core.toc_plus
import core.user
import core.utils

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

		self.acl_filename = os.path.join(self.directory_name, "acl.json")
		self.acl_data = core.settings.default_acl.copy()

	def load(self):
		if os.path.isfile(self.article_filename):
			self.article_data = core.utils.load_json_file(self.article_filename)
			self.history_data = core.utils.load_json_file(self.history_filename)
			self.acl_data = core.utils.load_json_file(self.acl_filename)

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

			core.utils.save_json_file(self.article_data, self.article_filename)

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
				markdown.extensions.toc.TocExtension(
					title = "Table of Contents",
					slugify = core.toc_plus.do_nothing
				),
				"legacy_em", "sane_lists", "tables"
			]
		)
	
	def save(self, username: str):
		now = datetime.datetime.now(datetime.UTC).isoformat()
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
				'editor' : username,
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

		core.utils.save_json_file(self.article_data, self.article_filename)
		core.utils.save_json_file(self.history_data, self.history_filename)
		core.utils.save_json_file(self.acl_data, self.acl_filename)

	def delete(self):
		if os.path.isdir(self.directory_name):
			shutil.rmtree(self.directory_name)
	
	def is_accessable(self, key: str, user: core.user.User | None) -> bool:
		if user == None:
			return self.acl_data[key] <= core.utils.AccessLevel.ANONYMOUS
		else:
			if self.acl_data[key] <= core.utils.AccessLevel.NOOB:
				return True
			elif self.acl_data[key] <= core.utils.AccessLevel.USER:
				return user.is_not_noob()
			else:
				return user.is_admin

def find_article(title):
	article = Article(title)
	article.load()
	return article.existence