import setuptools

install_requires = [
	"fastapi>=0.88.0",
	"jinja2>=3.1.2",
	"itsdangerous>=2.1.2",
	"python-multipart>=0.0.5",
	"markdown>=3.4.1",
	"Pygments>=2.14.0"
]

setuptools.setup(
	name = "doki^2",
	version = "0.1",
	description = "Simple wiki based on FastAPI",
	author = "Coma",
	author_email = "bmh4080@naver.com",
	packages = setuptools.find_packages(),
	install_requires = install_requires
)