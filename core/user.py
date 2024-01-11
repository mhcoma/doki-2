import hashlib
import json
import os

import fastapi
import starlette.middleware.sessions

import core

users_directory = os.path.join(core.base_dir, "users")

class User:
	def __init__(self, username: str, password: str | None = None, email: str | None = None):
		self.username = username
		self.user_filename = os.path.join(users_directory, f"{self.username}.json")
		self.existence = os.path.isfile(self.user_filename)

		self.email = email
		self.is_admin = False
		
		if password:
			self.hash_a = hashlib.sha256(password.encode('utf-8')).hexdigest()
			self.hash_b = hashlib.sha256(password[::-1].encode('utf-8')).hexdigest()

		if self.existence:
			user_file = open(self.user_filename, 'r', encoding = "utf-8")
			user_data = json.load(user_file)
			
			if not password:
				self.hash_a = user_data['hash_a']
				self.hash_b = user_data['hash_b']
			
			if not email:
				self.email = user_data['email']
			
			self.is_admin = user_data['is_admin']
			
			user_file.close()

	def join(self) -> bool:
		if self.existence:
			return False

		user_data = dict()
		user_data['username'] = self.username
		user_data['email'] = self.email
		user_data['hash_a'] = self.hash_a
		user_data['hash_b'] = self.hash_b
		user_data['is_admin'] = False

		if not os.path.isdir(users_directory):
			os.makedirs(users_directory)
		user_file = open(self.user_filename, 'w', encoding = "utf-8")
		json.dump(user_data, user_file, indent = '\t')
		user_file.close()

		return True
	
	def login(self, password: str, request: fastapi.Request) -> bool:
		if not self.existence:
			return False

		hash_a = hashlib.sha256(password.encode('utf-8')).hexdigest()
		hash_b = hashlib.sha256(password[::-1].encode('utf-8')).hexdigest()

		result = (hash_a == self.hash_a) and (hash_b == self.hash_b)

		if not result:
			return False

		starlette.middleware.sessions

		session = request.session
		session["username"] = self.username
		session["is_admin"] = self.is_admin

		return True

	def get_data(self) -> str:
		user_data = dict()
		user_data['existence'] = self.existence

		result = json.dumps(user_data)
		return result
