$(window).on('load', function() {
	let form = $('#join_form')

	form.on('submit', function() {
		let password = $('#password')
		let confirm_password = $('#confirm_password')
		
		if (password.val() != confirm_password.val()) {
			password.val('');
			confirm_password.val('');
			alert('Passwords did not match')
			return false;
		}
		return true;
	});
});