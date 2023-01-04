var header_search_bar;
var header_menu_btn;
var header_menu_box;

var menu_display = false;

$(window).on("load", function() {
	header_search_bar = document.getElementById('header_search_bar');
	header_menu_btn = document.getElementById('header_menu_btn');
	header_menu_box = document.getElementById('header_menu_box');
});

function toggle_menu() {
	if (menu_display) {
		document.getElementById('header_menu_btn').childNodes[0].src = '/static/modern/symbol_menu.svg'
		header_menu_box.style.display = 'none';
	}
	else {
		document.getElementById('header_menu_btn').childNodes[0].src = '/static/modern/symbol_close.svg'
		header_menu_box.style.display = 'block';
	}
	menu_display = !menu_display;
}