import hashlib
import json
import os
import datetime
import typing

import fastapi

import core
import core.utils

users_directory = os.path.join(core.base_dir, "users")

class UserData(typing.TypedDict):
	username: str
	hash_a: str
	hash_b: str
	email: str
	is_admin: bool
	join_date: str
	group: list[str]

class User:
	username: str
	hash_a: str
	hash_b: str
	email: str
	is_admin: bool
	group: list[str]

	def __init__(self, username: str, password: str | None = None, email: str | None = None):
		self.username = username
		self.user_filename = os.path.join(users_directory, f"{self.username}.json")
		self.existence = os.path.isfile(self.user_filename)

		self.email: str = email if email != None else ""
		self.is_admin: bool = False

		if password:
			self.hash_a = hashlib.sha256(password.encode('utf-8')).hexdigest()
			self.hash_b = hashlib.sha256(password[::-1].encode('utf-8')).hexdigest()

		if self.existence:
			user_file = open(self.user_filename, 'r', encoding = "utf-8")
			user_data: UserData = json.load(user_file)
			user_file.close()
			
			if not password:
				self.hash_a = user_data['hash_a']
				self.hash_b = user_data['hash_b']
			
			if not email:
				self.email = user_data['email']
			
			self.is_admin = user_data['is_admin']

			self.join_date = datetime.datetime.fromisoformat(user_data['join_date'])
			
			self.group = user_data['group']

	def join(self) -> bool:
		if self.existence:
			return False

		user_data: UserData = {
			'username': self.username,
			'hash_a': self.hash_a,
			'hash_b': self.hash_b,
			'email': self.email,
			'is_admin': False,
			'join_date': datetime.datetime.now(datetime.UTC).isoformat(),
			'group': []
		}

		if not os.path.isdir(users_directory):
			os.makedirs(users_directory)

		core.utils.save_json_file(user_data, self.user_filename)

		return True
	
	def login(self, password: str, request: fastapi.Request) -> bool:
		if not self.can_login(password):
			return False

		session = request.session
		session["username"] = self.username
		session["is_admin"] = self.is_admin

		return True

	def is_user_exist(self) -> bool:
		return self.existence
	
	def can_login(self, password: str) -> bool:
		if not self.existence: return False
		hash_a = hashlib.sha256(password.encode('utf-8')).hexdigest()
		hash_b = hashlib.sha256(password[::-1].encode('utf-8')).hexdigest()
		return (hash_a == self.hash_a) and (hash_b == self.hash_b)
	
	def is_not_noob(self) -> bool:
		return self.join_date + datetime.timedelta(days = 15) <= datetime.datetime.now()

def get_user_from_request(request: fastapi.Request) -> tuple[User | None, str]:
	if 'username' in request.session:
		username = request.session['username']
		return User(username), username
	else:
		client = request.client
		if not client is None:
			username = client.host
		else:
			username = "Unknown"
		return (None, username)