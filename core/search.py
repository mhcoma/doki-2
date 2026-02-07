import math
import os
import re
import typing

import tantivy

import core.article

class SearchResultItem(typing.NamedTuple):
	title: str
	title_snippet: str
	body_snippet: str

class SearchResult(typing.NamedTuple):
	query_text: str
	total_hits: int
	total_pages: int
	current_page: int
	items: list[SearchResultItem]

class SearchEngine:
	schema: tantivy.Schema
	index_dirname = "index"
	max_title_snippet_len = 100
	max_body_snippet_len = 300

	def __init__(self):
		schema_builder = tantivy.SchemaBuilder()
		schema_builder.add_text_field("title", stored=True, tokenizer_name="my_ngram")
		schema_builder.add_text_field("body", stored=True, tokenizer_name="my_ngram")
		schema_builder.add_text_field("title_id", stored=True, tokenizer_name="raw")
		self.schema = schema_builder.build()

		text_analyser_builder = tantivy.TextAnalyzerBuilder(tantivy.Tokenizer.ngram()).build()

		index_exists = os.path.isdir(SearchEngine.index_dirname)
		if not index_exists:
			os.mkdir(SearchEngine.index_dirname)

		self.index = tantivy.Index(self.schema, path=SearchEngine.index_dirname)
		self.index.register_tokenizer("my_ngram", text_analyser_builder)

		self.writer = self.index.writer(heap_size=128_000_000)

		if not index_exists:
			self.update_all_documents()

	def update_all_documents(self):
		article_names = core.article.Article.get_all_article_names()
		for article_name in article_names:
			article = core.article.Article(article_name)
			article.load()
			self.update_document(article)

	def update_document(self, article: core.article.Article):
		self.writer.delete_documents("title_id", article.title)

		document = tantivy.Document(
			title=article.title,
			title_id=article.title,
			body=article.plain_text
		)

		self.writer.add_document(document)
		self.writer.commit()
		self.index.reload()

	def delete_document(self, article: core.article.Article):
		self.writer.delete_documents("title", article.title)
		self.writer.commit()
		self.index.reload()

	def search(self, query_text: str, page: int):
		searcher = self.index.searcher()
		
		safe_query_text = re.sub(r'([+\-&|!(){}\[\]^"~*?:\\/])', r'\\\1', query_text.strip())
		phrase_layer_query_text = f"title:\"{safe_query_text}\"^100 OR body:\"{safe_query_text}\"^50"
		term_layer_query_text = f"title:{safe_query_text}^10 OR body:{safe_query_text}"
		final_query_text = f"({phrase_layer_query_text}) OR ({term_layer_query_text})"
		query = self.index.parse_query(final_query_text)

		limit = 4
		offset = (page - 1) * limit
		
		total_hits = searcher.search(query).count
		total_pages = math.ceil(total_hits / limit)
		search_result = searcher.search(query, limit=limit, offset=offset)
		items = self.generate_items(searcher, query, search_result)
		
		return SearchResult(
			query_text, total_hits, total_pages, page, items
		)
	
	def generate_items(self, searcher: tantivy.Searcher, query, search_result: tantivy.SearchResult):
		title_snippet_generator = tantivy.SnippetGenerator.create(
			searcher, query, self.schema, "title"
		)
		title_snippet_generator.set_max_num_chars(SearchEngine.max_title_snippet_len)
		body_snippet_generator = tantivy.SnippetGenerator.create(
			searcher, query, self.schema, "body"
		)
		body_snippet_generator.set_max_num_chars(SearchEngine.max_body_snippet_len)

		items = []

		for score, doc_address in search_result.hits:
			doc = searcher.doc(doc_address)

			title = doc.get_first("title")
			title_snippet = title_snippet_generator.snippet_from_doc(doc)
			title_snippet_html = title_snippet.to_html()
			if title_snippet_html == "":
				title_snippet_html = title[:SearchEngine.max_title_snippet_len]

			body_snippet = body_snippet_generator.snippet_from_doc(doc)
			body_snippet_html = body_snippet.to_html()
			if body_snippet_html == "":
				body_snippet_html = doc.get_first("body")[:SearchEngine.max_title_snippet_len]
			
			items.append(
				SearchResultItem(title, title_snippet_html, body_snippet_html)
			)

		return items


engine = SearchEngine()