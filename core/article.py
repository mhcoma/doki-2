import datetime
import enum
import heapq
import io
import json
import os
import re
import shutil

import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
import markdown.extensions.toc

import lxml
import lxml.html.clean

import core
import core.wikilinks_plus
import core.toc_plus
import core.user
import core.utils
import core.settings

class ArticleLoadType(enum.Enum):
	NONE = 0
	VIEW = 1
	EDIT = 2
	SEARCH = 3

class Article:
	article_directory_name = os.path.join(core.base_dir, "articles")
	md: markdown.Markdown
	cleaner: lxml.html.clean.Cleaner

	def __init__(self, title: str):
		self.raw_data: str = ""
		self.existence: bool = False
		self.title: str = title

		self.directory_name = os.path.join(Article.article_directory_name, self.title)

		self.article_filename = os.path.join(self.directory_name, "article.json")
		self.article_data = {}

		self.history_filename = os.path.join(self.directory_name, "history.json")
		self.history_data = []

		self.acl_filename = os.path.join(self.directory_name, "acl.json")
		self.acl_data = core.settings.instance.default_acl.copy()

		self.plain_text_data_filename = os.path.join(self.directory_name, "plain.txt")
		self.plain_text_data = ""

	def load(self, load_type: ArticleLoadType = ArticleLoadType.VIEW):
		if os.path.isfile(self.article_filename):
			if load_type == ArticleLoadType.VIEW:
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
			elif load_type == ArticleLoadType.SEARCH:
				plain_text_data_file = open(self.plain_text_data_filename, 'r', encoding = "utf-8")
				self.plain_text_data = plain_text_data_file.read()
				plain_text_data_file.close()

	def render_markdown(self):
		self.data = Article.convert_markdown(self.raw_data)
	
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

		plain_text_data_file = open(self.plain_text_data_filename, 'w', encoding = "utf-8")
		plain_text_data_file.write(Article.convert_markdown(self.raw_data, False))
		plain_text_data_file.close()

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
			
	def search_texts(self, text):
		pattern = re.compile(re.escape(text), re.I)
		
		is_found = False
		
		priority = 0
		title_results = []
		title_search_pos = 0
		title_matches = pattern.finditer(self.title)
		for r in title_matches:
			is_found = True
			r_span = r.span()
			r_group = r.group()
			title_results.append((False, self.title[title_search_pos:r_span[0]]))
			title_results.append((True, r_group))
			title_search_pos = r_span[1]
			priority += 1024
		title_results.append((False, self.title[title_search_pos:]))
		
		data_results = []
		data_search_pos = 0
		
		data_matches = pattern.finditer(self.plain_text_data)
		for r in data_matches:
			is_found = True
			r_span = r.span()
			r_group = r.group()
			data_results.append((False, self.plain_text_data[data_search_pos:r_span[0]]))
			data_results.append((True, r_group))
			data_search_pos = r_span[1]
			priority += 1
		if is_found:
			data_results.append((False, self.plain_text_data[data_search_pos:]))
		
		if is_found:
			return (-priority, title_results, data_results)
		return None
	
	@staticmethod
	def search_files(text: str):
		out_heap = []
		out_list = []
		for (root, dirs, files) in os.walk(Article.article_directory_name):
			for article_name in dirs:
				article = Article(article_name)
				article.load(load_type = ArticleLoadType.SEARCH)
				result = article.search_texts(text)
				if result:
					heapq.heappush(out_heap, result)
		is_found = False
		while out_heap:
			out_list.append(heapq.heappop(out_heap)[1:])
			is_found = True
		if not is_found:
			out_list = '검색 결과가 없습니다.'
		return str(out_list)
	
	@staticmethod
	def convert_markdown(raw_data: str, convert_to_html: bool = True) -> str:
		result = Article.md.convert(raw_data)
		if not convert_to_html: result = Article.convert_html_to_plain_text(result)
		return result
	
	@staticmethod
	def find_article(title):
		article = Article(title)
		article.load()
		return article.existence

	@staticmethod
	def convert_html_to_plain_text(html: str) -> str:
		return re.sub('(&nbsp;| |\t|\r|\n)+', ' ', str(Article.cleaner.clean_html(html))[5:-6])

md = markdown.Markdown(
	output_format = "html",
	extensions = [
		core.wikilinks_plus.WikiLinkPlusExtension(
			base_url = "/view/",
			end_url = "",
			find_article = Article.find_article
		),
		markdown.extensions.fenced_code.FencedCodeExtension(),
		markdown.extensions.codehilite.CodeHiliteExtension(
			noclasses = True,
			pygments_style = core.settings.instance.codehilite
		),
		markdown.extensions.toc.TocExtension(
			title = "Table of Contents",
			slugify = core.toc_plus.do_nothing
		),
		"legacy_em", "sane_lists", "tables"
	]
)

cleaner = lxml.html.clean.Cleaner(
	style = True,
	allow_tags = [''],
	remove_unknown_tags = False
)

setattr(Article, "md", md)
setattr(Article, "cleaner", cleaner)