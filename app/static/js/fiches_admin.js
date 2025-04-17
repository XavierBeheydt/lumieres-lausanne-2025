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

var fiches_admin;

if (django && django.jQuery) {
	(function($){ 
	   
        window.fiches_admin = window.fiches_admin || {
            add_person_biography: function(pk) {
                $("input[name=_selected_action][value="+pk+"]").attr("checked","checked");
                $("select[name=action]").val("add_biography");
                $("form").submit();
            }
        }

	   
	   $(document).ready(function(){
		   window.focus();
		   
			// ========================
			// Personne moderne, replace select by checkbox for NullBoolean Field
			// ========================
			$("select[id$=modern]").each(function(i, n){
				var $n = $(n), 
				    $cb = $("<input>", {
					    'type': "checkbox",
					    'rel': $n.attr('name')
				     }).change(function(){
					    var $this = $(this), 
						    $n = $("select[name=" + $this.attr('rel') + "]");
					    $n.val(($this.is(":checked")) ? "2" : "3");
				     });
				if ($n.val() == "2") {
					$cb.attr("checked", "checked");
				}
				$n.after($cb).hide();
			});
		
		     // =======================
			 // Project
			 // =======================
			 if ($("#project_form").length) {
			 	var $url_field = $("#id_url");
                $url_field
                    .after($("<button>", {
                        'text': "vérifier",
                        'type': "button",
                        'class': "button icon-btn check-btn",
                        'style': "margin-left: 10px"
                    }).prepend($('<span>', {'class': "icon", 'text': " "})) );
				if (typeof URLify == 'function') {
					$url_field.after($("<button>", {
                            'text': "générer",
							'title': "Générer l'url à partir de la valeur actuelle du nom",
                            'type': "button",
                            'class': "button icon-btn generate-btn",
                            'style': "margin-left: 10px",
							'click': function(){
								$url_field.val(URLify($("#id_name").val(), 100));
								return false;
							}
                        })
					    .prepend($('<span>', {'class': "icon", 'text': " "})) );
				}

			 }
			 
		});
		
	})(django.jQuery);
}