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
 * Script for adding elements to collections.
 * The functions defined here are called on pages displaying objects that can be added
 * to a collection. 
 * Ex:	on the display page of Bilio, Biography or Manuscript
 * 		on the list page of the same
 * 		on a page presenting result of a search query	
 */
var collector = (function(){
	var collector = {
		urls: { 
		  add: '', 
		  list: '', 
		  'shortinfo': '', 
		  '_project': {
                add: ''
            }
		},
		
		collection_obj: null,
		
		addObj_dialog: null,
		
		init: function() {
			// Init the main dialog
			collector.addObject_dialog = $("#ll-collector-dialog").dialog({
				autoOpen: false,
				modal: true,
				resizable: false,
				width: 450,
				buttons: { 
					'Ajouter' : collector.addObj_do,
					'Annuler': function(){ $(this).dialog('close'); }
				},
				open: function() {
					//collector.toggle_dlogShortInfo(false);
					collector.addObj_updateCollectionList();
					$("#ll-collector-dialog-form").show();
					collector.addObject_dialog.find(".ajax-loader, .errors").hide();
				},
				close: function() {
					collector.toggle_dlogShortInfo(false);
					collector.addObject_dialog.find(".ll-collector-item-title").html("");
				}
			});
			// Add «ENTER» Keydown Handler for adding the object
			$("#ll-collector-dialog").dialog('widget').keydown(function(event){ 
				if (event.keyCode && event.keyCode === $.ui.keyCode.ENTER){
					collector.addObj_do();
					event.preventDefault();
				}
			});
			
			// Setup the "New Collection" button
			$("#ll-collector-dialog-add-but").button({icons: { primary: "ui-icon-plusthick" }}).click(collector.create_new_coll);
			
			// Display Shortinfo about current collection
			$("#ll-collector-dialog-collinfo > a").click(function(){
				collector.toggle_dlogShortInfo();
				return false;
			});
		},
		
		update_shortinfo: function(){
			var coll_id = $("#ll-collector-collection").val(),
				//url = collector.urls.shortinfo.replace('#',coll_id);
				url = collector.urls.shortinfo.replace('%23',coll_id); // Replacing %23 (encoded hashtag #) with coll_id 
			$("#ll-collector-dialog-collinfo .ajax-loader").show();
			$("#ll-collector-dialog-collinfo-data").hide().load(url, function(){
				$("#ll-collector-dialog-collinfo-data").show();
				$("#ll-collector-dialog-collinfo .ajax-loader").hide();
			});
		},
		
		/**
		 * If status is true, force expand
		 * @param {Object} status
		 */
		toggle_dlogShortInfo: function(status) {
			var $dlog = $("#ll-collector-dialog"),
				expanded = (typeof status === 'undefined') ? $dlog.hasClass('expanded') : (!status),
				dH = 160;

			
			$dlog.toggleClass('expanded',!expanded).height(function(i,h){return expanded ? (h - dH) : (h + dH);});
			// Status is expanded -> collapse info
			if (expanded) {
				$("#ll-collector-dialog-collinfo-data").html("").hide();
				$("#ll-collector-dialog-collinfo > a .ui-icon").removeClass("ui-icon-triangle-1-s").addClass("ui-icon-triangle-1-e");
				$("#ll-collector-collection").change(function(){});
			}
			// -> Expand and load
			else {
				$("#ll-collector-dialog-collinfo-data").show();
				$("#ll-collector-collection").change(collector.update_shortinfo);
				$("#ll-collector-dialog-collinfo > a .ui-icon").addClass("ui-icon-triangle-1-s").removeClass("ui-icon-triangle-1-e");
				collector.update_shortinfo();
			}
			return !expanded;
		},
		
		addObj_updateCollectionList: function() {
			/*$.getJSON(collector.urls.list, function(data) {
				$("#ll-collector-collection").html(data);
			});*/
			$("#ll-collector-collection").load(collector.urls.list);
		},
		
		
		/**
		 * Send data to the view in charge of adding the object to the specified colection
		 */
		addObj_do: function() {
			$("#ll-collector-dialog-form").hide();
			collector.addObject_dialog.find(".errors").hide();
			collector.addObject_dialog.find(".ajax-loader").show();
			
			var obj_settings = {
				item_id: $("#ll-collector-objid-id").val(),
				item_type: $("#ll-collector-objtype-id").val(),
				coll_id: $("#ll-collector-collection").val()
			};
			var containerType = $("#ll-collector-dialog-form :radio[name=ll-collector-containerType]:checked").val() || 'collection';
			if (containerType == 'project') {
				obj_settings['proj_id'] = $("#ll-collector-project").val();
				delete(obj_settings.coll_id);
			}
			
			
			
			if ( (!obj_settings.item_id) || (!obj_settings.item_type) || (obj_settings.item_type==='unknown') ) {
				collector.error_msg("Impossible de continuer, la définition de l'élément ou de la collection est incomplet.");
			} else {
				$.ajax({
					url: (containerType == 'project') ? collector.urls._project.add : collector.urls.add,
					type: "POST",
					data: obj_settings,
					success: function() {
						collector.addObject_dialog.dialog("close");
					},
					error: function(xhr, textStatus, errorThrown) {
						// Construct a detailed error message
						//collector.error_msg(xhr.responseText);
						var errorMsg = "An error occurred while processing your request.";
						errorMsg += "<br/><strong>Response Text:</strong> " + (xhr.responseText || "No response text available.");
						errorMsg += "<br/><strong>Text Status:</strong> " + (textStatus || "No status text available.");
						errorMsg += "<br/><strong>Error Thrown:</strong> " + (errorThrown || "No error details available.");
						
						// Display the detailed error message to the user
						collector.error_msg(errorMsg);
					}
				});
				
				/*$.post(collector.urls.add, obj_settings, function(data, textStatus, xhr ){
					//
				});*/
			}
			
			return false;
		},
		
		
		/**
		 * Configure the dialog with the parameters of obj and open it
		 * obj = {
		 *     item_title: string with the title
		 *     item_id: id of the item to be added
		 *     item_type: class Name 
		 * }
		 * 	
		 * @param {Object} obj
		 * 
		 */
		addObj_open: function(obj) {
			var obj_settings = $.extend({},{item_title:"inconnu", item_id:-1, item_type:"unknown"},obj);
			collector.addObject_dialog.find(".ll-collector-item-title").html(obj_settings.item_title);
			$("#ll-collector-objid-id").val(obj.item_id);
			$("#ll-collector-objtype-id").val(obj.item_type);
			
			collector.update_inCollection(obj.item_type, obj.item_id);
			
			collector.addObject_dialog.find(".ll-collector-project-selector")
			    .css("display", $.inArray(obj.item_type, ['Biblio', 'Transcription']) > -1 ? 'block' : 'none' );
			
			collector.addObject_dialog.dialog('open');
		},
		
		update_inCollection: function(item_type, item_id) {
			$.get(collector.urls.incollection, {type: item_type, id: item_id}, function (data) {
				if ( data.incollection ) {
					$('#ll-collector-incollection')
						.show()
						.html('<br/><em>fait déjà partie de: </em>' + data.incollection);
				} else {
					$('#ll-collector-incollection').hide();
				}
				if ( data.inproject ) {
					$('#ll-collector-inproject')
						.show()
						.html('<br/><em>fait déjà partie de: </em>' + data.inproject);
				} else {
					$('#ll-collector-inproject').hide();
				}
			}, "json");
		},
		
		create_new_coll: function() {
			try {
				collector.collection_obj.create({
					'callback': 'collector.create_coll_done'
				});
			} catch(e) {}
		},
		
		create_coll_done: function(p) {
			// p.coll_id -> id of the new collection
			try {
				collector.collection_obj.edit_close();
				$("#ll-collector-collection").load(collector.urls.list);
			} catch(e) {}
		},	
		
		
		error_msg: function(msg) {
			if (!msg) msg = "";
			$("#ll-collector-dialog-form").hide();
			collector.addObject_dialog.find(".ajax-loader").hide();
			collector.addObject_dialog.find(".errors").show().find('.errors-content').html(msg);
		}
		
		
	};
	
	return collector;
})();
$(document).ready(function(){ collector.init(); });

