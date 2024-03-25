import pygments.lexers

import core

class EditorData:
	codehilite_lexers: list[tuple[str, str]]
	major_languages: tuple[str, ...]
	alternative_names: dict[str, str]

	def __init__(self):
		self.major_languages = (
			"ABAP",
			"Ada",
			"Agda",
			"Arturo",
			"AutoIt",
			"autohotkey",
			"Awk",
			"Bash",
			"Batchfile",
			"C",
			"CMake",
			"C#",
			"Carbon",
			"ChaiScript",
			"Clojure",
			"ClojureScript",
			"COBOL",
			"CoffeeScript",
			"Common Lisp",
			"Coq",
			"C++",
			"Crystal",
			"CSS",
			"CUDA",
			"D",
			"Dart",
			"Delphi",
			"Diff",
			"Docker",
			"Dylan",
			"Eiffel",
			"Elixir",
			"Elm"
			"EmacsLisp",
			"Erlang",
			"F#",
			"Factor",
			"Fish",
			"Forth",
			"Fortran",
			"FoxPro",
			"GDScript",
			"GLSL",
			"Go",
			"Golo",
			"Gosu",
			"GraphQL",
			"Groovy",
			"HLSL",
			"Haskell",
			"Haxe",
			"HTML",
			"Hy",
			"Idris",
			"INI",
			"Io",
			"Ioke",
			"J",
			"Java",
			"JavaScript",
			"JSON",
			"JSX",
			"Julia",
			"Kotlin",
			"Lean",
			"LessCss",
			"Lua",
			"Makefile",
			"Markdown",
			"NestedText",
			"NewLisp",
			"Nimrod",
			"Nix"
			"Objective-C",
			"OCaml",
			"Octave",
			"ODIN",
			"Perl6",
			"Perl",
			"PHP",
			"Pike",
			"Pony",
			"PostScript",
			"PowerShell",
			"Prolog",
			"Properties",
			"Python",
			"QBasic",
			"QML",
			"Racket",
			"REBOL",
			"Red",
			"Rexx",
			"Ruby",
			"Rust",
			"SAS",
			"S",
			"Standard ML",
			"Sass",
			"Scala",
			"Scheme",
			"SCSS",
			"Smalltalk",
			"Solidity",
			"SQL",
			"Stata",
			"Swift",
			"SWIG",
			"TOML",
			"Tcl",
			"Tcsh",
			"TeX",
			"Text only",
			"Twig",
			"TypeScript",
			"VBScript",
			"Vala",
			"VB.net",
			"verilog",
			"vhdl",
			"VimL",
			"WebAssembly",
			"XML",
			"YAML",
			"Zig"
		)
		self.alternative_names = {
			"autohotkey" : "AutoHotKey",
			"Batchfile" : "Batch File",
			"Nimrod" : "Nim",
			"Perl6" : "Raku",
			"Text only" : "Plain Text",
			"verilog" : "Verilog",
			"vhdl" : "VHDL",
			"VimL" : "Vim Script"
		}
		self.get_lexer_list()

	def get_lexer_list(self):
		self.codehilite_lexers = [
			("None", ""),
			("", "")
		]
		for name in self.major_languages:
			for lexer in pygments.lexers.get_all_lexers():
				if name == lexer[0]:
					self.codehilite_lexers.append((self.get_alternative_name(name), lexer[1][0]))
					break

		self.codehilite_lexers.append(("", ""))

		all_lexers = pygments.lexers.get_all_lexers()
		for lexer in all_lexers:
			name = lexer[0]
			if name in self.major_languages:
				continue
			if (len(lexer[1]) > 0):
				self.codehilite_lexers.append((self.get_alternative_name(name), lexer[1][0]))
	
	def get_alternative_name(self, name: str) -> str:
		if name in self.alternative_names:
			return self.alternative_names[name]
		return name