import setuptools

install_requires = [
	"fastapi>=0.110.0",
	"jinja2>=3.1.3",
	"itsdangerous>=2.1.2",
	"python-multipart>=0.0.9",
	"markdown>=3.6",
	"Pygments>=2.17.0"
	"lxml>=5.2.1",
	"lxml_html_clean>=0.1.0"
]

setuptools.setup(
	name = "doki^2",
	version = "0.1",
	description = "Simple file-based wiki",
	author = "Coma",
	author_email = "bmh4080@naver.com",
	packages = setuptools.find_packages(),
	install_requires = install_requires
)