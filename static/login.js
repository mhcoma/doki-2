$(window).on('load', function() {
	let username_textbox = $('#login_username');
	let password_textbox = $('#login_password');

	username_textbox[0].setCustomValidity('Username is required.');
	password_textbox[0].setCustomValidity('Password is required.');

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
				if (!is_user_exist) {
					username_textbox[0].setCustomValidity('Username that does not exist.');
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
			let result = true;
			if (val === '') {
				password_textbox[0].setCustomValidity('Password is required.');
				result = false;
			}
			else {
				let can_login = false;
				let username = username_textbox.val()
				$.ajax(
					{
						url: `/can_login/?username=${username}&password=${val}`,
						dataType: 'json',
						async: false,
						success: function(user_data) {
							can_login = user_data.can_login;
						}
					}
				)
				if (!can_login) {
					password_textbox[0].setCustomValidity('Password does not match.');
					result = false;
				}
			}
			if (result) {
				password_textbox[0].setCustomValidity('');
			}
		}
	);
});