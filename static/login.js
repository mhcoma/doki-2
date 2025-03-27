let username_textbox;
let password_textbox;
let hash_a;
let hash_b;

window.addEventListener('load', function() {
	username_textbox = document.getElementById('login_username');
	password_textbox = document.getElementById('login_password');
	
	hash_a = document.getElementById('hash_a');
	hash_b = document.getElementById('hash_b');

	username_textbox.setCustomValidity('Username is required.');
	password_textbox.setCustomValidity('Password is required.');

	['load', 'change', 'input'].forEach(function(eventtype) {
		username_textbox.addEventListener(eventtype, function(event) {
			let val = username_textbox.value;
			let result = true;
			if (val === '') {
				username_textbox.setCustomValidity('Username is required.');
				result = false;
			}
			else if (val.match(/[\W]/)) {
				username_textbox.setCustomValidity('Only latin alphabets, numbers, and underscores are allowed.');
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
						username_textbox.setCustomValidity('Username that does not exist.');
						result = false;
					}
				});
			}
			if (result) {
				username_textbox.setCustomValidity('');
			}
		});

		password_textbox.addEventListener(eventtype, function(event) {
			let val = password_textbox.value;
			let reversed_val = val.split('').reverse().join('');
			let hash_a_val = SHA256.createHash("sha256").update(val).digest("hex");
			let hash_b_val = SHA256.createHash("sha256").update(reversed_val).digest("hex");

			hash_a.value = hash_a_val;
			hash_b.value = hash_b_val;
			
			let result = true;
			if (val === '') {
				password_textbox.setCustomValidity('Password is required.');
				result = false;
			}
			else {
				let can_login = false;
				let username_val = username_textbox.value;
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
						password_textbox.setCustomValidity('Password does not match.');
						result = false;
					}
				});
			}
			if (result) {
				password_textbox.setCustomValidity('');
			}
		});
	});
});