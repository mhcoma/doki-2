# TOC Plus Extension for Python-Markdown
# ===============================================
# Forked from Table of Contents Extension
# Oringinal code Copyright 2008 [Jack Miller](https://codezen.org/)
# All changes of base code Copyright 2008-2014 The Python Markdown Project
# Additional changes Copyright 2023 [Michael Back](https://github.com/mhcoma).
# License: [BSD](https://opensource.org/licenses/bsd-license.php)

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor
from markdown.util import code_escape, parseBoolValue, AMP_SUBSTITUTE, HTML_PLACEHOLDER_RE, AtomicString
from markdown.treeprocessors import UnescapeTreeprocessor
import re
import html
import typing
import unicodedata
import xml.etree.ElementTree as etree

def slugify(value: str, separator: str, unicode: bool = False) -> str:
	if not unicode:
		value = unicodedata.normalize('NFKD', value)
		value = value.encode('ascii', 'ignore').decode('ascii')
	value = re.sub(r'[^\w\s-]', '', value).strip().lower()
	return re.sub(r'[{}\s]+'.format(separator), separator, value)

def slugify_unicode(value: str, separator: str) -> str:
	return slugify(value, separator, unicode=True)

def do_nothing(value: str, separator: str) -> str:
	return value

IDCOUNT_RE = re.compile(r'^(.*)_([0-9]+)$')

def unique(id: str, ids: typing.MutableSet[str]) -> str:
	while id in ids or not id:
		m = IDCOUNT_RE.match(id)
		if m:
			id = '%s_%d' % (m.group(1), int(m.group(2))+1)
		else:
			id = '%s_%d' % (id, 1)
	ids.add(id)
	return id

def get_name(el: etree.Element) -> str:
	text = []
	for c in el.itertext():
		if isinstance(c, AtomicString):
			text.append(html.unescape(c))
		else:
			text.append(c)
	return ''.join(text).strip()

def stashedHTML2text(text: str, md: Markdown, strip_entities: bool = True) -> str:
	def _html_sub(m: re.Match[str]) -> str:
		try:
			raw = md.htmlStash.rawHtmlBlocks[int(m.group(1))]
		except (IndexError, TypeError):  # pragma: no cover
			return m.group(0)
		res = re.sub(r'(<[^>]+>)', '', raw)
		if strip_entities:
			res = re.sub(r'(&[\#a-zA-Z0-9]+;)', '', res)
		return res

	return HTML_PLACEHOLDER_RE.sub(_html_sub, text)

def unescape(text: str) -> str:
	c = UnescapeTreeprocessor()
	return c.unescape(text)

def nest_toc_tokens(toc_list):
	ordered_list = []
	if len(toc_list):
		last = toc_list.pop(0)
		last['children'] = []
		levels = [last['level']]
		ordered_list.append(last)
		parents = []

		while toc_list:
			t = toc_list.pop(0)
			current_level = t['level']
			t['children'] = []

			if current_level < levels[-1]:
				levels.pop()
				to_pop = 0
				for p in reversed(parents):
					if current_level <= p['level']:
						to_pop += 1
					else:  # pragma: no cover
						break
				if to_pop:
					levels = levels[:-to_pop]
					parents = parents[:-to_pop]

				levels.append(current_level)
			
			if current_level == levels[-1]:
				(parents[-1]['children'] if parents
				 else ordered_list).append(t)
			else:
				last['children'].append(t)
				parents.append(last)
				levels.append(current_level)
			last = t

	return ordered_list

