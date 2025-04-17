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
 * Script used for the management of the collections in the Workpace pages
 */
var collection = (function(){
	var collection = {
		current_id: null,
		
		urls: {
			'create': "",
			'edit'  : "",
			'remove': "",
			'popup' : ""
		},
		
		create: function() {
			var url = collection.urls.create;
			if (arguments.length>0 && typeof arguments[0] === 'object' && typeof arguments[0].callback === 'string') {
				url += '?callback='+arguments[0].callback;
			}
			var dlog = $("<div>", {
				'id': 'collection-edit-dlog',
				'title': 'Nouvelle collection',
				'html': '<iframe src="'+url+'" width="570" height="380"/>'
				}).appendTo("body").dialog({
					modal: true,
					resizable: false,
					width: 600,
					height: 430,
					close: function() { dlog.remove(); },
					open: function() {}
				});
		},
		
		edit: function(coll_id) {
			if (typeof coll_id === 'undefined' || !coll_id || isNaN(coll_id)) {
				return false;
			}
			// Replace the placeholder '__COLL_ID__' with the actual collection ID
			var url = collection.urls.edit.replace('__COLL_ID__', coll_id);
			if (arguments.length > 1 && typeof arguments[1] === 'object' && typeof arguments[1].callback === 'string') {
				url += '&callback=' + arguments[1].callback;
			}
			var dlog = $("<div>", {
				'id': 'collection-edit-dlog',
				'title': 'Modification de la collection',
				'html': '<iframe src="' + url + '" width="570" height="380"/>'
			}).appendTo("body").dialog({
				modal: true,
				resizable: false,
				width: 600,
				height: 420,
				close: function() { dlog.remove(); },
				open: function() {}
			});
		},
		
		
		edit_close: function() {
			$("#collection-edit-dlog").dialog('close');
		},
		
		edit_done: function() {
			collection.edit_close();
			// To avoid reloading the page, pass an argument object with the proterty 'no_reload' = true
			if (arguments.length > 0 && typeof arguments[0] === 'object' && arguments[0].no_reload) {
				return false;
			}
			document.location.href = document.location.href;
			return false;
		},
		
		remove: function(coll_id, coll_title) {
			if (typeof coll_id === 'undefined' || !(coll_id) || isNaN(coll_id)) { return false; }
			// Replace the placeholder '__COLL_ID__' with the actual collection ID
			var url = collection.urls.remove.replace('__COLL_ID__', coll_id),
				dlog = $("<div>", {
					'title': 'Supprimer la collection',
					'html': 'Etes-vous sûr de vouloir supprimer la collection &laquo;' + coll_title + '&raquo; ?'
				}).appendTo("body").dialog({
					modal: true,
					resizable: false,
					buttons: {
						'Oui': function() { 
							$(this).dialog('close'); 
							document.location.href = url;
						},
						'Non': function() { $(this).dialog('close'); }
					}
				});
		},		
		
		popup_display: function(coll_id) {
			if (typeof coll_id === 'undefined' || !coll_id) { 
				return false;
			}
			// Replace the placeholder '__COLL_ID__' with the actual collection ID
			var url = collection.urls.popup.replace('__COLL_ID__', coll_id);
			var w_title = 'popup_collection_' + coll_id;
			var w = window.open(url, w_title, 'width=630, height=500, scrollbars=1');
		},
		
		
		remove_item: function(p) {
		    p.obj.addClass("hilight");
			var dlog = $("<div>", {
					'id': 'collection-remove-object-confirm-dlog',
					'title': 'Retirer un élément de la collection',
					'html': 'Etes-vous sûr de vouloir retirer l\'élément <br/><span class="ll-collection-item-title">' + p.type_title + ': ' + p.item_title + '</strong> ?'
				}).appendTo("body").dialog({
					modal: true,
					resizable: false,
					width: 400,
					height: 150,
					buttons: {
						'Oui': function() {
							$.ajax({
								'url': collection_remove_object_url,
								'type': 'POST',
								'data': {'coll_id': collection.current_id, 'item_id': p.item_id, 'item_type': p.item_type},
								success: function() { p.obj.hide(); dlog.dialog('close'); },
								error: function() { dlog.html("Une erreur est survenue lors du traitement. Essayez de recharger la page."); }
							});
						},
						'Non': function() { p.obj.removeClass("hilight"); dlog.dialog('close'); }
					},
					close: function() { dlog.remove(); }
				});
			
		}
		
	};
	return collection;
})();




