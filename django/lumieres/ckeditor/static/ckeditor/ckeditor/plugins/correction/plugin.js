/* Editorial Correction v 0.1
 * Editorial corrections to the text are recorded in @data-corr
 */

CKEDITOR.plugins.add('correction', {
    init: function(editor){
        //var iconPath = this.path + 'images/icon.png';
        var cur_lang = editor.config.language || CKEDITOR.lang.detect(CKEDITOR.config.defaultLanguage);
        var transcription_strings = {
            en: {
                label: "[Make Editorial Correction]",
                context_edit: 'Edit Editorial Correction',
                context_delete: 'Delete Editorial Correction',
                dialog_title: 'Editorial Correction Properties',
                dialog_original: 'Original Text',
                dialog_corrected: 'Corrected Text',
                },

            fr: {
                label: "[Adaptation éditoriale]",
                context_edit: "Modifier les adaptations éditoriales",
                context_delete: "Supprimer les adaptations éditoriales",
                dialog_title: "Adaptations éditoriales",
                dialog_original: 'Texte original',
                dialog_corrected: 'Texte adapté',
                },

            };

        var local_lang = transcription_strings[cur_lang];
            
        
        editor.addCommand('correctionDialog', new CKEDITOR.dialogCommand('correctionDialog'));
        
        editor.ui.addButton('Correction', {
            label: local_lang.label,
            command: 'correctionDialog',
                //icon: iconPath,
            className: "x-cke_label_button"
        });
        editor.addCommand('removeCorrection', {
            exec: function (editor) {
                var el = getContainer(editor.getSelection().getStartElement())
                	, correction = el.getAttribute('data-corr')
                	, style = new CKEDITOR.style({
                		element	: 'span',
        				"attributes": { 'class': 'sic', 'data-corr': correction, 'title': correction }                    		
                	});
            	style.remove(editor.document);
            }
        });
        if (editor.contextMenu) {
            editor.addMenuGroup('correctionGroup');
            editor.addMenuItem('correctionItem', {
                label: local_lang.context_edit,
                //icon: iconPath,
                command: 'correctionDialog',
                group: 'correctionGroup'
            });
            
            editor.contextMenu.addListener(function(element){
                if (element) {
                    //element = element.getAscendant('span', true);
                    element=getContainer(element);
                    }
                if (element && !element.isReadOnly() && !element.data('cke-realelement')) 
                    return {
                        correctionItem: CKEDITOR.TRISTATE_OFF
                    };
                // Return nothing if the conditions are not met.
                return null;
            });
            editor.addMenuItem('removeCorrectionItem', {
                label: local_lang.context_delete,
                //icon: iconPath,
                command: 'removeCorrection',
                group: 'correctionGroup'
            });
            
            editor.contextMenu.addListener(function(element){
                // http://docs.cksource.com/ckeditor_api/symbols/CKEDITOR.dom.node.html#getAscendant
                if (element) {
                    //element = element.getAscendant('span', true);
                    element=getContainer(element);
                    }
                // Return a context menu object in an enabled, but not active state.
                // http://docs.cksource.com/ckeditor_api/symbols/CKEDITOR.html#.TRISTATE_OFF
                if (element && !element.isReadOnly() && !element.data('cke-realelement')) 
                    return {
                        removeCorrectionItem: CKEDITOR.TRISTATE_OFF
                    
                    };
                // Return nothing if the conditions are not met.
                return null;
            });
        }
        CKEDITOR.dialog.add('correctionDialog', function(editor){
            return {
                title: local_lang.dialog_title,
                minWidth: 500,
                minHeight: 200,
                contents: [{
                    id: 'tab1',
                    label: 'Correction Properties',
                    elements: [{
                        type: 'html',
                        html: '<label class="cke_dialog_ui_labeled_label">' + local_lang.dialog_original 
                        	  + ':</label><div id="sic"></div>',
                        
                        setup: function(){
                        	var wrapper = this.getElement().getDocument().getById('sic')
                        		, selection = editor.getSelection() 
                        		, ranges;
                        	selection.lock();
                        	ranges = selection.getRanges();
                            wrapper.setHtml('');
                            ranges.forEach(function (range) {
                            	wrapper.append(range.cloneContents());
                            });
                            selection.unlock(true);
                        }
                    }, {
                        type: 'text',
                        id: 'correction',
                        label: local_lang.dialog_corrected,

                        setup: function(correction){
                            this.setValue(correction);
                        }
                    }]
                }],
                // This method is invoked once a dialog window is loaded. 
                onShow: function(){
                    var element = editor.getSelection().getStartElement();

                    if (element) 
                        element = getContainer(element);
                    
                    this.element = element;
                    this.insertMode = ! element || (element.getName() != 'span') || element.data('cke-realelement');
                    
                    // Invoke the setup functions of the element.
                    this.setupContent(this.insertMode ? '' : element.getAttribute('data-corr'));
                },
                onOk: function(){
                	var correction = this.getContentElement('tab1', 'correction').getValue();
                    if (this.insertMode) {
                		var style = new CKEDITOR.style({
                			element	: 'span',
                			"attributes": { 
                				'class': 'sic', 
                				'title': correction, 
                				'data-corr': correction 
                			}                    		
                		});
              			style.apply(editor.document);
                    } else {
                    	this.element.setAttribute('data-corr', correction);
                    	this.element.setAttribute('title', correction);
                    }
                    
                    this.commitContent();
                }
            };
        });
        {
            function getContainer(element) {
                // iterate over all the ancestors find span@class='sic'
                var elements = (element) ? element.getParents(true) : [];
                for (var i in elements) {
                    var el = elements[i];
                    if (el.getAttribute('class') == 'sic') {
                        return el;
                        //break;
                    }
                }
                return null;
            }
        }
    }
});
