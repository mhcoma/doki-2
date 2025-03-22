import json
import typing
import base64
import io

import fastapi
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating
import starlette.middleware.sessions

import PIL.Image

import core
import core.article
import core.user
import core.utils
import core.settings
import core.editor_data

app = fastapi.FastAPI()
templates = fastapi.templating.Jinja2Templates(directory = "templates", autoescape = False)
app.mount("/static", fastapi.staticfiles.StaticFiles(directory = "static"), name = "static")

app.add_middleware(
	starlette.middleware.sessions.SessionMiddleware,
	secret_key = core.settings.instance.secret_key
)

@app.get("/view", response_class = fastapi.responses.RedirectResponse)
@app.get("/view/", response_class = fastapi.responses.RedirectResponse)
@app.get("/view/{title}", response_class = fastapi.responses.HTMLResponse)
def view(request: fastapi.Request, title: typing.Optional[str] = None):
	if title == None:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	
	user, username = core.user.get_user_from_request(request)
	
	article = core.article.Article(title)
	article.load()
	codehilite = core.user.get_codehilite(user)
	article.render_markdown(codehilite)

	is_viewable = article.is_accessable('view', user)
	is_editable = article.is_accessable('edit', user)
	is_deletable = article.is_accessable('delete', user)
	is_movable = article.is_accessable('move', user)
	can_change_acl = article.is_accessable('acl', user)

	context: dict[str, typing.Any] = {
		'request': request,
		'title': title,
		'article': article,
		'settings': core.settings.instance,
		'user': user,
		'is_viewable': is_viewable,
		'is_editable': is_editable,
		'is_deletable': is_deletable,
		'is_movable': is_movable,
		'can_change_acl': can_change_acl,
		'codehilite': codehilite
	}
	
	response = templates.TemplateResponse(f"{core.settings.instance.skin}/view.html", context)

	return response

@app.get("/source", response_class = fastapi.responses.RedirectResponse)
@app.get("/source/", response_class = fastapi.responses.RedirectResponse)
@app.get("/source/{title}", response_class = fastapi.responses.HTMLResponse)
def view_source(request: fastapi.Request, title: typing.Optional[str] = None):
	if title == None:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	
	article = core.article.Article(title)
	article.load()

	user, username = core.user.get_user_from_request(request)

	context: dict[str, typing.Any] = {
		'request': request,
		'title': f"View source for {title}",
		'article': article,
		'settings': core.settings.instance,
		'user': user,
		'editor_data': core.editor_data.instance
	}

	response = templates.TemplateResponse(f"{core.settings.instance.skin}/source.html", context)

	return response

@app.get("/edit", response_class = fastapi.responses.RedirectResponse)
@app.get("/edit/", response_class = fastapi.responses.RedirectResponse)
@app.get("/edit/{title}", response_class = fastapi.responses.HTMLResponse)
def edit(request: fastapi.Request, title: typing.Optional[str] = None):
	if title == None:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	article = core.article.Article(title)
	article.load()

	user, username = core.user.get_user_from_request(request)

	is_editable = article.is_accessable('edit', user)
	if not is_editable:
		return fastapi.responses.RedirectResponse(f"/source/{title}")
	
	context: dict[str, typing.Any] = {
		'request': request,
		'title': f"Edit {title}",
		'article': article,
		'settings': core.settings.instance,
		'user': user,
		'editor_data': core.editor_data.instance
	}
	
	response = templates.TemplateResponse(f"{core.settings.instance.skin}/edit.html", context)

	return response

