const editor_insert_position = {
	LEFT: 0,
	CENTER: 1,
	RIGHT: 2
};
Object.freeze(editor_insert_position);

const editor_select_again = {
	NONE: 0,
	PART: 1,
	ALL: 2
};
Object.freeze(editor_select_again);


let editor_section_box;
let editor_button_section_focused;

let editor_link_target;
let editor_link_display;
let editor_link_radio;

let keydown_shift = false;

$(window).on('load', function() {
	editor_section_box = $('#editor_section_box')[0];
	editor_link_target = $('#editor_link_target')[0];
	editor_link_display = $('#editor_link_display')[0];
	editor_link_radio = $('[name = "editor_link_radio"]');
	edit_area = $('#edit_area')[0];
});

function editor_italic() {
	editor_select_insert_single(
		'_', 'Italic Text',
		editor_insert_position.CENTER, editor_select_again.PART
	);
}

function editor_bold() {
	editor_select_insert_single(
		'__', 'Bold Text',
		editor_insert_position.CENTER, editor_select_again.PART
	);
}

function editor_inline_code() {
	editor_select_insert_single(
		'`', 'Inline Code',
		editor_insert_position.CENTER, editor_select_again.PART
	);
}

function editor_blockquote() {
	editor_select_insert_single(
		'>', 'Blockquote',
		editor_insert_position.LEFT, editor_select_again.PART
	);
}

function editor_select_insert_pair(token_front, token_back, empty_replace, position, select_again) {
	let start = edit_area.selectionStart;
	let end = edit_area.selectionEnd;
	let selected = edit_area.value.substring(start, end);
	if (start == end) {
		selected = empty_replace;
	}

	let front_length = token_front.length;
	let back_length = token_back.length;

	switch (position) {
		case editor_insert_position.LEFT: {
			selected = token_front + selected;
			back_length = 0;
		} break;
		case editor_insert_position.CENTER: {
			selected = token_front + selected + token_back;
		} break;
		case editor_insert_position.RIGHT: {
			selected = selected + token_back;
			front_length = 0;
		} break;
	}
	edit_area.focus();
	document.execCommand('insertText', false, selected);
	end = start + selected.length;

	switch (select_again) {
		case editor_select_again.NONE: {
		} break;
		case editor_select_again.PART: {
			edit_area.select();
			edit_area.selectionStart = start + front_length;
			edit_area.selectionEnd = end - back_length;
		} break;
		case editor_select_again.ALL: {
			edit_area.select();
			edit_area.selectionStart = start;
			edit_area.selectionEnd = end;
		} break;
	}
}

function editor_select_insert_single(token_text, empty_replace, position, select_again) {
	editor_select_insert_pair(token_text, token_text, empty_replace, position, select_again);
}

function editor_get_select_block() {
	let selection_start = edit_area.selectionStart;
	let selection_end = edit_area.selectionEnd;
	let edit_end = edit_area.value.length;
	let block_start = selection_start;
	if (edit_area.value.charAt(block_start) == '\n') block_start--;
	while (edit_area.value.charAt(block_start) != '\n' && block_start != 0) block_start--;
	if (block_start != 0) block_start++;
	let block_end = selection_end;
	while (edit_area.value.charAt(block_end) != '\n' && block_end != edit_end) block_end++;
	let block_text = edit_area.value.substring(block_start, block_end);

	return {
		ss: selection_start,
		se: selection_end,
		bs: block_start,
		be: block_end,
		bt: block_text
	};
}

function editor_set_select_block(select_data) {
	edit_area.focus();
	edit_area.select();
	edit_area.selectionStart = select_data.bs;
	edit_area.selectionEnd = select_data.be;
	document.execCommand('insertText', false, select_data.bt);
	edit_area.select();
	edit_area.selectionStart = select_data.ss;
	edit_area.selectionEnd = select_data.se;
}

