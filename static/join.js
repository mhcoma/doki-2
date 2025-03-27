let username_textbox;
let password_textbox;
let confirm_password_textbox;
let email_textbox;
let hash_a;
let hash_b;

window.addEventListener('load', function() {
	username_textbox = document.getElementById('join_username');
	password_textbox = document.getElementById('join_password');
	confirm_password_textbox = document.getElementById('join_confirm_password')
	email_textbox = document.getElementById('join_email');
	
	hash_a = document.getElementById('hash_a');
	hash_b = document.getElementById('hash_b');

	username_textbox.setCustomValidity('Username is required.');
	password_textbox.setCustomValidity('Password is required.');
	confirm_password_textbox.setCustomValidity('Confirm password is required.');
	email_textbox.setCustomValidity('Email is required');

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
					if (is_user_exist) {
						username_textbox.setCustomValidity('This username is already in use.');
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
			if (val === '') {
				password_textbox.setCustomValidity('Password is required.');
			}
			else {
				password_textbox.setCustomValidity('');

				let hash_a_txt = SHA256.createHash("sha256").update(val).digest("hex");
				let hash_b_txt = SHA256.createHash("sha256").update(reversed_val).digest("hex");
				
				hash_a.value = hash_a_txt;
				hash_b.value = hash_b_txt;
			}
		});

		confirm_password_textbox.addEventListener(eventtype, function(event) {
			let val = confirm_password_textbox.value;
			if (val === '') {
				confirm_password_textbox.setCustomValidity('Confirm password is required.');
			}
			else if (val !== password_textbox.value) {
				confirm_password_textbox.setCustomValidity('Confirm password does not match.');
			}
			else {
				confirm_password_textbox.setCustomValidity('');
			}
		});

		email_textbox.addEventListener(eventtype, function(event) {
			let val = email_textbox.value;

			if (val === '') {
				email_textbox.setCustomValidity('Email is required.');
			}
			else if (
				!val.match(/(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/)
			) {
				email_textbox.setCustomValidity('Invalid email adress.');
			}
			else {
				email_textbox.setCustomValidity('');
			}
		});
	});
});