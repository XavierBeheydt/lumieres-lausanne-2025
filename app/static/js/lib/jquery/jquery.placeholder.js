/*
	jQuery Placeholder Plugin
	Author: Eymen Gunay
	Web: http://www.egunay.com/
	
	Modified by Julien Furrer <Julien.Furrer@unil.ch>
*/
(function( $ ){
    $.fn.__placeHolder = $.fn.__placeHolder || {};
    $.fn.__placeHolder.elems = $.fn.__placeHolder.elems || [];
    
    $.fn.placeHolder = function(options) {
		if (window.Modernizr && window.Modernizr.input && window.Modernizr.input.placeholder) {
			return this;
		}
        var settings = {
            'text' : 'Placeholder',
            'activeCss': {
				'color': '#000'
			},
            'placeholderCss': {
                'color': '#C6BDA8',
                'fontStyle': 'normal'
            }
        };
        if (typeof options == 'string') {
            if (options == 'elems') {
                return $.fn.__placeHolder.elems;
            }
            if (options == 'text') {
                return this.data('placeHolder.text');
            }
        }
        return this.each(function() {
            var eo = $(this);
            $.fn.__placeHolder.elems.push(eo);
            if ( options ) { 
                $.extend( true, settings, options );
            }
            eo.data('placeHolder.text', settings.text)
            for( var p in settings.placeholderCss) {
                settings.activeCss[p] = eo.css(p);
            }
            if (!eo.val()) {
                eo.val(settings.text);
                eo.css(settings.placeholderCss);
            }
            eo.unbind('focus');
            eo.bind('focus', function() {
                if(eo.val() == settings.text) {
                    eo.css(settings.activeCss);
                    eo.val("");
                }
            });
            eo.unbind('focusout');
            eo.bind('focusout', function() {
                $("#search_box img").css("display","none");
                if(eo.val() == "" || eo.val() == settings.text) {
                    eo.val(settings.text);
                    eo.css(settings.placeholderCss);
                }
            });
            
            eo.parents('form').eq(0).bind('submit', function(evt) { if(eo.val() == settings.text){ eo.val(""); } });
        });             
    
    };
})( jQuery );

/* ============================================================================
(function( $ ){
	$.fn.placeHolder = function(options) {
		var eo = this;
		var settings = {
			'text'		  : 'Placeholder',
			'placeholder' : '#AEAEAE',
			'active' 	  : '#000'
		};
		return this.each(function() {        
			if ( options ) { 
				$.extend( settings, options );
			}			
			if (!eo.val()) {
				eo.val(settings.text);
				eo.css("color", settings.placeholder);
			}
			eo.bind('focus', function() {
				if(eo.val() == settings.text) {
					eo.css("color", settings.active);
					eo.val("");	
				}
			});
			eo.bind('focusout', function() {
				$("#search_box img").css("display","none");
				if(eo.val() == "" || eo.val() == settings.text) {
					eo.val(settings.text);
					eo.css("color", settings.placeholder);
				}
			});
		});				
	
	};
})( jQuery );
============================================================================ */