$(window).on('load', function() {
	let username_textbox = $('#join_username');
	let password_textbox = $('#join_password');
	let confirm_password_textbox = $('#join_confirm_password');
	let email_textbox = $('#join_email');

	username_textbox[0].setCustomValidity('Username is required.');
	password_textbox[0].setCustomValidity('Password is required.');
	confirm_password_textbox[0].setCustomValidity('Confirm password is required.');
	email_textbox[0].setCustomValidity('Email is required');

	username_textbox.on(
		'load change input',
		function(event) {
			let val = username_textbox.val();
			let result = true;
			if (val === '') {
				username_textbox[0].setCustomValidity('Username is required.');
				result = false;
			}
			else if (val.match(/[\W]/)) {
				username_textbox[0].setCustomValidity('Only latin alphabets, numbers, and underscores are allowed.');
				result = false;
			}
			else {
				let is_user_exist = false;
				$.ajax(
					{
						url: `/is_user_exist/?username=${val}`,
						dataType: 'json',
						async: false,
						success: function(user_data) {
							is_user_exist = user_data.is_user_exist;
						}
					}
				);
				if (is_user_exist) {
					username_textbox[0].setCustomValidity('This username is already in use.');
					result = false;
				}
			}
			if (result) {
				username_textbox[0].setCustomValidity('');
			}
		}
	);

	password_textbox.on(
		'load change input',
		function(event) {
			let val = password_textbox.val();
			if (val === '') {
				password_textbox[0].setCustomValidity('Password is required.');
			}
			else {
				password_textbox[0].setCustomValidity('');
			}
		}
	);

	confirm_password_textbox.on(
		'load change input',
		function(event) {
			let val = confirm_password_textbox.val();
			if (val === '') {
				confirm_password_textbox[0].setCustomValidity('Confirm password is required.');
			}
			else if (val !== password_textbox.val()) {
				confirm_password_textbox[0].setCustomValidity('Confirm password does not match.');
			}
			else {
				confirm_password_textbox[0].setCustomValidity('');
			}
		}
	);

	email_textbox.on(
		'load change input',
		function(event) {
			let val = email_textbox.val();

			if (val === '') {
				email_textbox[0].setCustomValidity('Email is required.');
			}
			else if (
				!val.match(/(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/)
			) {
				email_textbox[0].setCustomValidity('Invalid email adress.');
			}
			else {
				email_textbox[0].setCustomValidity('');
			}
		}
	)
});