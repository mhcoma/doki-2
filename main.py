import fastapi
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating

import starlette.middleware.sessions

import core.article
import core.setting
import core.user

settings = core.setting.Setting()

app = fastapi.FastAPI()
templates = fastapi.templating.Jinja2Templates(directory = "templates", autoescape = False)
app.mount("/static", fastapi.staticfiles.StaticFiles(directory = "static"), name = "static")

app.add_middleware(starlette.middleware.sessions.SessionMiddleware, secret_key = "asdf")

@app.get("/view/{title}", response_class = fastapi.responses.HTMLResponse)
async def view(request: fastapi.Request, title: str):
	article = core.article.Article(title)
	article.load()
	article.convert_markdown()

	print(request.session)

	context = dict()
	context['request'] = request
	context['title'] = title
	context['settings'] = settings
	context['article'] = article
	
	response = templates.TemplateResponse(f"{settings.skin}/view.html", context)

	return response

@app.get("/edit/{title}", response_class = fastapi.responses.HTMLResponse)
async def edit(request: fastapi.Request, title: str):
	article = core.article.Article(title)
	article.load()

	context = dict()
	context['request'] = request
	context['title'] = f"Edit {title}"
	context['settings'] = settings
	context['article'] = article
	
	response = templates.TemplateResponse(f"{settings.skin}/edit.html", context)

	return response


@app.post("/edit-save/{title}", response_class = fastapi.responses.RedirectResponse, status_code = 303)
async def edit_save(
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
async def delete(request: fastapi.Request, title: str):
	article = core.article.Article(title)
	article.delete()
	return f"/view/{title}"


@app.get("/login/", response_class = fastapi.responses.HTMLResponse)
async def login(request: fastapi.Request):
	context = dict()
	context['request'] = request
	context['title'] = "Login"
	context['settings'] = settings
	
	response = templates.TemplateResponse(f"{settings.skin}/login.html", context)

	return response

@app.get("/join/", response_class = fastapi.responses.HTMLResponse)
async def join(request: fastapi.Request):
	context = dict()
	context['request'] = request
	context['title'] = "Join"
	context['settings'] = settings
	
	response = templates.TemplateResponse(f"{settings.skin}/join.html", context)

	return response

@app.post("/join-submit/", response_class = fastapi.responses.RedirectResponse, status_code = 303)
async def join_submit(
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

@app.post("/login-submit/", response_class = fastapi.responses.RedirectResponse, status_code = 303)
async def login_submit(
	response: fastapi.Response,
	request: fastapi.Request,
	username: str = fastapi.Form(),
	password: str = fastapi.Form()
):
	user = core.user.User(username)
	user.login(password, request)

	return "/"

@app.get("/", response_class = fastapi.responses.RedirectResponse, status_code = 308)
async def root(request: fastapi.Request):
	title = settings.mainpage
	return f"/view/{title}"