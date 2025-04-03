/* Marginal Notes v 0.2
 * This button allows editors to enter marginal notes into the transcription.
 */

CKEDITOR.plugins.add('notes', {

    init: function(editor){
        var ckeditor_instance_id='';
        var cur_lang = editor.config.language || CKEDITOR.lang.detect(CKEDITOR.config.defaultLanguage);
        var transcription_strings = {
            en: {
                label: "[Marginal Note]",
                title: {
                    'mleft': 'This text is placed in the right margin',
                    'mright': 'This text is placed in the right margin',
                    'mbottom': 'This text is placed in the bottom margin',
                    'mother': ''
                },
                context_edit: 'Edit Marginal Note',
                context_delete: 'Delete Marginal Note',
                dialog_title: 'Marginal Note Properties',
                dialog_note_text: 'Note Text',
                dialog_note_text_empty_error: "Description cannot be empty",
                location_label: "Location of note",
                location_select: [['Left Margin', 'mleft'], ['Right Margin', 'mright']],
            },
            fr: {
                label: "[Note Marginale]",
                title: {
                    'mleft': 'Ce texte est situé dans la marge gauche',
                    'mright': 'Ce texte est situé dans la marge droite',
                    'mbottom': 'Ce texte est situé dans la marge inférieure',
                    'mother': ''
                },
                context_edit: 'Modifier note marginale',
                context_delete: 'Supprimer la note marginale',
                dialog_title: 'Propriétés Note Marginale',
                dialog_note_text: 'Texte de la Note',
                dialog_note_text_empty_error: "Notez le texte ne peut pas être vide",
                location_label: 'Emplacement de la Note',
                location_select: [['la marge gauche', 'mleft'], ['la marge droite', 'mright']],
            
            }
        };
        var local_lang = transcription_strings[cur_lang];
        
        //var iconPath = this.path + 'images/icon.png';
        
        editor.addCommand('notesDialog', new CKEDITOR.dialogCommand('notesDialog'));
        
        editor.ui.addButton('Notes', {
            label: local_lang.label,
            command: 'notesDialog',
            //icon: iconPath,
            className: "x-cke_label_button"
        });
        editor.addCommand('removeNotes', {
            exec: function(editor){
                var sel = editor.getSelection()
                	, element = sel.getStartElement()
                	, element$;
                element = getContainer(element);
                element$ = $(element.$);
                element$.replaceWith(element$.text());
            }
        });
        if (editor.contextMenu) {
            editor.addMenuGroup('notesGroup');
            editor.addMenuItem('notesItem', {
                label: local_lang.context_edit,
                //icon: iconPath,
                command: 'notesDialog',
                group: 'notesGroup'
            });
            
            editor.contextMenu.addListener(function(element){
                if (element) {
                    //element = element.getAscendant('span', true);
                    element = getContainer(element);
                }
                if (element && !element.isReadOnly() && !element.data('cke-realelement')) 
                    return {
                        notesItem: CKEDITOR.TRISTATE_OFF
                    };
                // Return nothing if the conditions are not met.
                return null;
            });
            editor.addMenuItem('removeNotesItem', {
                label: local_lang.context_delete,
                //icon: iconPath,
                command: 'removeNotes',
                group: 'notesGroup'
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
                        removeNotesItem: CKEDITOR.TRISTATE_OFF
                    
                    };
                // Return nothing if the conditions are not met.
                return null;
            });
        }
        CKEDITOR.dialog.add('notesDialog', function(editor){
            return {
                title: local_lang.dialog_title,
                minWidth: 600,
                minHeight: 370,
                contents: [{
                    id: 'tab1',
                    label: local_lang.dialog_title,
                    elements: [{
                        type: 'textarea',
                        id: 'doc_notes',
                        label: local_lang.dialog_note_text,
                        //validate: CKEDITOR.dialog.validate.notEmpty(local_lang.dialog_note_text_empty_error),
                        
                        setup: function(element){
                            //this.setValue( element.getAttribute( "data-sic" ) );
                            this.setValue(element.getHtml());
                            x = this.getInputElement().getAttribute('id');
                            CKEDITOR.replace(x, {
                                'skin': 'v2',
                                'language': 'fr',
                                'contentsCss': '../../../../site-media/css/tinyMCE_transcripts.css',
                                'bodyClass': 'cked-content',
                                'extraPlugins': 'overline,transcription,correction,illeg',
                                'toolbar': 'Transcription',
                                'toolbar_Transcription':  [
       									['SelectAll', 'Cut','Copy','Paste','PasteText'],
                                        ['Italic','Underline','Overline','Superscript','Source'],
                                        ['SpecialChar','-','Link','Unlink'],
                                        '/',
                                        ['Added', 'Suppressed'],['Supplied','Unclear','Illeg','Correction']
                                    ],
                                'enterMode' : CKEDITOR.ENTER_BR,
                                'shiftEnterMode': CKEDITOR.ENTER_BR,
    });
        ckeditor_instance_id=this.getInputElement().getAttribute('id');
                        },
                        commit: function(element){
                            //element.setAttribute( "data-sic", this.getValue() );
                            //x = this.getInputElement().getAttribute('id');
                            var body = CKEDITOR.instances[x].getData();
                            element.setHtml(body);
                            if (CKEDITOR.instances[ckeditor_instance_id]) CKEDITOR.instances[ckeditor_instance_id].destroy();
                        }
                    }, {
                        type: 'select',
                        id: 'place',
                        label: local_lang.location_label,
                        items:  local_lang.location_select,
                        
                        //validate : CKEDITOR.dialog.validate.notEmpty( "Correction field cannot be empty" )
                        
                        setup: function(element){
                            this.setValue(element.getAttribute("data-place"));
                        },
                        commit: function(element){
                            var className = this.getValue();
                            element.setAttribute("data-place", className);
                            element.setAttribute("class", className);
                            element.setAttribute("title", local_lang.title[className]);
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
                // iterate over all the ancestors find span@class='sic'
                var elements = (element) ? element.getParents(true) : [];
				
                for (var i in elements) {
                    var el = elements[i];
                    if ((el.getAttribute('class') == 'mleft') || (el.getAttribute('class') == 'mright') || (el.getAttribute('class') == 'mbottom') || (el.getAttribute('class') == 'mother')) {
                        return el;
                        // break;
                    }
                }
                return null;
            }
        }
    }
});

