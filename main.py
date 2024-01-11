import fastapi
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating
import starlette.middleware.sessions

import core.article
import core.setting
import core.user
import core.editor_data

settings = core.setting.Setting()
editor_data = core.editor_data.EditorData()

app = fastapi.FastAPI()
templates = fastapi.templating.Jinja2Templates(directory = "templates", autoescape = False)
app.mount("/static", fastapi.staticfiles.StaticFiles(directory = "static"), name = "static")

app.add_middleware(
	starlette.middleware.sessions.SessionMiddleware,
	secret_key = settings.secret_key
)

@app.get("/view/{title}", response_class = fastapi.responses.HTMLResponse)
def view(request: fastapi.Request, title: str):
	article = core.article.Article(title)
	article.load()
	article.convert_markdown()

	if 'username' in request.session:
		user = core.user.User(request.session['username'])
	else:
		user = None

	context = dict()
	context['request'] = request
	context['title'] = title
	context['article'] = article
	context['settings'] = settings
	context['user'] = user
	
	response = templates.TemplateResponse(f"{settings.skin}/view.html", context)

	return response

@app.get("/edit/{title}", response_class = fastapi.responses.HTMLResponse)
def edit(request: fastapi.Request, title: str):
	article = core.article.Article(title)
	article.load()

	if 'username' in request.session:
		user = core.user.User(request.session['username'])
	else:
		user = None

	context = dict()
	context['request'] = request
	context['title'] = f"Edit {title}"
	context['article'] = article
	context['settings'] = settings
	context['user'] = user
	context['editor_data'] = editor_data
	
	response = templates.TemplateResponse(f"{settings.skin}/edit.html", context)

	return response


@app.post("/edit-save/{title}", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def edit_save(
	request: fastapi.Request,
	title: str,
	raw_data: str = fastapi.Form(None)
):

	client = request.client
	if not client is None:
		user = client.host
	else:
		user = "Unknown"

	article = core.article.Article(title)
	article.load()
	if raw_data is None:
		raw_data = ""
	raw_data = raw_data.replace('\r', '')
	raw_data = raw_data.strip()
	if not article.existence or raw_data != article.raw_data:
		article.raw_data = raw_data
		article.save(user)
	return f"/view/{title}"

@app.get("/delete/{title}", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def delete(request: fastapi.Request, title: str):
	article = core.article.Article(title)
	article.delete()
	return f"/view/{title}"

@app.get("/get_user/{username}", response_class = fastapi.responses.HTMLResponse)
def get_user(request: fastapi.Request, username: str):
	user = core.user.User(username)
	result = user.get_data()
	return result

@app.get("/login/", response_class = fastapi.responses.HTMLResponse)
def login(request: fastapi.Request):
	context = dict()
	context['request'] = request
	context['title'] = "Login"
	context['settings'] = settings

	if 'username' in request.session:
		return fastapi.responses.RedirectResponse("/", status_code = 303)

	if 'referer' in request.headers:
		http_referer = request.headers['referer']
		request.session['referer'] = http_referer
	
	response = templates.TemplateResponse(f"{settings.skin}/login.html", context)

	return response

@app.post("/login-submit/", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def login_submit(
	response: fastapi.Response,
	request: fastapi.Request,
	username: str = fastapi.Form(),
	password: str = fastapi.Form()
):
	user = core.user.User(username)
	user.login(password, request)

	redirect_url = request.session['referer']

	if not redirect_url:
		return "/"

	request.session.pop('referer', None)

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

	if 'username' in request.session:
		user = core.user.User(request.session['username'])
	else:
		user = None

	context = dict()
	context['request'] = request
	context['title'] = "Join"
	context['settings'] = settings
	context['user'] = user
	
	if 'username' in request.session:
		return fastapi.responses.RedirectResponse("/", status_code = 303)
	
	response = templates.TemplateResponse(f"{settings.skin}/join.html", context)

	return response

@app.post("/join-submit/", response_class = fastapi.responses.RedirectResponse, status_code = 303)
def join_submit(
	request: fastapi.Request,
	username: str = fastapi.Form(),
	password: str = fastapi.Form(),
	confirm_password: str = fastapi.Form(),
	email: str = fastapi.Form()
):
	user = core.user.User(username, password, email)
	join_result = user.join()

	if join_result:
		return "/login/"

	return "/join/"

@app.get("/", response_class = fastapi.responses.RedirectResponse, status_code = 308)
def root(request: fastapi.Request):
	title = settings.mainpage
	return f"/view/{title}"