/*
function remove_collection(obj) {
	var $obj= $(obj),
		//coll_title = $obj.contents().filter(function() {return this.nodeType == 3;}).text(),
		coll_title = $obj.find('a').text(),
		collID;
	try { collID = $obj.attr('id').split('__')[1]; } catch(e) { return false; }
	
	var url = collection_delete_url_base.replace('#',collID),
		dlog = $("<div>", {
		'title': 'Supprimer la collection',
		'html': 'Etes-vous sûr de vouloir supprimer la collection &laquo;' + coll_title + '&raquo; ?'
	}).appendTo("body").dialog({
		modal: true,
		resizable: false,
		buttons: {
			'Oui': function() { 
				$(this).dialog('close'); 
				document.location.href = url;
			},
			'Non': function() { $(this).dialog('close'); }
		}
	});
	return false;
}
*/
/*
function edit_collection(obj) {
	var collID;
	try { collID = $(obj).attr('id').split('__')[1]; } catch(e) { return false; }
	var url = collection_edit_url_base.replace('#',collID),
		dlog = $("<div>", {
			'id': 'collection-edit-dlog',
			'title': 'Modification de la collection',
			'html': '<iframe src="'+url+'" width="580" height="370"/>'
		}).appendTo("body").dialog({
			modal: true,
			resizable: false,
			width: 600,
			height: 400,
			close: function() { dlog.remove(); },
			open: function() {}
		});
}
*/
/*
function new_collection(obj) {
	var dlog = $("<div>", {
			'id': 'collection-edit-dlog',
			'title': 'Nouvelle collection',
			'html': '<iframe src="'+collection_new_url+'" width="580" height="370"/>'
		}).appendTo("body").dialog({
			modal: true,
			resizable: false,
			width: 600,
			height: 400,
			close: function() { dlog.remove(); },
			open: function() {}
		});
}
*/
/*
function edit_collection_close() { 
	// To avoid reloading the page, pass an argument object with the proterty 'no_save' = true
	$("#collection-edit-dlog").dialog('close');
	if (arguments.length > 0 && typeof arguments[0] === 'object' && arguments[0].no_save) {
		return false;
	}
	document.location.href = document.location.href;
	return false;
}
*/
/*
function collection_display_popup(obj) {
	var collID;
	try { collID = $(obj).attr('id').split('__')[1]; } catch(e) { return false; }
	var url = collection_display_popup_url_base.replace('#',collID),
		w_title = 'popup_collection_'+collID,
		w = window.open(url, w_title, 'width=400, height=600');
}
*/

/**
 * Remove an object from a collection
 * @param {Object} obj	the Element tyg the contains the id of the object to be removed in the form celem__<item_type>__<item_id>
 */
/*
function remove_collection_item(obj) {
	var $obj = $(obj),
		item_title = $obj.contents().filter(function() {return this.nodeType == 3;}).text(),
		type_title = $obj.closest('dd').prev('dt').text(),
		coll_id = current_collection_id,
		item_id,
		item_type;

	try { 
		item_type = $obj.attr('id').split('__')[1];
		item_id   = $obj.attr('id').split('__')[2];
	} catch(e) { return false; }
	
	var dlog = $("<div>", {
		'id': 'collection-remove-object-confirm-dlog',
		'title': 'Retirer un élément de la collection',
		'html': 'Etes-vous sûr de vouloir retirer l\'élément &laquo;' + type_title + ': ' + item_title + '&raquo; ?'
	}).appendTo("body").dialog({
		modal: true,
		resizable: false,
		buttons: {
			'Oui': function() {
				$.ajax({
					'url': collection_remove_object_url,
					'type': 'POST',
					'data': {'coll_id': coll_id, 'item_id': item_id, 'item_type': item_type},
					success: function() { $obj.hide(); dlog.dialog('close'); },
					error: function() { dlog.html("Une erreur est survenue lors du traitement. Essayez de recharger la page."); }
				});
			},
			'Non': function() { dlog.dialog('close'); }
		},
		close: function() { dlog.remove(); }
	});
	return false;
}
*/