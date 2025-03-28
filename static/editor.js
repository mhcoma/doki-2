class Editor {
	constructor() {
		this.section_box = document.getElementById('editor_section_box');
		this.link_target = document.getElementById('editor_link_target')
		this.link_display = document.getElementById('editor_link_display')

		this.link_radio = document.getElementsByName('editor_link_radio');

		this.image_upload = document.getElementById('editor_image_upload');
		this.image_url = document.getElementById('editor_image_url');
		this.image_alt_text = document.getElementById('editor_image_alt_text');
		this.image_upload?.addEventListener('change', function() {
			let form = new FormData();
			form.append('image_file', editor.image_upload.files[0]);
			fetch('/compress-image/', {
				method: 'POST',
				body: form
			}).then(function(res) {
				return res.json();
			}).then(function(data) {
				let compressed_image = data.compressed_image;
				editor.image_url.value = compressed_image;
			});

			editor.image_upload.value = '';
		});
		this.image_radio = document.getElementsByName('editor_image_radio');
		this.image_size = document.getElementById('editor_image_size');
		
		this.image_radio?.forEach(function(element) {
			element.addEventListener('change', function(event) {
				editor.image_size.disabled = editor.image_radio[0].checked;
			});
		}, this);

		this.table_rows = document.getElementById('editor_table_rows');
		this.table_columns = document.getElementById('editor_table_columns');
		this.table_radio = document.getElementsByName('editor_table_radio');

		['load', 'change', 'input'].forEach(function(eventtype) {
			this.table_rows?.addEventListener(eventtype, function(event) {
				validate_int_input(editor.table_rows);
			});
			this.table_columns?.addEventListener(eventtype, function(event) {
				validate_int_input(editor.table_rows);
			});
		}, this);

		this.fenced_code_language = document.getElementById('editor_fenced_code_language');

		this.edit_area = document.getElementById('edit_area');

		this.keydown_shift = false;
		this.keydown_ctrl = false;
	}

	validate_int_input(input_obj) {
		val = input_obj.value;
		input_obj.value = parseInt(val);
	}
	
	italic() {
		editor.select_insert_single(
			'_', 'Italic Text',
			EditorInsertPosition.CENTER, EditorSelectAgainType.PART
		);
	}
	
	bold() {
		editor.select_insert_single(
			'__', 'Bold Text',
			EditorInsertPosition.CENTER, EditorSelectAgainType.PART
		);
	}
	
	inline_code() {
		editor.select_insert_single(
			'`', 'Inline Code',
			EditorInsertPosition.CENTER, EditorSelectAgainType.PART
		);
	}
	
	blockquote() {
		editor.select_insert_single(
			'>', 'Blockquote',
			EditorInsertPosition.LEFT, EditorSelectAgainType.PART
		);
	}
	
	select_insert_pair(token_front, token_back, empty_replace, position, select_again) {
		let start = editor.edit_area.selectionStart;
		let end = editor.edit_area.selectionEnd;
		let selected = editor.edit_area.value.substring(start, end);
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
		editor.edit_area.focus();
		document.execCommand('insertText', false, selected);
		end = start + selected.length;
	
		switch (select_again) {
			case EditorSelectAgainType.NONE: {
			} break;
			case EditorSelectAgainType.PART: {
				editor.edit_area.select();
				editor.edit_area.selectionStart = start + front_length;
				editor.edit_area.selectionEnd = end - back_length;
			} break;
			case EditorSelectAgainType.ALL: {
				editor.edit_area.select();
				editor.edit_area.selectionStart = start;
				editor.edit_area.selectionEnd = end;
			} break;
		}
	}
	
	select_insert_single(token_text, empty_replace, position, select_again) {
		editor.select_insert_pair(token_text, token_text, empty_replace, position, select_again);
	}
	
	get_select_block() {
		let selection_start = editor.edit_area.selectionStart;
		let selection_end = editor.edit_area.selectionEnd;
		let edit_end = editor.edit_area.value.length;
		let block_start = selection_start;
		if (editor.edit_area.value.charAt(block_start) == '\n') block_start--;
		while (editor.edit_area.value.charAt(block_start) != '\n' && block_start != 0) block_start--;
		if (block_start != 0) block_start++;
		let block_end = selection_end;
		while (editor.edit_area.value.charAt(block_end) != '\n' && block_end != edit_end) block_end++;
		let block_text = editor.edit_area.value.substring(block_start, block_end);
	
		return {
			ss: selection_start,
			se: selection_end,
			bs: block_start,
			be: block_end,
			bt: block_text
		};
	}
	
	set_select_block(select_data) {
		editor.edit_area.focus();
		editor.edit_area.select();
		editor.edit_area.selectionStart = select_data.bs;
		editor.edit_area.selectionEnd = select_data.be;
		document.execCommand('insertText', false, select_data.bt);
		editor.edit_area.select();
		editor.edit_area.selectionStart = select_data.ss;
		editor.edit_area.selectionEnd = select_data.se;
	}
	
	insert_tab() {
		let select_data = editor.get_select_block();
	
		if (select_data.ss != select_data.se) {
			let block_text_lines = select_data.bt.split('\n');
			select_data.bt = block_text_lines.join('\n\t');
			select_data.bt = '\t' + select_data.bt;
			let tab_count = block_text_lines.length;
			if (select_data.bs != select_data.ss) {
				if (editor.edit_area.value.charAt(select_data.ss - 1) != '\t') {
					select_data.ss++;
				}
			}
			select_data.se += tab_count;
			editor.set_select_block(select_data);
		}
		else editor.select_insert_single('\t', '', 0, 0);
	}
	
	remove_tab() {
		let select_data = editor.get_select_block();
	
		let block_text_lines = select_data.bt.split('\n\t');
		select_data.bt = block_text_lines.join('\n');
		let tab_count = block_text_lines.length;
		if (select_data.bs != select_data.ss) {
			if (editor.edit_area.value.charAt(select_data.ss) != '\t') {
				if (select_data.bt.charAt(0) == '\t')
					select_data.ss--;
			}
		}
		else if (select_data.be == select_data.se) {
			tab_count--;
		}
		console.log(editor.edit_area.value.charCodeAt(select_data.ss));
		if (select_data.bt.charAt(0) == '\t') {
			select_data.bt = select_data.bt.substring(1);
			tab_count++;
		}
		select_data.se -= tab_count;
		editor.set_select_block(select_data);
	}
	
	insert_line_after() {
		let select_data = editor.get_select_block();
		let tab_count = 0;
		for (let i = 0; i < select_data.bt.length; i++) {
			if (select_data.bt.charAt(i) != '\t') break;
			tab_count += 1;
		}
		select_data.bt = select_data.bt + '\n' + '\t'.repeat(tab_count);
		
		select_data.ss = select_data.be + 1 + tab_count;
		select_data.se = select_data.ss;
		editor.set_select_block(select_data);
	}
	
	insert_line_before() {
		let select_data = editor.get_select_block();
		let tab_count = 0;
		for (let i = 0; i < select_data.bt.length; i++) {
			if (select_data.bt.charAt(i) != '\t') break;
			tab_count += 1;
		}
		select_data.bt = '\t'.repeat(tab_count) + '\n' + select_data.bt;
		
		select_data.ss = select_data.bs + tab_count;
		select_data.se = select_data.ss;
		editor.set_select_block(select_data);
	}
	
	extend_link(btn) {
		editor.extend_box('editor_link', btn);
		editor.select_link();
	}
	
	select_link() {
		let selection_start = editor.edit_area.selectionStart;
		let selection_end = editor.edit_area.selectionEnd;
	
		editor.link_target.value = editor.edit_area.value.substring(selection_start, selection_end);
		editor.link_display.value = '';
	}
	
	insert_link() {
		let link_target = editor.link_target.value;
		let link_display = editor.link_display.value;
		let link_radio = 0;
		for (let i = 0; i < editor.link_radio.length; i++) {
			if (editor.link_radio[i].checked) {
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
		editor.edit_area.focus();
		document.execCommand('insertText', false, link_text);
	
		editor.close_section();
	}
	
	extend_image(btn) {
		editor.extend_box('editor_image', btn);
		editor.image_url.value = '';
	}
	
	insert_image() {
		let alt_text = editor.image_alt_text.value;
		if (alt_text == '') alt_text = 'Image';
		let url_text = editor.image_url.value;
		let width_text = editor.image_size.value;
	
		let img_text;
	
		if (editor.image_radio[0].checked) {
			img_text = `![${alt_text}](${url_text})`;
		}
		else {
			img_text = `<img src="${url_text}" alt="${alt_text}" style="width: ${width_text};">`;
		}
		
		editor.edit_area.focus();
		document.execCommand('insertText', false, img_text);
	
		editor.close_section();
	}
	
	insert_fenced_code() {
		let lang_name = editor.fenced_code_language.options[editor.fenced_code_language.selectedIndex].value
		editor.select_insert_pair(
			'```' + lang_name + '\n', '\n```', 'Fenced Code',
			EditorInsertPosition.CENTER,
			EditorSelectAgainType.PART
		);
	
		editor.edit_area.focus();
	
		editor.close_section();
	}
	
	insert_table() {
		let table_rows = editor.table_rows.value;
		let table_colums = editor.table_columns.value;
	
		let table_radio = 0;
		for (var i = 0; i < editor.table_radio.length; i++) {
			if (editor.table_radio[i].checked) {
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
	
		editor.edit_area.focus();
		document.execCommand('insertText', false, table_text);
	
		editor.close_section();
	}
	
	close_section() {
		editor.extend_box('editor_link', editor.button_section_focused);
	}
	
	extend_box(id, btn) {
		let block_section;
		for (let i = 0; i < editor.section_box.childNodes.length; i++) {
			var section = editor.section_box.childNodes[i];
			if (section.id == id) {
				block_section = section;
			}
			else if (section.id != undefined) {
				section.style.display = 'none';
			}
		}
		if (editor.button_section_focused != undefined) {
			editor.button_section_focused.classList.remove('btn_editor.focused');
		}
		if (editor.button_section_focused != btn) {
			editor.button_section_focused = btn;
			editor.button_section_focused.classList.add('btn_editor.focused');
			block_section.style.display = 'block';
		}
		else {
			block_section.style.display = 'none';
			editor.button_section_focused = undefined;
		}
		btn.blur();
		editor.edit_area.focus();
	}
	
	keydown(event) {
		switch (event.keyCode) {
			case 9: {
				event.preventDefault();
				if (editor.keydown_shift) {
					editor.remove_tab();
				}
				else {
					editor.insert_tab();
				}
			} break;
			case 13: {
				if (editor.keydown_ctrl) {
					event.preventDefault();
					if (editor.keydown_shift) {
						editor.insert_line_before();
					}
					else {
						editor.insert_line_after();
					}
				}
			} break;
			case 16: {
				editor.keydown_shift = true;
			} break;
			case 17: {
				editor.keydown_ctrl = true;
			} break;
		}
	}
	
	keyup(event) {
		switch (event.keyCode) {
			case 16: {
				editor.keydown_shift = false;
			} break;
			case 17: {
				editor.keydown_ctrl = false;
			} break;
		}
	}
}

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

let editor;

window.addEventListener('load', function() {
	editor = new Editor();
});