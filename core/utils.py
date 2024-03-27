import enum
import json

import fastapi

import core

class AccessLevel(int, enum.Enum):
	ANONYMOUS = 0
	NOOB = 1
	USER = 2
	ADMIN = 3
	def __lt__(self, other):
		if self.__class__ is other.__class__:
			return self.value < other.value
		return NotImplemented
	def __le__(self, other):
		if self.__class__ is other.__class__:
			return self.value <= other.value
		return NotImplemented
	def __gt__(self, other):
		if self.__class__ is other.__class__:
			return self.value > other.value
		return NotImplemented
	def __ge__(self, other):
		if self.__class__ is other.__class__:
			return self.value >= other.value
		return NotImplemented
	def __str__(self):
		return self.name.upper()
	@classmethod
	def _missing_(cls, value):
		if type(value) is str:
			value = value.upper()
			if value in dir(cls):
				return cls[value]

		raise ValueError("%r is not a valid %s" % (value, cls.__name__))

def load_json_file(filename: str):
	file = open(filename, 'r', encoding = "utf-8")
	data = json.load(file)
	file.close()
	return data

def save_json_file(data, filename: str):
	file = open(filename, 'w', encoding = "utf-8")
	json.dump(data, file, indent = '\t')
	file.close()