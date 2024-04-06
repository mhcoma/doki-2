let username_textbox;
let password_textbox;
let hash_a;
let hash_b;

$(window).on('load', function() {
	username_textbox = $('#login_username');
	password_textbox = $('#login_password');
	
	hash_a = $('#hash_a');
	hash_b = $('#hash_b');

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
			let reversed_val = val.split('').reverse().join('');
			let hash_a_val = SHA256.createHash("sha256").update(val).digest("hex");
			let hash_b_val = SHA256.createHash("sha256").update(reversed_val).digest("hex");

			hash_a.val(hash_a_val);
			hash_b.val(hash_b_val);
			
			let result = true;
			if (val === '') {
				password_textbox[0].setCustomValidity('Password is required.');
				result = false;
			}
			else {
				let can_login = false;
				let username_val = username_textbox.val()
				$.ajax(
					{
						url: `/can_login/?username=${username_val}&hash_a=${hash_a_val}&hash_b=${hash_b_val}`,
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