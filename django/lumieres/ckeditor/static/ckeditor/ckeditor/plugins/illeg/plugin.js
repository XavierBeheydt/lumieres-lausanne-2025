/* Illegible Text v 0.2
 * This button allows the editor to record information about illegible
 * test. This data is currently recored as the content of the 
 * <span class="illeg"></span>. However, once the ultimate aim is to have
 * that information recorded in @data-illeg and to make <span class="illeg">
 * and uneditable placeholder in ckeditor.
 */

CKEDITOR.plugins.add('illeg', {
    init: function(editor){
        var cur_lang = editor.config.language || CKEDITOR.lang.detect(CKEDITOR.config.defaultLanguage);
        var transcription_strings = {
        en: {
            label: "[Illeg]",
            title: 'illegible',
            context_edit: 'Edit Illegible Description',
            context_delete: 'Delete Illegible',
            dialog_title: 'Illegible Text',
            dialog_description: 'Description of extent of illegible text',
            dialog_not_empty: "Description cannot be empty",
            },

        fr: {
            label: "[Illisible]",
            title: 'illisibles',
            context_edit: "Modifier le texte illisibles",
            context_delete: "Supprimer le texte illisibles",
            dialog_title: "Texte Illisible",
            dialog_description: "Description de l'étendue du texte illisible",
            dialog_not_empty: "Description ne peut pas être vide",
            }
        };

        var local_lang = transcription_strings[cur_lang];

        //var iconPath = this.path + 'images/icon.png';
        
        editor.addCommand('illegDialog', new CKEDITOR.dialogCommand('illegDialog'));
        editor.ui.addButton('Illeg', {
            label: local_lang.label,
            command: 'illegDialog',
            className: "x-cke_label_button"
        });
        editor.addCommand('removeIlleg', {
            exec: function (editor) {
                var sel = editor.getSelection(), element = sel.getStartElement();
                el = getContainer(element);
                el.remove();
            }
        });
        if (editor.contextMenu) {
            editor.addMenuGroup('illegGroup');
            editor.addMenuItem('illegItem', {
                label: local_lang.context_edit,
                //icon: iconPath,
                command: 'illegDialog',
                group: 'illegGroup'
            });
            
            editor.contextMenu.addListener(function(element){
                if (element) {
                    //element = element.getAscendant('span', true);
                    element=getContainer(element);
                    }
                if (element && !element.isReadOnly() && !element.data('cke-realelement')) 
                    return {
                        illegItem: CKEDITOR.TRISTATE_OFF
                    };
                // Return nothing if the conditions are not met.
                return null;
            });
            editor.addMenuItem('removeIllegItem', {
                label: local_lang.context_delete,
                //icon: iconPath,
                command: 'removeIlleg',
                group: 'illegGroup'
            });
            
            editor.contextMenu.addListener(function(element){
                if (element) {
                    element=getContainer(element);
                    }
                if (element && !element.isReadOnly() && !element.data('cke-realelement')) 
                    return {
                        removeIllegItem: CKEDITOR.TRISTATE_OFF
                    };
                return null;
            });
        }
        CKEDITOR.dialog.add('illegDialog', function(editor){
            return {
                title: local_lang.dialog_title,
                minWidth: 400,
                minHeight: 200,
                contents: [{
                    id: 'tab1',
                    label: local_lang.dialog_title,
                    elements: [{
                        type: 'text',
                        id: 'desc',
                        label: local_lang.dialog_description,
                        validate : CKEDITOR.dialog.validate.notEmpty( local_lang.dialog_not_empty ),
                        
                        setup: function(element){
                            this.setValue(element.getText());
                        },
                        commit: function(element){
                            element.setText(this.getValue());
                            // @data-illeg is not to be used until a way of creating uneditable text in ckeditor is possible
                            //element.setAttribute("data-illeg", this.getValue().replace(/"/g,"&quot;"));
                        }
                    }]
                }],
                // This method is invoked once a dialog window is loaded. 
                onShow: function(){
                    var sel = editor.getSelection(), element = sel.getStartElement();
                    selected_text = sel.getSelectedText();

                    if (element) 
                        //element = element.getAscendant('span', true);
                        element=getContainer(element);
                    
                    if (!element || element.getName() != 'span' || element.data('cke-realelement')) {
                        element = editor.document.createElement('span');
                        element.setText(selected_text);
                        this.insertMode = true;
                    }
                    else 
                        this.insertMode = false;
                    
                    this.element = element;
                    element.setAttribute('class', 'illeg');
                    element.setAttribute('title',local_lang.title);
                    
                    // Invoke the setup functions of the element.
                    this.setupContent(this.element);
                },
                onOk: function(){
                    var dialog = this, illeg = this.element;
                    
                    if (this.insertMode) 
                        editor.insertElement(illeg);
                    
                    this.commitContent(illeg);
                }
            };
        });
 /*      editor.on('contentDom', function() //when the pre-filled data in CKEditor is ready
            {
                x=CKEDITOR.dom.document
                alert();
                $('.illeg').each(function(){ alert('hi');});
                $('.illeg').bind('click',function() {
  alert('Handler for .change() called.');
});
            }); */

        {
            function getContainer(element) {
                // iterate over all the ancestors find span@class='sic'
                var elements = (element) ? element.getParents(true) : [];
				
                for (var i in elements) {
                    var el = elements[i];
                    if (el.getAttribute('class') == 'illeg') {
                        return el;
                        //break;
                    }
                }
                return null;
            }
        }
    }
});
