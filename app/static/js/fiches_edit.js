/*****
 * 
 *    Copyright (C) 2010-2012 Université de Lausanne, RISET
 *    < http://www.unil.ch/riset/ >
 *
 *    This file is part of Lumières.Lausanne.
 *    Lumières.Lausanne is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    Lumières.Lausanne is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *    This copyright notice MUST APPEAR in all copies of the file.                      
 *
 ****/
/**
 * Code utilisé pour l'édition des fiches'
 */

var DATE_FORMAT = DATE_FORMAT || 'dmy',
	DATE_SEPARATOR = DATE_SEPARATOR || '-';

var fiches_edit = $.extend({}, fiches_edit, {
	has_changed: false
	
	, encode_transcription_pos: function() {
		if ( ! CKEDITOR || ! CKEDITOR.instances["id_text"] ) { return ""; }
		CKEDITOR.instances.id_text.focus();
		var sel = CKEDITOR.instances.id_text.getSelection().getRanges();
		if ( ! sel || sel.length < 1 ) { return ""; }
		var element = sel[0].startContainer
			, cssSel = "" + sel[0].startOffset;
		while ( element ) {
			cssSel = element.getIndex() + "," + cssSel;
			element = element.getParent();
		}
		return cssSel;
	}

	//--
	, submit_form: function(e, continueEditing) {
		if (e && e.type == "click") { e.preventDefault(); }
		
		var editForm = $(".content form.edit-form");
		if (continueEditing === true) {
			var continueField = editForm.find("input[name=__continue]")
				, positionField = editForm.find("input[name=__position]");
			if (!continueField.length) {
				editForm.prepend($("<input>",{'type': "hidden", 'name': "__continue", 'value': "on"}));
			} else {
				continueField.val("on");
			}
			if (!positionField.length) {
				editForm.prepend($("<input>",{'type': "hidden", 'name': "__position", 'value': this.encode_transcription_pos()}));
			} else {
				positionField.val(this.encode_transcription_pos());
			}
		} else {
			editForm.find("input[name=__continue], input[name=__position]").remove();
		}
		
		var onsubmit_callback = editForm.data('onsubmit');
		if (typeof onsubmit_callback == 'function') { onsubmit_callback.apply(editForm); }
		
		return editForm.submit();
	}
	
	// 
	, _recommandationCheckCallback : null
	, registerRecommandationCallback: function(callback) {
		fiches_edit._recommandationCheckCallback = callback;
	}
	// If there is a recommandation callback defined for this form,
	// call it and return the result. Otherwise return true 
	, checkRecommandation: function() {
		if (typeof fiches_edit._recommandationCheckCallback == 'function') {
			return fiches_edit._recommandationCheckCallback();
		} else {
			return true;
		}
		return true;
	}
	
	//--
	, updateVarDateField: function(e) {
		var	container   = $(this),
			date_node   = container.siblings("[name="+container.attr("rel")+"]"),
			format_node = $("[name="+date_node.attr("name")+"_f]"),
			all_checked = $(":checked", container).length === 3,
			date_list   = [], 
			format_list = [],
			empty_date  = false,
			d, c, v, v_fld, format;
		
		// Read the date according to the order given by DATE_FORMAT
		// Determine wich date fields are populated
		for (d in DATE_FORMAT) {
			c = DATE_FORMAT[d];
			v_fld = container.find("input."+c).eq(0);
			v = v_fld.val();
			if ( v.length > 0 ) {
				date_list.push(v);
				format = '%' + ((c === 'y') ? 'Y' : c);
				if ( !all_checked && $('.bracket_' + c, container).prop('checked') ) {
					format = "[" + format + "]";
				}
				format_list.push(format);
			} else {
				if (c === 'y') { 
					empty_date = true; 
					break;
				}
				date_list.push("01");
			}
		}
		
		// If there is no year value, the date is concidered empty
		if (! empty_date) {
			date_node.val(date_list.join(DATE_SEPARATOR));
			format = format_list.join(DATE_SEPARATOR);
			if ( all_checked ) {
				format = "[" + format + "]";
			}
			format_node.val(format);	
		} else {
			date_node.val("");
			format_node.val("");
		}
	}
	
	//--
	, invalidate: function(obj) {
		this.has_changed = true;
	}
	
	//--
	, cancelEdition: function(display_url) {
		if (typeof(display_url)=='undefined') return false;
		var do_cancel = (this.has_changed) ? 
				confirm("Les dernières modifications n'ont pas été enregistrées. Si vous continuez elles seront perdues.\nContinuer ?") :
				true;
		if (do_cancel) { document.location = display_url; }
		return false;
	} 
	
	
	//--
	, addRemoveFormBut: function(form_elem, but_title, callback, buttonText) {
        $(":checkbox[name$=DELETE]", form_elem).each(function(){
            var but = $('<button>',{
				    text:  (typeof buttonText == 'string') ? buttonText : (but_title || "Supprimer"),
                    style: (buttonText) ? "font-size: 11px;" : "font-size: 9px;",
                    type: 'button',
                    title: but_title || "Supprimer",
                    click: function(){ 
					   $(this).next().click(); 
					   if(typeof callback=='function') { callback(); };
					   return false;
					}
                });
            $(this).before(but);
            if ($.fn.button) { but.button({text: (!!buttonText), icons: { primary: "ui-icon-close" }}) }
        })
        .hide();
    }
	
	//--
	, init_vardateformat: function(format_node){		
        // Initialize main variables
        format_node = $(format_node);
		if (format_node.data('vardateformat') == 'inited') { return; }
		
                // Normalized format
        var format = String(format_node.val()).toLowerCase().replace(/[^ymd]+/ig,''),
            date_node = $("input[name='" + format_node.attr("name").slice(0,-2) + "']"),
            output_val = [],
            output_node = $('<div class="vardate-multifield-container" style="display:inline;"/>');
        
        // Basic validity checks
        if ( (typeof(date_node) === 'undefined') || (format==='undefined') ) { return; }

        // Initialize other variables
        var date_val = date_node.val(),
            date_list = (date_val) ? date_val.split(DATE_SEPARATOR) : ["","",""],
            formatted_date_list = ["","",""],
            d,c;
        
        // Apply initial formatting to the date
        for (d in DATE_FORMAT) {
            c = DATE_FORMAT[d];
            if (format.indexOf(c) !== -1 ) {
                formatted_date_list[d] = date_list[d];
            }
        }
        
        // Create date widget
        var output_node = $('<div class="vardate-multifield-container" rel="'+date_node.attr("name")+'" style="display:inline;"/>');
        for (d in DATE_FORMAT) {
            c = DATE_FORMAT[d];
            var c_ph = (c=='d') ? "jj" : ((c=='m') ? "mm" : ((c=='y') ? "aaaa" : "") );
            output_node.append(
                $('<input type="text" class="' + c + '" placeholder="' + c_ph + '" value="'+formatted_date_list[d]+'" size="' + ((c==='y')?'4':'2') + '"/>')
            );
        }
        
        date_node.after(output_node).hide();
		format_node.data('vardateformat', 'inited');
    }
	
	//--
	/**
	 * Call $.fn.button on the elements with common parameters for adding
	 * new empty fields
	 * @param {Object} obj
	 */
	, applyAddFieldButtonUI: function(obj, originalText) {
		if ($.fn.button) {
			$(obj).each(function(i, n){
				var $n = $(n);
				if(!originalText){ $n.text("Plus de champs"); };
				$n.css("fontSize", "9px").button({
					icons: {
						primary: "ui-icon-squaresmall-plus"
					}
				});
			});
		}
	}
   
});

