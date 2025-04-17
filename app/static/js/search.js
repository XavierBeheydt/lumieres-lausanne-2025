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
* Code Javascript pour la gestion des filtres de recherche.
* LLv3, ne s'applique plus que pour les recherches Biographiques
*/
var search_filter = search_filter || {
	  debug: true
	, filter_definitions: []
	, filter_applied: []
	, filter_implied: []
	, filter_elem: []
	
	, init: function() {
		this.filter_definitions = $("#search-filter-definitions");
		this.filter_applied     = $("#search-filter-applied");
		this.filter_implied     = $("#search-filter-implied");
		this.filter_elem        = $(".search-filter", this.filter_definitions);
	}
	
	
	, filter_add: function() {
		var new_filter = this.filter_elem.clone().appendTo(this.filter_applied);
		this.__update_filter_display();
		try { search_filter.hooks['post_filter_add'](new_filter); } catch(e) {}
		return new_filter;
	}
	
	, filter_del: function(obj) {
		$(obj).parents(".search-filter").remove();
		this.__update_filter_display();
	}
	
	, filters_remove_all: function() {
		this.filter_applied.find(".search-filter").remove();
		$.cookie('fiches_search_filters', null);
		this.filter_add();
	}
	
	, filter_move: function(obj, dir) {
		var $filter = $(obj).parents(".search-filter");
		if (dir=='up') {
			$filter.prev().before($filter);
		} else if (dir=='down') {
			$filter.next().after($filter);
		}
		this.__update_filter_display();
	}
	
	, __update_filter_display: function() {
		var filters = $("#search-filter-applied .search-filter");
		filters.find(".filter-op, .filter-del, .filter-up, .filter-down").css('visibility','visible');
		filters.first()
				.find(".filter-op, .filter-up").css('visibility','hidden');
		filters.last()
				.find(".filter-down").css('visibility','hidden');
		if (filters.length==1) {
			filters.find(".filter-del").css('visibility','hidden');
		}
	}
	
	, filter_class_change: function() {
		var class_selector = $(this),
			filter_content = search_filter.filter_definitions.find(".filter-"+class_selector.val()).clone();
		class_selector.parents(".search-filter")
			.find(".filter-content-placeholder").html("")
				.append(filter_content);
		try { search_filter.hooks['post_filter_class_change'](filter_content); } catch(e) {}
	}
	
	
	, filter_operator_change: function(){
		var filter_op = $(this);
		filter_op.next().focus()
			.parents(".search-filter-content")
				.find(".op_spec").hide().end()
				.find(".op_"+filter_op.val()).show();
	}
	
	
	, get_filters_query: function(){
		var filters_def = [];
		$("#search-filter-applied, #search-filter-implied").find(".search-filter-content").each(function(){
			var $this = $(this), 
				$filter = $this.parents('.search-filter'),
				parts = [], 
				filter_op = $filter.find('[name=filter_op]').val(),
				filter_class = $filter.find('[name=filter_class]').val();
			
			$this.find("[name=pre-process-hook]").each(function(){ search_filter.hooks[$(this).val()]($this); });
			
			$this.find(".search-filter-content-part").each(function(){
				var c_filter = $(this),  								// current Filter
					f_obj = {
						attr : c_filter.find('[name=attr]').val(),		// the query agrument
						type : c_filter.find('[name=type]').val(),		// the query value type
						op   : c_filter.find('[name=op]').val(),		// the query operator
						val  : c_filter.find('[name=val]').val()		// the query value
					};
				if (typeof(f_obj.val)=='undefined') { return; }
				
				// --------------------
				// -- Validations
				// --------------------
				if (f_obj.type == 'number' ) {
					if (isNaN(parseInt(f_obj.val)) && f_obj.val=='notnull') {
						f_obj.op = 'isnull';
						f_obj.val = "0";
					}
				}

				if (f_obj.type == 'string' ) {
					if (f_obj.val=='notnull') {
						f_obj.op  = 'isnull';
						f_obj.val = "";
						parts.push(f_obj);
					}
				}
				
				if (f_obj.op == 'range' ) {
					var c_val = parseInt(f_obj.val), c_val1;
					try {
						c_val1 = parseInt(c_filter.find('[name=val1]').val());
					} catch(e) {
						c_val1 = NaN;
					}
					
					if (isNaN(c_val)) {
						if (isNaN(c_val1)) { 
							// If both are invalid, abort
							return;
						}
						
						// If no valid start value, change the query into a "before" c_val1
						f_obj.op = 'lt';
						f_obj.val = c_val1;
					}
					else if (isNaN(c_val1)) {
						// If no valid end date, change the query into a "after" c_val
						f_obj.op = 'gt';
						f_obj.val = c_val;
					}
					else {
						// Real range
						// Push two fiter params, one with higher limit (c_val1) and op = 'lt'
						// and one with the lower limit (c_val) with op ='gt'
						
						// Check that c_val and c_val1 are in the correct order
						if (c_val1 < c_val) {
							var tmp_val = c_val;
							c_val = c_val1; c_val1 = tmp_val;
						}
						
						// Save original operator for potential unserialization
						f_obj.op_origin = 'range';
						
						// Clone f_obj for the lower limit
						parts.push($.extend({}, f_obj, {val: c_val, op:'gt'}));
						
						// The obj for the lower limit
						f_obj.val = c_val1;
						f_obj.op  = 'lt';
						
					}
				}
			
				if (f_obj.val != "") {
					parts.push(f_obj);
				}
			});	// End of each search-filter-content-part
			
			// Post Hooks invocation
			$this.find("[name=post-process-hook]").each(function(){ search_filter.hooks[$(this).val()]($this,{op:filter_op,cl:filter_class, params:parts}); });
			
			filters_def.push({op:filter_op, cl:filter_class,  params:parts});
		}); // End of each filter-content
	
		return {model_name:search_model_name, filters:filters_def};
	}

	, serialize_filters: function() {
		return $.toJSON(search_filter.get_filters_query());
	}
	
	, unserialize_filters: function(jsonStr) {
		try{
			var filters_def = $.parseJSON(jsonStr);
			if (filters_def.model_name !== search_model_name) {
				return false;
			}
			for (var f_idx=0; f_idx<filters_def.filters.length; f_idx++) {
				var f_def = filters_def.filters[f_idx];
				if ($("#search-filter-implied .filter-" + f_def.cl).length > 0) { continue; }
				var new_filter = search_filter.filter_add();
				
				$('[name=filter_op]', new_filter).val( f_def['op'] );
				try {
					$('.filter-class', new_filter).val(f_def['cl']).change();
				} catch(e) {}
				var parts = new_filter.find(".search-filter-content-part");
				for (var p_idx=0; p_idx<f_def.params.length; p_idx++) {
					var param = f_def.params[p_idx],
						op = param.op_origin ? param.op_origin : param.op;
					
					$(parts[p_idx])
						.find('[name=attr]').val(param.attr).end()
						.find('[name=op]').val(op).change().end()
						.find('[name=type]').val(param.type).end()
						.find('[name=val]').val(param.val)
					;
					if (op=='range') {
						param = f_def.params[p_idx+1];
						$(parts[p_idx]).find('[name=val1]').val(param.val)
						p_idx++;
					}

				}
				try { search_filter.hooks['post_unserialize_filter'](f_def, new_filter) } catch(e) {}				
			}
			return true;
		} catch (e) {
			return false;
		}
	}
	
	, hooks: {
		v:0
		
		, biography__societymembership__date__pre_hook: function(obj){
			//console.log("do hook for: ");
			//console.log(obj);
		}
		
		, biography__last__version__post_hook: function(obj, p) {
			var f_obj = {
				attr : "biography__version",
				type : "number",
				op   : "exact",
				val  : "0"
			};
			// p.params.push(f_obj);
		}
		
	}
};


