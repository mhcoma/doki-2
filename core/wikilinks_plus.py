# WikiLinks Plus Extension for Python-Markdown
# ======================================
# Forked from WikiLinks Extension
# Original code Copyright [Waylan Limberg](http://achinghead.com/).
# All changes of base code Copyright The Python Markdown Project
# Additional changes Copyright 2023 [Michael Back](https://github.com/mhcoma).
# License: [BSD](https://opensource.org/licenses/bsd-license.php)

from __future__ import annotations

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re

import typing

def build_url(self, text: str, base: str, end: str) -> tuple[str, str, str]:
	splitted_text = text.split('|')
	title =  self.unescape(splitted_text[0]).strip()
	label = title
	if len(splitted_text) != 1:
		label = splitted_text[1]
	return (f"{base}{title}{end}", label, title)

def find_article(title):
	return True

class WikiLinkPlusExtension(Extension):
	def __init__(self, **kwargs):
		self.config = {
			'base_url': ['/', 'String to append to beginning or URL.'],
			'end_url': ['/', 'String to append to end of URL.'],
			'exist_class': ['wikilink', 'CSS hook. Leave blank for none.'],
			'not_exist_class' : ['ne_wikilink', 'CSS hook. Leave blank for none.'],
			'build_url': [build_url, 'Callable formats URL from label.'],
			'find_article': [find_article, 'Callable'] 
		}

		super().__init__(**kwargs)

	def extendMarkdown(self, md):
		self.md = md
		WIKILINK_RE = r'\[\[([^[\]*?\"<>]+)\]\]'
		wikilinkPattern = WikiLinksPlusInlineProcessor(WIKILINK_RE, self.getConfigs())
		wikilinkPattern.md = md
		md.inlinePatterns.register(wikilinkPattern, 'wikilink', 75)

class WikiLinksPlusInlineProcessor(InlineProcessor):
	def __init__(self, pattern: str, config: dict[str, typing.Any]):
		super().__init__(pattern)
		self.config = config

	def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element | str, int, int]:
		if m.group(1).strip():
			base_url, end_url, exist_class, not_exist_class = self._getMeta()
			# text = self.unescape(m.group(1)).strip()
			text = m.group(1)
			result = self.config['build_url'](self, text, base_url, end_url)
			url = result[0]
			a = etree.Element('a')
			a.text = result[1]
			a.set('href', url)
			if exist_class:
				a.set('class', exist_class)
			if not_exist_class:
				if not self.config['find_article'](result[2]):
					a.set('class', exist_class + ' ' + not_exist_class)
		else:
			a = ''
		return a, m.start(0), m.end(0)

	def _getMeta(self) -> tuple[str, str, str, str]:
		base_url = self.config['base_url']
		end_url = self.config['end_url']
		exist_class = self.config['exist_class']
		not_exist_class = self.config['not_exist_class']

		if hasattr(self.md, 'Meta'):
			meta = getattr(self.md, 'Meta')
			if 'wiki_base_url' in meta:
				base_url = meta['wiki_base_url'][0]
			if 'wiki_end_url' in meta:
				end_url = meta['wiki_end_url'][0]
			if 'wiki_exist_class' in meta:
				exist_class = meta['wiki_exist_class'][0]
			if 'wiki_not_exist_class' in meta:
				not_exist_class = meta['wiki_not_exist_class'][0]

		return base_url, end_url, exist_class, not_exist_class

def makeExtension(**kwargs):  # pragma: no cover
	return WikiLinkPlusExtension(**kwargs)
