class LoginForm {
	constructor() {
		this.username_textbox = document.getElementById('login_username');
		this.password_textbox = document.getElementById('login_password');
		
		this.hash_a = document.getElementById('hash_a');
		this.hash_b = document.getElementById('hash_b');
	
		this.username_textbox.setCustomValidity('Username is required.');
		this.password_textbox.setCustomValidity('Password is required.');

		['load', 'change', 'input'].forEach(function(eventtype) {
			this.username_textbox.addEventListener(eventtype, this.validate_username_textbox);
			this.password_textbox.addEventListener(eventtype, this.validate_password_textbox);
		}, this);
	}

	validate_username_textbox(event) {
		let val = login_form.username_textbox.value;
		let result = true;
		if (val === '') {
			login_form.username_textbox.setCustomValidity('Username is required.');
			result = false;
		}
		else if (val.match(/[\W]/)) {
			login_form.username_textbox.setCustomValidity('Only latin alphabets, numbers, and underscores are allowed.');
			result = false;
		}
		else {
			let is_user_exist = false;
			let form = new FormData();
			form.append('username', val);
			fetch('/is_user_exist/', {
				method: 'POST',
				body: form
			}).then(function(res) {
				return res.json();
			}).then(function(data) {
				is_user_exist = data.is_user_exist;
				if (!is_user_exist) {
					login_form.username_textbox.setCustomValidity('Username that does not exist.');
					result = false;
				}
			});
		}
		if (result) {
			login_form.username_textbox.setCustomValidity('');
		}
	}

	validate_password_textbox(event) {
		let val = login_form.password_textbox.value;
		let reversed_val = val.split('').reverse().join('');
		let hash_a_val = SHA256.createHash("sha256").update(val).digest("hex");
		let hash_b_val = SHA256.createHash("sha256").update(reversed_val).digest("hex");

		login_form.hash_a.value = hash_a_val;
		login_form.hash_b.value = hash_b_val;
		
		let result = true;
		if (val === '') {
			login_form.password_textbox.setCustomValidity('Password is required.');
			result = false;
		}
		else {
			let can_login = false;
			let username_val = login_form.username_textbox.value;
			let form = new FormData();
			form.append('username', username_val);
			form.append('hash_a', hash_a_val);
			form.append('hash_b', hash_b_val);
			fetch('/can_login/', {
				method: 'POST',
				body: form
			}).then(function(res) {
				return res.json();
			}).then(function(data) {
				can_login = data.can_login;
				if (!can_login) {
					login_form.password_textbox.setCustomValidity('Password does not match.');
					result = false;
				}
			});
		}
		if (result) {
			login_form.password_textbox.setCustomValidity('');
		}
	}
}

let login_form;

window.addEventListener('load', function() {
	login_form = new LoginForm();
});