import json
import urllib.parse

import flask

import core.article
import core.search

def view_response(title: str, redirected_from: str | None = None, no_redirect: int | None = None):
	is_htmx = flask.request.headers.get("HX-Request")
	user = None
	article = core.article.Article(title)
	article.load()
	if article.has_redirect and not no_redirect:
		return view_response(article.redirect_target, redirected_from=article.title, no_redirect=1)
	
	perm = article.get_permissions(user)
	context = {
		'title': f"{article.title}",
		'article': article,
		'redirected_from': redirected_from,
		'perm': perm,
		# 'codehilite': "github-dark"
	}
	rendered_html = flask.render_template(
		"view.jinja",
		**context
	)
	response = flask.make_response(rendered_html)

	if is_htmx:
		response_values = {
			'title': f"{article.title}",
			'from': redirected_from,
			'noredirect': no_redirect
		}
		response.headers['HX-Title'] = urllib.parse.quote(context['title'])
		response.headers['HX-Push-Url'] = flask.url_for("view", **response_values)
	return response

def edit_response(title: str):
	is_htmx = flask.request.headers.get("HX-Request")
	article = core.article.Article(title)
	user = None

	article.load()
	perm = article.get_permissions(user)
	context = {
		'title': f"Edit: {article.title}",
		'article': article,
		'perm': perm
	}
	rendered_html = flask.render_template(
		"edit.jinja",
		**context
	)
	response = flask.make_response(rendered_html)
	if is_htmx:
		response_values = {
			'title': f"{article.title}"
		}
		response.headers['HX-Title'] = urllib.parse.quote(context['title'])
		response.headers['HX-Push-Url'] = flask.url_for("edit", **response_values)
	return response

def edit_save_response(title: str, raw_text: str):
	article = core.article.Article(title)
	user = None
	perm = article.get_permissions(user)
	article.load()
	article.raw_text = raw_text
	article.save()
	core.search.engine.update_document(article)

	response = flask.make_response("", 204)
	response.headers["HX-Location"] = json.dumps(
		{
			'path': flask.url_for('view', title=article.title, noredirect=1),
			'target': "#doki2-main",
			'select': "#doki2-main",
			'swap': "outerHTML transition:true"
		}
	)
	return response
def search_response(query_text: str):
	is_htmx = flask.request.headers.get("HX-Request")
	query = flask.request.args.get("query")
	
	page = flask.request.args.get("page", 1, type=int)
	search_result = core.search.engine.search(query_text, page)
	context = {
		'title': f"Search: {query_text}",
		'search_result': search_result
	}
	rendered_html = flask.render_template(
		"search.jinja",
		**context
	)
	response = flask.make_response(rendered_html)
	if is_htmx:
		response_values = {
			'query': query_text,
			'page': page
		}
		response.headers['HX-Title'] = urllib.parse.quote(context['title'])
		response.headers['HX-Push-Url'] = flask.url_for("search", **response_values)
	return response

def search_go_response(query_text: str):
	user = None
	article = core.article.Article(query_text)
	if article.existence:
		return core.response.view_response(article.title)
	else:
		return core.response.search_response(query_text)
	
def go_response(query_text: str):
	return core.response.view_response(query_text)