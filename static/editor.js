const EditorInsertPosition = {
	LEFT: 0,
	CENTER: 1,
	RIGHT: 2
};
Object.freeze(EditorInsertPosition);

const EditorSelectAgainType = {
	NONE: 0,
	PART: 1,
	ALL: 2
};
Object.freeze(EditorSelectAgainType);


let editor_section_box;
let editor_button_section_focused;

let editor_link_target;
let editor_link_display;
let editor_link_radio;

let editor_image_upload;
let editor_image_url;
let editor_image_alt_text;
let editor_image_radio;
let editor_image_size;

let editor_table_rows;
let editor_table_columns;
let editor_table_radio;

let editor_fenced_code_language;

let keydown_shift = false;
let keydown_ctrl = false;

window.addEventListener('load', function() {
	editor_section_box = document.getElementById('editor_section_box');
	editor_link_target = document.getElementById('editor_link_target')
	editor_link_display = document.getElementById('editor_link_display')

	editor_link_radio = document.getElementsByName('editor_link_radio');

	editor_image_upload = document.getElementById('editor_image_upload');
	editor_image_url = document.getElementById('editor_image_url');
	editor_image_alt_text = document.getElementById('editor_image_alt_text');
	editor_image_upload?.addEventListener('change', function() {
		let form = new FormData();
		form.append('image_file', editor_image_upload.files[0]);
		fetch('/compress-image/', {
			method: 'POST',
			body: form
		}).then(function(res) {
			return res.json();
		}).then(function(data) {
			let compressed_image = data.compressed_image;
			editor_image_url.value = compressed_image;
		});

		editor_image_upload.value = '';
	});
	editor_image_radio = document.getElementsByName('editor_image_radio');
	editor_image_size = document.getElementById('editor_image_size');
	
	editor_image_radio?.forEach(function(element) {
		element.addEventListener('change', function(event) {
			editor_image_size.disabled = editor_image_radio[0].checked;
		});
	});

	editor_table_rows = document.getElementById('editor_table_rows');
	editor_table_columns = document.getElementById('editor_table_columns');
	editor_table_radio = document.getElementsByName('editor_table_radio');

	['load', 'change', 'input'].forEach(function(eventtype) {
		editor_table_rows?.addEventListener(eventtype, function(event) {
			validate_int_input(editor_table_rows);
		});
		editor_table_columns?.addEventListener(eventtype, function(event) {
			validate_int_input(editor_table_rows);
		});
	});

	editor_fenced_code_language = document.getElementsByName('editor_fenced_code_language');

	edit_area = this.document.getElementById('edit_area');
});

function validate_int_input(input_obj) {
	val = input_obj.value;
	input_obj.value = parseInt(val);
}

function editor_italic() {
	editor_select_insert_single(
		'_', 'Italic Text',
		EditorInsertPosition.CENTER, EditorSelectAgainType.PART
	);
}

function editor_bold() {
	editor_select_insert_single(
		'__', 'Bold Text',
		EditorInsertPosition.CENTER, EditorSelectAgainType.PART
	);
}

function editor_inline_code() {
	editor_select_insert_single(
		'`', 'Inline Code',
		EditorInsertPosition.CENTER, EditorSelectAgainType.PART
	);
}

