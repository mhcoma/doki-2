import datetime
import enum
import heapq
import io
import json
import os
import re
import shutil
import typing

import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
import markdown.extensions.toc

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

class SearchResult:
	priority: int
	title: str
	title_results: list[tuple[bool, str]]
	content_results: list[tuple[bool, str]]

	def __init__(self, priority, title, title_results, content_results):
		self.priority = priority
		self.title = title
		self.title_results = title_results
		self.content_results = content_results
	
	def __lt__(self, other):
		if self.__class__ is other.__class__:
			return self.priority < other.priority
	
	def __le__(self, other):
		if self.__class__ is other.__class__:
			return self.priority <= other.priority
	
	def __gt__(self, other):
		if self.__class__ is other.__class__:
			return self.priority > other.priority
	
	def __ge__(self, other):
		if self.__class__ is other.__class__:
			return self.priority >= other.priority

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
			
	def search_texts(self, text) -> SearchResult | None:
		pattern = re.compile(re.escape(text), re.I)
		
		is_found = False
		
		priority = 0
		title_results: list[tuple[bool, str]] = []
		title_search_pos = 0
		title_matches = pattern.finditer(self.title)
		title_len = len(self.title)
		for r in title_matches:
			r_span = r.span()
			r_group = r.group()
			if r_span[0] - title_search_pos > 0:
				title_results.append((False, self.title[title_search_pos:r_span[0]]))
			title_results.append((True, r_group))
			title_search_pos = r_span[1]
			priority += 2
			is_found = True
		if len(self.title) - title_search_pos > 0:
			title_results.append((False, self.title[title_search_pos:]))
		
		content_results: list[tuple[bool, str, tuple[int, int]]] = []
		new_content_results: list[tuple[bool, str]] = []
		content_search_pos = 0
		content_matches = pattern.finditer(self.plain_text_data)
		content_len = len(self.plain_text_data)
		for r in content_matches:
			r_span = r.span()
			r_group = r.group()
			if r_span[0] - content_search_pos > 0:
				pos = (content_search_pos, r_span[0])
				content_results.append((False, self.plain_text_data[content_search_pos:r_span[0]], pos))
			pos = (r_span[0], r_span[1])
			content_results.append((True, r_group, pos))
			content_search_pos = r_span[1]
			priority += 1
			is_found = True
		
		if is_found:
			if len(self.plain_text_data) - content_search_pos > 0:
				pos = (content_search_pos, content_len)
				content_results.append((False, self.plain_text_data[content_search_pos:], pos))
			
			if len(content_results) > 1:
				results_token_len_sum = 0
				is_break_next = False
				stls_at_break = 0
				for index, content_result in enumerate(content_results):
					is_true, token, pos = content_result
					token_len = pos[1] - pos[0]
					if index == 0 and not is_true:
						if token_len >= 25:
							token = token[token_len - 25:token_len]
							token_len = 25
					results_token_len_sum += token_len
					new_content_results.append((is_true, token))
					print(results_token_len_sum)
					if not is_break_next and results_token_len_sum > 256:
						is_break_next = True
						stls_at_break = results_token_len_sum
						continue
					if is_break_next:
						break
				print(new_content_results, stls_at_break)
				if new_content_results[-1][0] and stls_at_break > 256:
					new_content_results.pop()
			else:
				content_result = content_results[0]
				is_true, token, pos = content_result
				new_content_results.append((is_true, token))
				stls_at_break = len(token)
			
			is_last_true, last_token = new_content_results[-1]
			last_token_len = len(last_token)
			if stls_at_break > 256:
				last_token = last_token[:last_token_len + (256 - stls_at_break)] + " ..."
			new_content_results[-1] = (is_last_true, last_token)
		
		if is_found:
			return SearchResult(-priority, self.title, title_results, new_content_results)
		return None
	
	@staticmethod
	def search_files(text: str) -> list[SearchResult]:
		out_heap: list[SearchResult] = []
		out_list: list[SearchResult] = []
		for (root, dirs, files) in os.walk(Article.article_directory_name):
			for article_name in dirs:
				article = Article(article_name)
				article.load(load_type = ArticleLoadType.SEARCH)
				result = article.search_texts(text)
				if result:
					heapq.heappush(out_heap, result)
		is_found = False
		while out_heap:
			result = heapq.heappop(out_heap)
			out_list.append(result)
			is_found = True
		return out_list
	
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