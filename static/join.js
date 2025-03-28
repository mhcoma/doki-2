class JoinForm {
	constructor() {
		this.username_textbox = document.getElementById('join_username');
		this.password_textbox = document.getElementById('join_password');
		this.confirm_password_textbox = document.getElementById('join_confirm_password')
		this.email_textbox = document.getElementById('join_email');
		
		this.hash_a = document.getElementById('hash_a');
		this.hash_b = document.getElementById('hash_b');

		this.username_textbox.setCustomValidity('Username is required.');
		this.password_textbox.setCustomValidity('Password is required.');
		this.confirm_password_textbox.setCustomValidity('Confirm password is required.');
		this.email_textbox.setCustomValidity('Email is required');

		['load', 'change', 'input'].forEach(function(eventtype) {
			this.username_textbox.addEventListener(eventtype, this.validate_username);
			this.password_textbox.addEventListener(eventtype, this.validate_password);
			this.confirm_password_textbox.addEventListener(eventtype, this.validate_confirm_password);
			this.email_textbox.addEventListener(eventtype, this.validate_email);
		}, this);
	}

	validate_username(event) {
		let val = join_form.username_textbox.value;
		let result = true;
		if (val === '') {
			join_form.username_textbox.setCustomValidity('Username is required.');
			result = false;
		}
		else if (val.match(/[\W]/)) {
			join_form.username_textbox.setCustomValidity('Only latin alphabets, numbers, and underscores are allowed.');
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
					join_form.username_textbox.setCustomValidity('This username is already in use.');
					result = false;
				}
			});
		}
		if (result) {
			join_form.username_textbox.setCustomValidity('');
		}
	}

	validate_password(event) {
		let val = join_form.password_textbox.value;
		let reversed_val = val.split('').reverse().join('');
		if (val === '') {
			join_form.password_textbox.setCustomValidity('Password is required.');
		}
		else {
			join_form.password_textbox.setCustomValidity('');

			let hash_a_txt = SHA256.createHash("sha256").update(val).digest("hex");
			let hash_b_txt = SHA256.createHash("sha256").update(reversed_val).digest("hex");
			
			join_form.hash_a.value = hash_a_txt;
			join_form.hash_b.value = hash_b_txt;
		}
	}

	validate_confirm_password(event) {
		let val = join_form.confirm_password_textbox.value;
		if (val === '') {
			join_form.confirm_password_textbox.setCustomValidity('Confirm password is required.');
		}
		else if (val !== join_form.password_textbox.value) {
			join_form.confirm_password_textbox.setCustomValidity('Confirm password does not match.');
		}
		else {
			join_form.confirm_password_textbox.setCustomValidity('');
		}
	}

	validate_email(event) {
		let val = join_form.email_textbox.value;

		if (val === '') {
			join_form.email_textbox.setCustomValidity('Email is required.');
		}
		else if (
			!val.match(/(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/)
		) {
			join_form.email_textbox.setCustomValidity('Invalid email adress.');
		}
		else {
			join_form.email_textbox.setCustomValidity('');
		}
	}
}

let join_form;

window.addEventListener('load', function() {
	join_form = new JoinForm();
});