function editor_blockquote() {
	editor_select_insert_single(
		'>', 'Blockquote',
		EditorInsertPosition.LEFT, EditorSelectAgainType.PART
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
		case EditorInsertPosition.LEFT: {
			selected = token_front + selected;
			back_length = 0;
		} break;
		case EditorInsertPosition.CENTER: {
			selected = token_front + selected + token_back;
		} break;
		case EditorInsertPosition.RIGHT: {
			selected = selected + token_back;
			front_length = 0;
		} break;
	}
	edit_area.focus();
	document.execCommand('insertText', false, selected);
	end = start + selected.length;

	switch (select_again) {
		case EditorSelectAgainType.NONE: {
		} break;
		case EditorSelectAgainType.PART: {
			edit_area.select();
			edit_area.selectionStart = start + front_length;
			edit_area.selectionEnd = end - back_length;
		} break;
		case EditorSelectAgainType.ALL: {
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
	if (select_data.bs != select_data.ss) {
		if (edit_area.value.charAt(select_data.ss) != '\t') {
			if (select_data.bt.charAt(0) == '\t')
				select_data.ss--;
		}
	}
	else if (select_data.be == select_data.se) {
		tab_count--;
	}
	console.log(edit_area.value.charCodeAt(select_data.ss));
	if (select_data.bt.charAt(0) == '\t') {
		select_data.bt = select_data.bt.substring(1);
		tab_count++;
	}
	select_data.se -= tab_count;
	editor_set_select_block(select_data);
}

function editor_insert_line_after() {
	let select_data = editor_get_select_block();
	let tab_count = 0;
	for (let i = 0; i < select_data.bt.length; i++) {
		if (select_data.bt.charAt(i) != '\t') break;
		tab_count += 1;
	}
	select_data.bt = select_data.bt + '\n' + '\t'.repeat(tab_count);
	
	select_data.ss = select_data.be + 1 + tab_count;
	select_data.se = select_data.ss;
	editor_set_select_block(select_data);
}

function editor_insert_line_before() {
	let select_data = editor_get_select_block();
	let tab_count = 0;
	for (let i = 0; i < select_data.bt.length; i++) {
		if (select_data.bt.charAt(i) != '\t') break;
		tab_count += 1;
	}
	select_data.bt = '\t'.repeat(tab_count) + '\n' + select_data.bt;
	
	select_data.ss = select_data.bs + tab_count;
	select_data.se = select_data.ss;
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
	editor_link_display.value = '';
}

function editor_insert_link() {
	let link_target = editor_link_target.value;
	let link_display = editor_link_display.value;
	let link_radio = 0;
	for (let i = 0; i < editor_link_radio.length; i++) {
		if (editor_link_radio[i].checked) {
			link_radio = i;
			break;
		}
	}
	let link_text = '';
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

	editor_close_section();
}

function editor_extend_image(btn) {
	editor_extend_box('editor_image', btn);
	editor_image_url.value = '';
}

function editor_insert_image() {
	let alt_text = editor_image_alt_text.value;
	if (alt_text == '') alt_text = 'Image';
	let url_text = editor_image_url.value;
	let width_text = editor_image_size.value;

	let img_text;

	if (editor_image_radio[0].checked) {
		img_text = `![${alt_text}](${url_text})`;
	}
	else {
		img_text = `<img src="${url_text}" alt="${alt_text}" style="width: ${width_text};">`;
	}
	
	edit_area.focus();
	document.execCommand('insertText', false, img_text);

	editor_close_section();
}

function editor_insert_fenced_code() {
	editor_select_insert_pair(
		'```' + editor_fenced_code_language.val() + '\n', '\n```', 'Fenced Code',
		EditorInsertPosition.CENTER,
		EditorSelectAgainType.PART
	);

	edit_area.focus();

	editor_close_section();
}

function editor_insert_table() {
	let table_rows = editor_table_rows.val();
	let table_colums = editor_table_columns.val();

	let table_radio = 0;
	for (var i = 0; i < editor_table_radio.length; i++) {
		if (editor_table_radio[i].checked) {
			table_radio = i;
			break;
		}
	}

	let table_text = '';

	if (table_radio == 0) {
		for (var i = 0; i < table_rows; i++) {
			for (var j = 0; j < table_colums; j++) {
				table_text += "|   ";
			}
			table_text += "|\n";
			if (i == 0) {
				for (var j = 0; j < table_colums; j++) {
					table_text += "|---";
				}
				table_text += "|\n";
			}
		}
	}
	else {
		table_text += "<table>\n";

		if (table_radio == 1) {
			table_text += "\t<thead>\n\t\t<tr>\n";
			for (var i = 0; i < table_colums; i++) {
				table_text += "\t\t\t<th>   </th>\n"
			}
			table_text += "\t\t</tr>\n\t</thead>\n";
			table_rows--;
		}

		table_text += "\t<tbody>\n";
		for (var i = 0; i < table_rows; i++) {
			table_text += "\t\t<tr>\n";
			for (var j = 0; j < table_colums; j++) {
				table_text += "\t\t\t<td>   </td>\n"
			}
			table_text += "\t\t</tr>\n";
		}
		table_text += "\t</tbody>\n";

		table_text += "</table>\n";
	}

	edit_area.focus();
	document.execCommand('insertText', false, table_text);

	editor_close_section();
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
		editor_button_section_focused.classList.remove('btn_editor_focused');
	}
	if (editor_button_section_focused != btn) {
		editor_button_section_focused = btn;
		editor_button_section_focused.classList.add('btn_editor_focused');
		block_section.style.display = 'block';
	}
	else {
		block_section.style.display = 'none';
		editor_button_section_focused = undefined;
	}
	btn.blur();
	edit_area.focus();
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
		case 13: {
			if (keydown_ctrl) {
				event.preventDefault();
				if (keydown_shift) {
					editor_insert_line_before();
				}
				else {
					editor_insert_line_after();
				}
			}
		} break;
		case 16: {
			keydown_shift = true;
		} break;
		case 17: {
			keydown_ctrl = true;
		} break;
	}
}

function editor_keyup(event) {
	switch (event.keyCode) {
		case 16: {
			keydown_shift = false;
		} break;
		case 17: {
			keydown_ctrl = false;
		} break;
	}
}