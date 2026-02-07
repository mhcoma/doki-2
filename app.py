import json
import urllib.parse

import flask

import core.article
import core.search
import core.response

app = flask.Flask(__name__)

@app.route("/")
def root():
	return flask.redirect(flask.url_for("view", title="test"))

@app.route("/view/<title>")
def view(title: str):
	no_redirect = flask.request.args.get("noredirect", None)
	redirected_from = flask.request.args.get("from", None)
	return core.response.view_response(title, redirected_from, no_redirect)

@app.route("/edit/<title>")
def edit(title: str):
	return core.response.edit_response(title)

@app.route("/edit-save/<title>", methods=["POST"])
def edit_save(title: str):
	raw_text = flask.request.form.get("raw_text", "")
	return core.response.edit_save_response(title, raw_text)

@app.route("/search-go")
def search_go():
	query_text = flask.request.args.get("query")
	return core.response.search_go_response(query_text)

@app.route("/go")
def go():
	query_text = flask.request.args.get("query")
	return core.response.go_response(query_text)

@app.route("/search")
def search():
	query_text = flask.request.args.get("query")
	return core.response.search_response(query_text)

if __name__ == "__main__":
	app.run()