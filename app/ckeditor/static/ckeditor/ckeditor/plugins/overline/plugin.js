/*
Copyright © 2012, Florian Steffen. All rights reserved.
*/

CKEDITOR.plugins.add('overline', {
	requires: ['styles', 'button'],

	init: function( editor ) {
		var style = new CKEDITOR.style({ 
			element	: 'span',
			"attributes": { 'class': 'overline' }
		});

		editor.attachStyleStateChange(style, function(state) {
			!editor.readOnly && editor.getCommand('overline').setState(state);
		});

		editor.addCommand('overline', new CKEDITOR.styleCommand(style));

		editor.ui.addButton(
			'Overline', 
			{ label: 'Surligné', command: 'overline', icon: 'plugins/overline/icon.png' }
		);
	}
});