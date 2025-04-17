/* Footnote Plugin for CKEDITOR v0.1
 * This plugin stores the footnote contents (escaped) in the @data-note.
 * The automatic numbering is taken care of using the CSS counter directive.
 * The CSS stylesheet rules are defined in tinyMCE_transcripts.css
 * 
 * Michael Hawkins
 */

CKEDITOR.plugins.add('footnote', {

    init: function(editor){
        var ckeditor_instance_id='';
        var cur_lang = editor.config.language || CKEDITOR.lang.detect(CKEDITOR.config.defaultLanguage);
        var transcription_strings = {
            en: {
                label: "[Footnote]",
                title: {
                    'note-editorial': 'This is an editorial footnote',
                    'note-document': 'This is a document footnote'
                },
                context_edit: 'Edit Footnote',
                context_delete: 'Delete Footnote',
                dialog_title: 'Footnote Properties',
                dialog_note_text: 'Footnote Contents',
                dialog_note_text_empty_error: "footnote cannot be empty",
                location_label: "Type of footnote",
                location_select: [['Editorial Footnote', 'note-editorial'], ['Document Footnote', 'note-document']],
            },
            fr: {
                    label: "[Note de bas de page]",
                    title: {
                        'note-editorial': 'Editorial footnote',
                        'not-document': 'Document footnote'
                    },
                    context_edit: 'Modifier la note',
                    context_delete: 'Supprimer la note',
                    dialog_title: 'Paramètres de la note',
                    dialog_note_text: 'Contenu de la note',
                    dialog_note_text_empty_error: "la note ne peut pas être vide",
                    location_label: "Type de note",
                    location_select: [['Note éditoriale', 'note-editorial'], ['Note de document', 'note-document']],
                }
            };
        var local_lang = transcription_strings[cur_lang];
        
        editor.addCommand('footnoteDialog', new CKEDITOR.dialogCommand('footnoteDialog'));
        
        editor.ui.addButton('Footnote', {
            label: local_lang.label,
            command: 'footnoteDialog',
            //icon: iconPath,
            className: "x-cke_label_button"
        });
        editor.addCommand('removeFootnote', {
            exec: function(editor){
                var sel = editor.getSelection(), element = sel.getStartElement();
                el = getContainer(element);
                el.remove();
            }
        });
        if (editor.contextMenu) {
            editor.addMenuGroup('footnoteGroup');
            editor.addMenuItem('footnoteItem', {
                label: local_lang.context_edit,
                //icon: iconPath,
                command: 'footnoteDialog',
                group: 'footnoteGroup'
            });
            
            editor.contextMenu.addListener(function(element){
                if (element) {
                    //element = element.getAscendant('span', true);
                    element = getContainer(element);
                }
                if (element && !element.isReadOnly() && !element.data('cke-realelement')) 
                    return {
                        footnoteItem: CKEDITOR.TRISTATE_OFF
                    };
                // Return nothing if the conditions are not met.
                return null;
            });
            editor.addMenuItem('removeFootnoteItem', {
                label: local_lang.context_delete,
                //icon: iconPath,
                command: 'removeFootnote',
                group: 'footnoteGroup'
            });
            
            editor.contextMenu.addListener(function(element){
                // http://docs.cksource.com/ckeditor_api/symbols/CKEDITOR.dom.node.html#getAscendant
                if (element) {
                    //element = element.getAscendant('span', true);
                    element = getContainer(element);
                }
                // Return a context menu object in an enabled, but not active state.
                // http://docs.cksource.com/ckeditor_api/symbols/CKEDITOR.html#.TRISTATE_OFF
                if (element && !element.isReadOnly() && !element.data('cke-realelement')) 
                    return {
                        removeFootnoteItem: CKEDITOR.TRISTATE_OFF
                    
                    };
                // Return nothing if the conditions are not met.
                return null;
            });
        }
        CKEDITOR.dialog.add('footnoteDialog', function(editor){
            return {
                title: local_lang.dialog_title,
                minWidth: 600,
                minHeight: 370,
                contents: [{
                    id: 'tab1',
                    label: local_lang.dialog_title,
                    elements: [{
                        type: 'textarea',
                        id: 'footnote-text',
                        label: local_lang.dialog_note_text,
                        //validate: CKEDITOR.dialog.validate.notEmpty(local_lang.dialog_note_text_empty_error),
                        
                        setup: function(element){
                            if (element.getAttribute("data-note")) {
                                this.setValue(element.getAttribute("data-note").replace(/&quot;/igm, '"')
                                			  .replace(/&gt;/igm, '>').replace(/&lt;/igm, '<'));
                            }
                            //this.setValue(element.getHtml());
                            x = this.getInputElement().getAttribute('id');
                            CKEDITOR.replace(x, {
                                'skin': 'v2',
                                'language': 'fr',
                                'contentsCss': '../../../../site-media/css/tinyMCE_transcripts.css',
                                'bodyClass': 'cked-content',
                                'extraPlugins': 'overline,transcription,correction,illeg',
                                'toolbar': 'Transcription',
                                'toolbar_Transcription':  [
//                                    ['Bold','Italic','Underline','Superscript','Source'],
//                                    ['Image','SpecialChar','-','Link','Unlink','Anchor'],
									['SelectAll', 'Cut','Copy','Paste','PasteText'],
                                    ['Italic','Underline','Overline','Superscript','Source'],
                                    ['SpecialChar','-','Link','Unlink'],
                                    '/',
                                    ['Added', 'Suppressed'],['Supplied','Unclear','Illeg','Correction']
                                    ],
    });
    ckeditor_instance_id=this.getInputElement().getAttribute('id');
                        },
                        commit: function(element){
                            //element.setAttribute( "data-sic", this.getValue() );
                            //x = this.getInputElement().getAttribute('id');
                            var body = CKEDITOR.instances[x].getData();
                            element.setText(' ');
                            body=body.replace(/"/igm,"&quot;");
                            element.setAttribute("data-note", body.replace(/</igm,"&lt;").replace(/>/igm,"&gt;"));
                            // strips the tags and display the text in a popup
                            element.setAttribute("title", $('<div>' + body + '</div>').text().trim().replace(/[\n\r]/g, ''));
                            if (CKEDITOR.instances[ckeditor_instance_id]) CKEDITOR.instances[ckeditor_instance_id].destroy();
                        }
                    }, {
                        type: 'select',
                        id: 'place',
                        label: local_lang.location_label,
                        items:  local_lang.location_select,
                        
                        //validate : CKEDITOR.dialog.validate.notEmpty( "Correction field cannot be empty" )
                        
                        setup: function(element){
                            this.setValue(element.getAttribute("class"));
                        },
                        commit: function(element){
                            var className = this.getValue();
                            element.setAttribute("class", className);
                        }
                    }]
                }],
                // This method is invoked once a dialog window is loaded. 
                onShow: function(){
                    var sel = editor.getSelection(), element = sel.getStartElement();
                    selected_text = sel.getSelectedText();
                    
                    if (element) 
                        //element = element.getAscendant('span', true);
                        element = getContainer(element);
                    
                    if (!element || element.getName() != 'span' || element.data('cke-realelement')) {
                        element = editor.document.createElement('span');
                        element.setText(selected_text);
                        this.insertMode = true;
                    }
                    else 
                        this.insertMode = false;
                    
                    this.element = element;
                    //element.setAttribute('class', 'sic');
                    
                    //var textarea = this.getContentElement('tab1', 'doc_notes').getInputElement()
                    //var textarea_id=textarea.getId();
                    //CKEDITOR.replace(textarea_id, {"filebrowserWindowWidth": 940, "bodyClass": "cked-content", "language": "fr", "filebrowserBrowseUrl": "/ckeditor/browse/", "filebrowserUploadUrl": "/ckeditor/upload/", "toolbar_Transcription": [["Save", "-"], ["SelectAll", "Cut", "Copy", "Paste", "PasteText", "PasteFromWord", "-", "Undo", "Redo", "-", "RemoveFormat", "Source"], "/", ["Bold", "Italic", "Underline", "Superscript", "-", "JustifyLeft", "JustifyCenter", "JustifyRight"], ["Image", "HorizontalRule", "Table", "SpecialChar", "-", "Link", "Unlink", "Anchor"], "/", ["Styles", "Format"], "/", ["Added", "Suppressed", "Notes"], ["Supplied", "Unclear", "Illeg", "Correction"]], "extraPlugins": "transcription,correction,notes,illeg", "height": 200, "width": 850, "removePlugins": "flash,iframe,bidi", "skin": "v2", "filebrowserWindowHeight": 747, "toolbar": "Transcription"});
                    this.setupContent(this.element);

                },
                onOk: function(){
                    var dialog = this, note = this.element;
                    
                    if (this.insertMode) 
                        editor.insertElement(note);
                    
                    this.commitContent(note);
                },
                onCancel: function(){
                    if (CKEDITOR.instances[ckeditor_instance_id]) CKEDITOR.instances[ckeditor_instance_id].destroy();
                }
            };
        });
        {
            function getContainer(element){
                var elements = (element) ? element.getParents(true) : [];
                
                for (var i in elements) {
                    var el = elements[i];
                    if ((el.getAttribute('class') == 'note-editorial') || (el.getAttribute('class') == 'note-document')) {
                        return el;
                        //break;
                    }
                }
                return null;
            }
        }
    }
});