var display_settings = display_settings || {
	  debug: true
    , save_settings: function() {
		var settings_obj = {},
//			col_display_settings = $("#ui-dialog-display-columns-settings .column-display-settings"),
			col_display_settings = $("#ui-dialog-filterset-settings .column-display-settings"),
  			model_name = $("[name=model_name]", col_display_settings).val();
		settings_obj[model_name] = {};
		
		$(".column-settings :checked", col_display_settings).each(function(){
		    var $this = $(this),
		        row_name = $this.attr('name');
		    try {
				settings_obj[model_name][row_name.split('__')[1]] = $this.val();
		    } catch(e) {}
		});
		$.post(save_settings_url, {
			display_settings: $.toJSON(settings_obj)
		});
    }
};


function display_params_dialog() {
	//$("#ui-dialog-display-columns-settings").dialog({
	$("#ui-dialog-filterset-settings").dialog({
		  modal: true
		, resizable: false  
		, width: 550
		, height: 430
		, buttons: { "Ok": function() { display_settings.save_settings(); $(this).dialog("close"); }, "Cancel": function() { $(this).dialog("close"); } }
	});

}


function execute_query() {
	var serialized_filters = search_filter.serialize_filters();
	if (Base64 && typeof Base64.encode === 'function') {
		serialized_filters = Base64.encode(serialized_filters);
	}
	var ordering = $("#result-ordering"),
		order_by = ($("#result-ordering").length == 0) ? "" : $("#result-ordering").val();
	
	$("#search-results").
		text("").
		append(
			$('<div>', { 
				style: "text-align:center",
				text: "Recherche en cours..."
			}).append($('<br>')).
			append(
				$('<img>', {
					'src': MEDIA_URL + "images/ajax-loader.gif"
				})
			)
		).
		load(do_search_url+"?q="+serialized_filters+"&o="+order_by);
	$.cookie('fiches_search_filters', null);
	$.cookie('fiches_search_filters', serialized_filters, {path:document.location.pathname});
	$.cookie('fiches_search_result_order', order_by, {path:document.location.pathname});
}

	

$(document).ready(function(){
	search_filter.init();
	$("select.filter-operator").live('change', search_filter.filter_operator_change);
	$("select.filter-class").live('change', search_filter.filter_class_change);
	
	var cookie_filters = $.cookie('fiches_search_filters');
	try { cookie_filters = Base64.decode(cookie_filters); } catch(e) {}
	
	if (cookie_filters && search_filter.unserialize_filters(cookie_filters)) {
		// cookie parsed, do nothing
	} else {
		search_filter.filter_add();
	}
	
	try {
		var cookie_order = $.cookie('fiches_search_result_order');
		if (cookie_order) {
			$("#result-ordering").val(cookie_order);
		}
	} catch (e) {};
	
});

// jQuery-UI pour dialog
$(document).ready(function(){
	$(".column-display-settings .column-settings").buttonset();
	//$("#ui-dialog-filterset-settings-tabs").tabs();
});

// Pagination
$(document).ready(function(){
	$(".paginator .pagination a").live('click', function(){
		$("#search-results").text("").
		append(
			$('<div>', { 
				style: "text-align:center",
				text: "Recherche en cours..."
			}).append($('<br>')).
			append(
				$('<img>', {
					'src': MEDIA_URL + "images/ajax-loader.gif"
				})
			)
		).
		load(do_search_url+this.search);
		return false;
	});
});