function editor_insert_tab() {
	let select_data = editor_get_select_block();

	if (select_data.ss != select_data.se) {
		let block_text_lines = select_data.bt.split('\n');
		select_data.bt = block_text_lines.join('\n\t');
		select_data.bt = '\t' + select_data.bt;
		let tab_count = block_text_lines.length;
		if (select_data.bs != select_data.ss) {
			if (edit_area.value.charAt(select_data.ss - 1) != '\t') {
				select_data.ss++;
			}
		}
		select_data.se += tab_count;
		editor_set_select_block(select_data);
	}
	else editor_select_insert_single('\t', '', 0, 0);
}

function editor_remove_tab() {
	let select_data = editor_get_select_block();

	let block_text_lines = select_data.bt.split('\n\t');
	select_data.bt = block_text_lines.join('\n');
	let tab_count = block_text_lines.length;
	if (select_data.bs != select_data.ss)
		if (edit_area.value.charAt(select_data.ss) != '\t') {
			if (select_data.bt.charAt(0) == '\t')
				select_data.ss--;
		}
	else if (select_data.be == select_data.se);
		tab_count--;
	console.log(edit_area.value.charCodeAt(select_data.ss));
	if (select_data.bt.charAt(0) == '\t') {
		select_data.bt = select_data.bt.substring(1);
		tab_count++;
	}
	select_data.se -= tab_count;
	editor_set_select_block(select_data);
}

function editor_extend_link(btn) {
	editor_extend_box('editor_link', btn);
	editor_select_link();
}

function editor_select_link() {
	let selection_start = edit_area.selectionStart;
	let selection_end = edit_area.selectionEnd;

	editor_link_target.value = edit_area.value.substring(selection_start, selection_end);
	editor_link_display.value = ''
}

function editor_insert_link() {
	let link_target = editor_link_target.value;
	let link_display = editor_link_display.value;
	let link_radio = 0;
	for (var i = 0; i < editor_link_radio.length; i++) {
		if (editor_link_radio[i].checked) {
			link_radio = i;
			break;
		}
	}
	let link_text = ''
	if (link_display == '') {
		if (link_radio == 0) {
			link_text = '[[' + link_target + ']]';
		}
		else  {
			link_text = '<' + link_target  + '>';
		}
	}
	else {
		if (link_radio == 0) {
			link_text = '[[' + link_target + '|' + link_display + ']]';
		}
		else {
			link_text = '[' + link_display  + '](' + link_target + ' "' + link_display + '")';
		}
	}
	edit_area.focus();
	document.execCommand('insertText', false, link_text);

	editor_close_section()
}

function editor_close_section() {
	editor_extend_box('editor_link', editor_button_section_focused);
}

function editor_extend_box(id, btn) {
	let block_section;
	for (let i = 0; i < editor_section_box.childNodes.length; i++) {
		var section = editor_section_box.childNodes[i];
		if (section.id == id) {
			block_section = section;
		}
		else if (section.id != undefined) {
			section.style.display = 'none';
		}
	}
	if (editor_button_section_focused != undefined) {
		editor_button_section_focused.removeAttribute('style');
	}
	if (editor_button_section_focused != btn) {
		editor_button_section_focused = btn;
		editor_button_section_focused.style.backgroundColor = '#dfdfdf';
		block_section.style.display = 'block';
	}
	else {
		block_section.style.display = 'none';
		btn.removeAttribute('style');
		editor_button_section_focused = undefined;
	}
	btn.blur();
	edit_area.focus()
}

function editor_keydown(event) {
	switch (event.keyCode) {
		case 9: {
			event.preventDefault();
			if (keydown_shift) {
				editor_remove_tab();
			}
			else {
				editor_insert_tab();
			}
		} break;
		case 16: {
			keydown_shift = true;
		} break;
	}
}

function editor_keyup(event) {
	switch (event.keyCode) {
		case 16: {
			keydown_shift = false;
		} break;
	}
}