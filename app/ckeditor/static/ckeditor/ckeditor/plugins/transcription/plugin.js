/*
* Plugin for adding Transcription specific buttons
* Only three component added to illustrate the way things could be done
* 
* The use of the localization makes the code a bit more long and less readable
* It was done mainly to explore the possibilities of the CKEditor API
*/

CKEDITOR.plugins.add( 'transcription',
{
    requires : [ 'styles', 'button' ],

    init : function( editor )
    {

        // All buttons use the same code to register. So, to avoid
        // duplications, let's use this tool function.
        var addButtonCommand = function( buttonName, buttonLabel, buttonClassName, commandName, styleDefiniton, variablesValues ) {
            
            var style = new CKEDITOR.style( styleDefiniton, variablesValues );

            editor.attachStyleStateChange( style, function( state ){
                    editor.getCommand( commandName ).setState( state );
            });

            editor.addCommand( commandName, new CKEDITOR.styleCommand( style ) );
            
            
            editor.ui.addButton( buttonName, {
                label : buttonLabel,
                command : commandName,
                className: buttonClassName
            });
        };
        
        var addMarginButton = function( buttonName, buttonLabel, buttonClassName, commandName, styleDefiniton, variablesValues ) {
            
            var style = new CKEDITOR.style( styleDefiniton, variablesValues );

            editor.attachStyleStateChange( style, function( state ){
                    editor.getCommand( commandName ).setState( state );
            });

            editor.addCommand( commandName, new CKEDITOR.styleCommand( style ) );
            
            
            editor.ui.addButton( buttonName, {
                label : buttonLabel,
                command : commandName,
                className: buttonClassName
            });
        };

        // Localization strings. Could be ommitted, used here for testing purpose.
        var config = editor.config,
            lang = editor.lang,
            cur_lang = editor.config.language || CKEDITOR.lang.detect(CKEDITOR.config.defaultLanguage),
            
            transcription_strings = {
                en: {
                    added: "\\Added/",
                    added_title: "This text has been added by the author",
                    suppressed: "Deleted",
                    suppressed_title: "Deleted",
                    supplied: "[Supplied]",
                    supplied_title: "This text has been supplied by the author",
                    unclear: "[Unclear]",
                    unclear_title: "The editor is uncertain of this reading",
                    illeg: "[Illeg]",
                    illeg_title: 'illegible',
                    marginright: "[Margin Right]",
                    marginright_title: "This text is placed in the right margin",
                    marginleft: "[Margin Left]",
                    marginleft_title: "This text is placed in the left margin"
                },
                
                fr: {
                    added: "\\Ajout/",
                    added_title: "Ce texte a été rajouté par l'auteur",
                    suppressed: "Biffé",
                    suppressed_title: "Biffé",
                    supplied: "[Complété]",
                    supplied_title: "Ce texte a été complété par l'éditeur",
                    unclear: "[Lecture incertaine]",
                    unclear_title: "L'éditeur n'est pas sûr de sa lecture",
                    illeg: "[Illisible]",
                    illeg_title: 'illisible',
                    marginright: "[Marge droite]",
                    marginright_title: "Ce texte est situé dans la marge droite",
                    marginleft: "[Marge gauche]",
                    marginleft_title: "Ce texte est situé dans la marge gauche"

                }
            },
            
            local_lang = transcription_strings[cur_lang];
        	
        
        
        addButtonCommand( 'Added',
                          local_lang.added,
                          "x-cke_label_button",
                          'added',
                          config.transcriptionStyles_added,
                          {'title': local_lang.added_title }
                          );
        
        addButtonCommand( 'Suppressed',
                          local_lang.suppressed,
                          "x-cke_label_button x-trans-suppressed_button",
                          'suppressed',
                          config.transcriptionStyles_suppressed,
                          {'title': local_lang.suppressed_title }
                          );
        
        addButtonCommand( 'Supplied',
                          local_lang.supplied,
                          "x-cke_label_button",
                          'supplied',
                          config.transcriptionStyles_supplied,
                          {'title': local_lang.supplied_title }
                          );

        addButtonCommand( 'Unclear',
                          local_lang.unclear,
                          "x-cke_label_button",
                          'unclear',
                          config.transcriptionStyles_unclear,
                          {'title': local_lang.unclear_title }
                          );
        

    }
});



/**
 * The style definition to be used to apply a transcription specific style in the text.
 * @type Object
 * @example
 * config.transcriptionStyles_added = { element : 'ins', overrides : 'strong' };
 * @example
 * config.transcriptionStyles_supplied = { element : 'span', attributes : {'class': 'supplied'} };
 */

CKEDITOR.config.transcriptionStyles_added = { element : 'ins', attributes : {'title': "#(title)"} };

CKEDITOR.config.transcriptionStyles_suppressed = { element : 'del', attributes : {'title': "#(title)"} };

CKEDITOR.config.transcriptionStyles_supplied = { element : 'span', attributes : {'class': 'supplied', 'title': "#(title)"} };

CKEDITOR.config.transcriptionStyles_unclear = { element : 'span', attributes : {'class': 'unclear', 'title': "#(title)"} };

CKEDITOR.config.transcriptionStyles_illeg = { element : 'span', attributes : {'class': 'illeg', 'title': "#(title)"} };

CKEDITOR.config.transcriptionStyles_marginright = { element : 'span', attributes : {'class': 'mright', 'title': "#(title)"}};

CKEDITOR.config.transcriptionStyles_marginleft = { element : 'span', attributes : {'class': 'mleft', 'title': "#(title)"} };

CKEDITOR.config.shiftEnterMode = CKEDITOR.ENTER_BR

/*
 * MOVED TO PYTHON SETTINGS FILES 
CKEDITOR.config.specialChars = [ [ '&szlig;','Latin small letter sharp s' ], ['%', 'Percent Sign'],['\u2021', 'Double Dagger'],['\u2020', ' Dagger'],['\u222B', ' Integral'], [ '&pound;', 'Pound Sign' ], [ '&sect;', 'Section sign' ],['&para;', 'Paragraph Sign'],[ '&frac14;','Vulgar fraction one quarter' ], [ '&frac12;','Vulgar fraction one half' ], [ '&frac34;','Vulgar fraction three quarters' ] ];

CKEDITOR.stylesSet.add( 'default',[
{
    name:'Normal',
    element:'p',
    attributes: {'class': 'normal'}
},
{
    name: 'Verse',
    element: 'p',
    attributes: {
        'class': 'verse'
    }
}])
*/




