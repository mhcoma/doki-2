'''
WikiLinks Plus Extension for Python-Markdown
======================================

Forked from WikiLinks Extension

Original code Copyright [Waylan Limberg](http://achinghead.com/).

All changes of base code Copyright The Python Markdown Project

Additional changes Copyright 2023 [Michael Back](https://github.com/mhcoma).

License: [BSD](https://opensource.org/licenses/bsd-license.php)

'''
import markdown
from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re
import os

import typing

def build_url(text, base, end):
# def build_url(label):
	""" Build a url from the label, a base, and an end. """
	# clean_label = re.sub(r'([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
	# return '{}{}{}'.format(base, clean_label, end)
	list = text.split('|')
	title = list[0]
	label = title
	if len(list) != 1:
		label = list[1]
	return (f"{base}{title}{end}", label, title)

def find_article(title):
	return True

# class WikiLinkExtension(Extension):
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

		# append to end of inline patterns
		# WIKILINK_RE = r'\[\[([\w0-9_ -]+)\]\]'
		WIKILINK_RE = r'\[\[([^[\]*?\"<>]+)\]\]'

		# wikilinkPattern = WikiLinksInlineProcessor(WIKILINK_RE, self.getConfigs())
		wikilinkPattern = WikiLinksPlusInlineProcessor(WIKILINK_RE, self.getConfigs())
		wikilinkPattern.md = md
		md.inlinePatterns.register(wikilinkPattern, 'wikilink', 75)


# class WikiLinksInlineProcessor(InlineProcessor):
class WikiLinksPlusInlineProcessor(InlineProcessor):
	def __init__(self, pattern, config):
		super().__init__(pattern)
		self.config: dict[str, typing.Any] = config

	def handleMatch(self, m, data):
		if m.group(1).strip():
			# base_url, end_url, html_class = self._getMeta()
			base_url, end_url, exist_class, not_exist_class = self._getMeta()

			text = m.group(1).strip()

			# url = self.config['build_url'](label, base_url, end_url)
			result = self.config['build_url'](text, base_url, end_url)

			url = result[0]

			a = etree.Element('a')
			a.text = result[1]
			a.set('href', url)

			# if html_class:
			# 	a.set('class', html_class)
			if exist_class:
				a.set('class', exist_class)
			if not_exist_class:
				if not self.config['find_article'](result[2]):
					a.set('class', exist_class + ' ' + not_exist_class)
		else:
			a = ''
		return a, m.start(0), m.end(0)

	def _getMeta(self):
		""" Return meta data or config data. """
		base_url = self.config['base_url']
		end_url = self.config['end_url']

		# html_class = self.config['html_class']
		exist_class = self.config['exist_class']
		not_exist_class = self.config['not_exist_class']

		if hasattr(self.md, 'Meta'):
			meta = getattr(self.md, 'Meta')
			if 'wiki_base_url' in meta:
				base_url = meta['wiki_base_url'][0]
			if 'wiki_end_url' in meta:
				end_url = meta['wiki_end_url'][0]
			# if 'wiki_html_class' in self.md.Meta:
			# 	html_class = self.md.Meta['wiki_html_class'][0]
			if 'wiki_exist_class' in meta:
				exist_class = meta['wiki_exist_class'][0]
			if 'wiki_not_exist_class' in meta:
				not_exist_class = meta['wiki_not_exist_class'][0]

		# return base_url, end_url, html_class
		return base_url, end_url, exist_class, not_exist_class

def makeExtension(**kwargs):  # pragma: no cover
	# return WikiLinkExtension(**kwargs)
	return WikiLinkPlusExtension(**kwargs)