class TocPlusTreeprocessor(Treeprocessor):
	def __init__(self, md: Markdown, config: dict[str, typing.Any]):
		super().__init__(md)

		self.marker: str = config["marker"]
		self.title: str = config["title"]
		self.base_level = int(config["baselevel"]) - 1
		self.slugify = config["slugify"]
		self.sep = config["separator"]
		self.toc_class = config["toc_class"]
		self.title_class: str = config["title_class"]
		self.use_anchors: bool | None = parseBoolValue(config["anchorlink"])
		self.anchorlink_class: str = config["anchorlink_class"]
		self.use_permalinks = parseBoolValue(config["permalink"], False)
		if self.use_permalinks is None:
			self.use_permalinks = config["permalink"]
		self.permalink_class: str = config["permalink_class"]
		self.permalink_title: str = config["permalink_title"]
		self.permalink_leading: bool | None = parseBoolValue(config["permalink_leading"], False)
		self.header_rgx = re.compile("[Hh][123456]")
		if isinstance(config["toc_depth"], str) and '-' in config["toc_depth"]:
			self.toc_top, self.toc_bottom = [int(x) for x in config["toc_depth"].split('-')]
		else:
			self.toc_top = 1
			self.toc_bottom = int(config["toc_depth"])

	def iterparent(self, node: etree.Element) -> typing.Iterator[tuple[etree.Element, etree.Element]]:
		for child in node:
			if not self.header_rgx.match(child.tag) and child.tag not in ['pre', 'code']:
				yield node, child
				yield from self.iterparent(child)

	def replace_marker(self, root: etree.Element, elem: etree.Element) -> None:
		''' Replace marker with elem. '''
		for (p, c) in self.iterparent(root):
			text = ''.join(c.itertext()).strip()
			if not text:
				continue
			if c.text and c.text.strip() == self.marker and len(c) == 0:
				for i in range(len(p)):
					if p[i] == c:
						p[i] = elem
						break

	def set_level(self, elem: etree.Element) -> None:
		level = int(elem.tag[-1]) + self.base_level
		if level > 6:
			level = 6
		elem.tag = 'h%d' % level

	def add_anchor(self, c: etree.Element, elem_id: str) -> None:
		anchor = etree.Element("a")
		anchor.text = c.text
		anchor.attrib["href"] = "#" + elem_id
		anchor.attrib["class"] = self.anchorlink_class
		c.text = ""
		for elem in c:
			anchor.append(elem)
		while len(c):
			c.remove(c[0])
		c.append(anchor)

	def add_permalink(self, c: etree.Element, elem_id: str) -> None:
		permalink = etree.Element("a")
		permalink.text = ("%spara;" %
			AMP_SUBSTITUTE if self.use_permalinks is True else self.use_permalinks
		)
		permalink.attrib["href"] = "#" + elem_id
		permalink.attrib["class"] = self.permalink_class
		if self.permalink_title:
			permalink.attrib["title"] = self.permalink_title
		c.append(permalink)

	def build_toc_div(self, toc_list: list) -> etree.Element:
		div = etree.Element("div")
		div.attrib["class"] = self.toc_class

		if self.title:
			header = etree.SubElement(div, "span")
			header.attrib["class"] = "toctitle"
			header.text = self.title

		def build_etree_ul(toc_list: list, parent: etree.Element) -> etree.Element:
			ul = etree.SubElement(parent, "ul")
			for item in toc_list:
				li = etree.SubElement(ul, "li")
				link = etree.SubElement(li, "a")
				link.text = item.get('name', '')
				link.attrib["href"] = '#' + item.get('id', '')
				if item['children']:
					build_etree_ul(item['children'], li)
			return ul

		build_etree_ul(toc_list, div)

		if 'prettify' in self.md.treeprocessors:
			self.md.treeprocessors['prettify'].run(div)

		return div

	def run(self, doc: etree.Element) -> None:
		used_ids = set()
		for el in doc.iter():
			if "id" in el.attrib:
				used_ids.add(el.attrib["id"])

		toc_tokens = []
		for el in doc.iter():
			if isinstance(el.tag, str) and self.header_rgx.match(el.tag):
				self.set_level(el)
				text = get_name(el)

				if "id" not in el.attrib:
					innertext = unescape(stashedHTML2text(text, self.md))
					el.attrib["id"] = unique(self.slugify(innertext, self.sep), used_ids)

				if int(el.tag[-1]) >= self.toc_top and int(el.tag[-1]) <= self.toc_bottom:
					toc_tokens.append({
						'level': int(el.tag[-1]),
						'id': el.attrib["id"],
						'name': stashedHTML2text(
							code_escape(el.attrib.get('data-toc-label', text)),
							self.md, strip_entities=False
						)
					})

				if 'data-toc-label' in el.attrib:
					del el.attrib['data-toc-label']

				if self.use_anchors:
					self.add_anchor(el, el.attrib["id"])
				if self.use_permalinks not in [False, None]:
					self.add_permalink(el, el.attrib["id"])

		toc_tokens = nest_toc_tokens(toc_tokens)
		div = self.build_toc_div(toc_tokens)
		if self.marker:
			self.replace_marker(doc, div)

		toc = self.md.serializer(div)
		for pp in self.md.postprocessors:
			toc = pp.run(toc)
		self.md.toc_tokens = toc_tokens
		self.md.toc = toc

class TocPlusExtension(Extension):
	TreeProcessorClass = TocPlusTreeprocessor

	def __init__(self, **kwargs):
		self.config = {
			'marker': [
				'[TOC]',
				'Text to find and replace with Table of Contents. Set to an empty string to disable. '
				'Default: `[TOC]`.'
			],
			'title': [
				'', 'Title to insert into TOC `<div>`. Default: an empty string.'
			],
			'title_class': [
				'toctitle', 'CSS class used for the title. Default: `toctitle`.'
			],
			'toc_class': [
				'toc', 'CSS class(es) used for the link. Default: `toclink`.'
			],
			'anchorlink': [
				False, 'True if header should be a self link. Default: `False`.'
			],
			'anchorlink_class': [
				'toclink', 'CSS class(es) used for the link. Defaults: `toclink`.'
			],
			'permalink': [
				0, 'True or link text if a Sphinx-style permalink should be added. Default: `False`.'
			],
			'permalink_class': [
				'headerlink', 'CSS class(es) used for the link. Default: `headerlink`.'
			],
			'permalink_title': [
				'Permanent link', 'Title attribute of the permalink. Default: `Permanent link`.'
			],
			'permalink_leading': [
				False,
				'True if permalinks should be placed at start of the header, rather than end. Default: False.'
			],
			'baselevel': ['1', 'Base level for headers. Default: `1`.'],
			'slugify': [
				slugify, 'Function to generate anchors based on header text. Default: `slugify`.'
			],
			'separator': ['-', 'Word separator. Default: `-`.'],
			'toc_depth': [
				6,
				'Define the range of section levels to include in the Table of Contents. A single integer '
				'(b) defines the bottom section level (<h1>..<hb>) only. A string consisting of two digits '
				'separated by a hyphen in between (`2-5`) defines the top (t) and the bottom (b) (<ht>..<hb>). '
				'Default: `6` (bottom).'
			],
		}
		super().__init__(**kwargs)

	def extendMarkdown(self, md):
		md.registerExtension(self)
		self.md = md
		self.reset()
		tocext = self.TreeProcessorClass(md, self.getConfigs())
		md.treeprocessors.register(tocext, 'toc', 5)

	def reset(self):
		self.md.toc = ''
		self.md.toc_tokens = []

def makeExtension(**kwargs):  # pragma: no cover
	return TocPlusExtension(**kwargs)