@app.get("/edit-save", response_class = fastapi.responses.RedirectResponse)
@app.get("/edit-save/", response_class = fastapi.responses.RedirectResponse)
@app.post("/edit-save/{title}", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def edit_save(
	request: fastapi.Request,
	title: typing.Optional[str] = None,
	raw_data: str = fastapi.Form(None)
):
	if title == None:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	
	user, username = core.user.get_user_from_request(request)

	article = core.article.Article(title)
	article.load()

	is_editable = article.is_accessable('edit', user)

	if is_editable:
		if raw_data is None:
			raw_data = ""
		raw_data = raw_data.replace('\r', '').strip()
		if not article.existence or raw_data != article.raw_data:
			article.raw_data = raw_data
			article.save(username)
	
	return f"/view/{title}"

@app.get("/acl", response_class = fastapi.responses.RedirectResponse)
@app.get("/acl/", response_class = fastapi.responses.RedirectResponse)
@app.get("/acl/{title}", response_class = fastapi.responses.HTMLResponse)
def acl(request: fastapi.Request, title: typing.Optional[str] = None):
	if title == None:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	article = core.article.Article(title)
	article.load()

	user, username = core.user.get_user_from_request(request)

	can_change_acl = article.is_accessable('acl', user)
	if not can_change_acl:
		return fastapi.responses.RedirectResponse(f"/view/{title}")
	
	context: dict[str, typing.Any] = {
		'request': request,
		'title': f"Change ACL of {title}",
		'article': article,
		'settings': core.settings.instance,
		'user': user
	}
	
	response = templates.TemplateResponse(f"{core.settings.instance.skin}/acl.html", context)

	return response

@app.get("/acl-save", response_class = fastapi.responses.RedirectResponse)
@app.get("/acl-save/", response_class = fastapi.responses.RedirectResponse)
@app.post("/acl-save/{title}", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def acl_save(
	request: fastapi.Request,
	title: typing.Optional[str] = None,
	raw_acl_data: str = fastapi.Form(None)
):
	if title == None:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	
	user, username = core.user.get_user_from_request(request)

	article = core.article.Article(title)
	article.load()

	can_change_acl = article.is_accessable('acl', user)

	if can_change_acl:
		if raw_acl_data is None:
			raw_acl_data = core.settings.instance.default_acl.copy()
		raw_acl_data = raw_acl_data.replace('\r', '').strip()
		if not article.existence or raw_acl_data != article.raw_acl_data:
			article.raw_acl_data = raw_acl_data
			article.save(username)
	
	return f"/view/{title}"

@app.get("/delete", response_class = fastapi.responses.RedirectResponse)
@app.get("/delete/", response_class = fastapi.responses.RedirectResponse)
@app.get("/delete/{title}", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def delete(request: fastapi.Request, title: typing.Optional[str] = None):
	if title == None:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	
	user, username = core.user.get_user_from_request(request)

	article = core.article.Article(title)
	article.load(load_type = core.article.ArticleLoadType.DELETE)
	is_deletable = article.is_accessable('delete', user)

	if is_deletable:
		article.delete()
	return f"/view/{title}"

@app.get("/search-go/", response_class = fastapi.responses.RedirectResponse)
def search_go(request: fastapi.Request, search_text: str = ""):
	if core.article.Article.find_article(search_text):
		return fastapi.responses.RedirectResponse(f"/view/{search_text}", status_code = 303)
	return fastapi.responses.RedirectResponse(f"/search/?query={search_text}", status_code = 303)

@app.get("/search", response_class = fastapi.responses.HTMLResponse)
@app.get("/search/", response_class = fastapi.responses.HTMLResponse)
def search(request: fastapi.Request, query: str = ""):
	result = core.article.Article.search_files(query)
	context: dict[str, typing.Any] = {
		'request': request,
		'settings': core.settings.instance,
		'title' : f"Search for {query}",
		'result': result,
		'text': query,
		'article_existence': core.article.Article.find_article(query),
	}

	response = templates.TemplateResponse(f"{core.settings.instance.skin}/search.html", context)
	return response

@app.get("/is_user_exist/", response_class = fastapi.responses.HTMLResponse)
def is_user_exist(request: fastapi.Request, username: str):
	user = core.user.User(username)
	result = dict()
	result['is_user_exist'] = user.is_user_exist()
	return json.dumps(result)

@app.get("/can_login/", response_class = fastapi.responses.HTMLResponse)
def can_login(request: fastapi.Request, username: str, hash_a: str, hash_b: str):
	user = core.user.User(username)
	result = dict()
	result['can_login'] = user.can_login(hash_a, hash_b)
	return json.dumps(result)

@app.get("/login/", response_class = fastapi.responses.HTMLResponse)
def login(request: fastapi.Request):

	context: dict[str, typing.Any] = {
		'request': request,
		'settings': core.settings.instance,
		'editor_data': core.editor_data.instance
	}

	if 'username' in request.session:
		redirect_url = "/"
		return fastapi.responses.RedirectResponse(redirect_url, status_code = 303)

	if 'referer' in request.headers:
		http_referer = request.headers['referer']
		request.session['referer'] = http_referer
	
	response = templates.TemplateResponse(f"{core.settings.instance.skin}/login.html", context)

	return response

@app.post("/login-submit/", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def login_submit(
	response: fastapi.Response,
	request: fastapi.Request,
	username: str = fastapi.Form(),
	password: str = fastapi.Form(),
	hash_a: str = fastapi.Form(),
	hash_b: str = fastapi.Form(),
):
	user = core.user.User(username)
	result = user.login(hash_a, hash_b, request)

	redirect_url = request.session['referer'] if result else "/login/"

	if result:
		if not redirect_url:
			return "/"
		request.session.pop('referer', None)
	else:
		print(request.session['referer'])

	return redirect_url

@app.get("/logout/", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def logout(request: fastapi.Request):

	redirect_url = request.headers['referer']
	request.session.pop('username', None)
	request.session.pop('is_admin', None)
	
	if not redirect_url:
		return "/"

	return redirect_url

@app.get("/join/", response_class = fastapi.responses.HTMLResponse)
def join(request: fastapi.Request):
	user, username = core.user.get_user_from_request(request)

	context: dict[str, typing.Any] = {
		'request': request,
		'title': "Join",
		'settings': core.settings.instance,
		'user': user,
	}
	
	if 'username' in request.session:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	
	response = templates.TemplateResponse(f"{core.settings.instance.skin}/join.html", context)

	return response

@app.post("/join-submit/", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def join_submit(
	request: fastapi.Request,
	username: str = fastapi.Form(),
	password: str = fastapi.Form(),
	confirm_password: str = fastapi.Form(),
	hash_a: str = fastapi.Form(),
	hash_b: str = fastapi.Form(),
	email: str = fastapi.Form()
):
	user = core.user.User(username, hash_a, hash_b, email)
	join_result = user.join()

	if join_result:
		return "/login/"

	return "/join/"

@app.post("/compress-image/", response_class = fastapi.responses.HTMLResponse)
def compress_image(request: fastapi.Request, image_file: fastapi.UploadFile = fastapi.Form()):
	format: str
	match image_file.content_type:
		case "image/apng" | "image/gif" | "image/png" | "image/webp":
			format = "webp"
		case "image/jpeg":
			format = "jpeg"
		case "image/svg+xml":
			format = "svg+xml"
		case _:
			return ""

	if format == "svg+xml":
		image_data = image_file.file.read()
	else:
		image = PIL.Image.open(image_file.file)

		buffer = io.BytesIO()
		ext = image.format

		if "duration" in image.info:
			image.save(buffer, format = format, save_all = True, duration = image.info['duration'])
		else:
			image.save(buffer, format = format)
		image_data = buffer.getvalue()
	image_str = f"data:image/{format};base64," + base64.b64encode(image_data).decode("utf-8")

	result = dict()
	result['compressed_image'] = image_str
	return json.dumps(result)

@app.get("/", response_class = fastapi.responses.RedirectResponse, status_code = 308)
def root(request: fastapi.Request):
	title = core.settings.instance.mainpage
	return f"/view/{title}"