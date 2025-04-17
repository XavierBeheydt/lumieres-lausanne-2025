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
var staticlist_widget = {
    version: '1'
  , appendDeleteButton: function(obj) { 
  		var but = $('<button>',{
				'class': "staticlist-delete-item",
				'type': "button",
				click: function() { $(this).parent().fadeOut('fast', function(){$(this).remove()}); return false },
				text: "Supprimer"
		});
		$(obj).prepend(but);
		but.button({text: false, icons: { primary: "ui-icon-close" }});
	}
      , addToList : function(o, name) {
          	var sl_container = $(o).parents(".staticlist_container"),
    		    sl_selector  = sl_container.find("select.staticlist_helper_select"),
    		    sl_valuelist = sl_container.find("div.staticlist_values"),
			    value = sl_selector.val();
				if (!value) { return; }
			var label = sl_selector.find(":selected").text(),
    		    template = staticlist_widget.templates[name],
			    value_entry = $(template.replace('%(label)s' , label)
    	        					.replace('%(name)s'  , name)
    	        					.replace('%(value)s' , value)
    	    );
			sl_valuelist.append(value_entry);
			sl_selector.val("");
			staticlist_widget.appendDeleteButton(value_entry);
      }
};

var dynamiclist_widget = {
	    version: '1'
      , class_prefix: 'dynamiclist'
	  //, appendDeleteButton: function(obj) { $(obj).append('<button class="delete" onclick="$(this).parent().fadeOut(\'fast\', function(){$(this).remove()}); return false;"><span>Supprimer</span></button>'); }
	  , appendDeleteButton: function(obj) { 
	  		var but = $('<button>',{
					'class': "dynamiclist-delete-item",
					'type': "button",
					click: function() { $(this).parent().fadeOut('fast', function(){$(this).remove()}); return false },
					text: "Supprimer"
			});
			$(obj).prepend(but);
			but.button({text: false, icons: { primary: "ui-icon-close" }});
		}
	  , addToList : function(o, name) {
				var container = $(o).parents("."+this.class_prefix+"_container"),
					label = container.find("."+this.class_prefix+"_helper_input").val(),
				    value = container.find(".helper_input_value").val();
				if (value && label) {
					var template = this.templates[name],
						value_entry = $(template.replace('%(label)s' , label)
							.replace('%(name)s'  , name)
							.replace('%(value)s' , value)
						);
					// Add new entry to the value list
		          	container.find("div."+this.class_prefix+"_values").append(value_entry);
					this.appendDeleteButton(value_entry);

					// Clear current source input values
					container.find("."+this.class_prefix+"_helper_input").val("").end()
							 .find("."+this.class_prefix+"_helper_input").val("").end()
							 .find(".dynamiclist_helper_addbut").attr("disabled", "disabled")
					;
				}
	      	}
	};

