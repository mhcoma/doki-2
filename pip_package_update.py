import os

os.system("pip freeze > package.txt")

pkg_filename = "package.txt"
pkg_file = open(pkg_filename, "r")
pkg_text = pkg_file.read().replace("==", ">=")
pkg_file.close()
pkg_file = open(pkg_filename, "w")
pkg_file.write(pkg_text)
pkg_file.close()

os.system("pip install -r package.txt --upgrade")