var formset_utils = $.extend({}, formset_utils, {
	
	// In the new formset's form, replace `curIdx' with `newIdx' in any nodes 
	// having `curIdx' in the 'name' attribute or having a 'rel' attribute
	update_newform_idx: function($newForm, curIdx, newIdx) {
		$newForm.find("[name*='-"+curIdx+"-'], [rel]").each(function(){
			var $t = $(this), newid, newname, newrel;
			if ($t.attr('id')) {
				newid = $t.attr('id').replace('-' + curIdx + '-', '-' + newIdx + '-');
				$t.attr("id", newid).val("");
			}
			
			if ($t.attr('name')) {
				newname = $t.attr('name').replace('-'+curIdx+'-', '-'+newIdx+'-');
				$t.attr("name",newname);
			}
			
			if ($t.attr('rel')) {
				newrel = $t.attr('rel').replace('-'+curIdx+'-', '-'+newIdx+'-');
				$t.attr("rel",newrel);
				$t.find("input").val("");
			}
		});
	}
	
});


$(document).ready(function(){
		
	$(".vardateformat").each(function(){
		
		// Initialize main variables
		var format_node = $(this);
		if (format_node.data('vardateformat') == 'inited') { return; }
		
				// Normalized format
		var	format = String(format_node.val()).toLowerCase(),
			date_node = $("input[name='" + format_node.attr("name").slice(0,-2) + "']"),
			output_val = [];
		
		// Basic validity checks
		if ( (typeof(date_node) === 'undefined') || (format==='undefined') ) { return; }

		// Initialize other variables
		var date_val = date_node.val(),
			date_list = (date_val) ? date_val.split(DATE_SEPARATOR) : ["","",""],
			formatted_date_list = ["","",""],
            brackets = [],
            all_brackets = (format === '[%d-%m-%y]'),
            d,c;

		// Apply initial formatting to the date
		for (d in DATE_FORMAT) {
			c = DATE_FORMAT[d];
			if (format.indexOf(c) !== -1 ) {
				formatted_date_list[d] = date_list[d];
			}
            brackets[d] = all_brackets || format.indexOf('[%' + c + ']') !== -1;
		}
		
		// Create date widget
		var output_node = $('<div class="vardate-multifield-container" rel="' + date_node.attr("name") 
							+ '" style="display:inline;"/>');
		for ( d in DATE_FORMAT ) {
			c = DATE_FORMAT[d];
			var c_ph = "jj";
			switch (c) {
				case 'm': 
					c_ph = 'mm'; 
					break;
				case 'y': 
					c_ph = 'aaaa'; 
					break;
			}
			output_node.append('<input type="text" class="' + c + '" placeholder="' + c_ph + '" value="'
							   + formatted_date_list[d] + '" size="' + ((c === 'y') ? '4' : '2') 
							   + '" maxlength="' + ((c === 'y') ? '4' : '2') + '"/>');
		}
		output_node.append('<br/><label>entre crochets</label>');
		for ( d in DATE_FORMAT ) {
			c = DATE_FORMAT[d];
			output_node.append('<input type="checkbox" class="bracket_' + c + '" ' 
							   + ((brackets[d]) ? 'checked="1" ': '') + '/>');
		}
		
		date_node.after(output_node).hide();
		format_node.data('vardateformat', 'inited');
	});
	
	$("input[id][name], select[id][name], textarea[id][name]").change(function(){fiches_edit.invalidate(this);});
	if ( window.CKEDITOR ) {
		CKEDITOR.on('currentInstance', function(){fiches_edit.invalidate(this);});
	}
	
	$("form.edit-form").submit(function(){
		$(".vardate-multifield-container").each(fiches_edit.updateVarDateField);
		return fiches_edit.checkRecommandation();
	});
	
	$(":checkbox[name$=DELETE]")
		.addClass("formset_delete_but")	
		.live("click", function(){$(this).parents(".form-instance").fadeOut('fast'); });
	  
	// ========== Tooltip ==========
	if ($.fn.simpletooltip) {
		$(".tooltiplink a").each(function(){
			var $a = $(this),
			    help_div = $("#" + $a.attr('href').substr(1)).eq(0);
			if (help_div.length) {
				help_div.hide().addClass("tooltip_content");
			    $a.simpletooltip({ showEffect: "fadeIn", hideEffect: "fadeOut", showDelay: 0.8, 'click': true, 'clickAndHover': true, 'hideOnClick': true });
			} else {
				$a.hide();
			}
		});
	}
});

window.fiches_edit = fiches_edit;

