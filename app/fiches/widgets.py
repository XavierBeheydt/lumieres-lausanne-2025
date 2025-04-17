# -*- coding: utf-8 -*-
#
#    Copyright (C) 2010-2012 Université de Lausanne, RISET
#    < http://www.unil.ch/riset/ >
#
#    This file is part of Lumières.Lausanne.
#    Lumières.Lausanne is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Lumières.Lausanne is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    This copyright notice MUST APPEAR in all copies of the file.

from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str, force_str
from django.utils.text import Truncator
from django.forms.models import modelformset_factory
from itertools import chain
from django.apps import apps
from fiches.utils import dbg_logger

# Import models to use the fields correctly
from django.db import models  # <-- Add this import

# TODO: to delete
# def get_lookup_class(field):
#     try:
#         return f"{field.remote_field.model.__name__}_{field.name}"
#     except Exception as e:
#         dbg_logger.debug(f"Error setting lookup_class: {e}")
#         return ""

class PersonWidget(forms.TextInput):
    """
    Custom widget for ForeignKey fields pointing to Person objects.
    """

    class Media:
        css = {
            'all': ('css/jquery.autocomplete.css',),
        }
        js = (
            'js/lib/jquery/jquery.bgiframe.min.js',
            'js/lib/jquery/jquery.ajaxQueue.js',
            'js/lib/jquery/jquery.autocomplete.min.js',
        )

    def __init__(self, fk_field=None, attrs=None):
        """
        Initialize the widget with metadata from the ForeignKey field.
        :param fk_field: A ForeignKey field object or None.
        :param attrs: Optional widget attributes.
        """
        self.fk_field = fk_field
        self.lookup_class = ""
        if fk_field:
            try:
                related_model_name = fk_field.related_model.__name__
                related_field_name = fk_field.name
                self.lookup_class = f"{related_model_name}_{related_field_name}"
            except AttributeError as e:
                print(f"Error setting lookup_class: {e}")

        attrs = attrs or {}
        super().__init__(attrs)

class StaticList(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=(), add_title="Add", empty_label=None):
        super().__init__(attrs)
        self.choices = list(choices)
        self.add_title = add_title
        self.empty_label = empty_label

    # Add `renderer=None` so Django 2.1+ doesn’t complain
    def render(self, name, value, attrs=None, choices=(), renderer=None):
        """
        Custom rendering for a 'static' dropdown + 'Add' button approach.
        Users pick from an existing list; no free text input is provided.
        """
        if value is None:
            value = ''
        if attrs is None:
            attrs = {}
        final_attrs = self.build_attrs(attrs)
        final_attrs['name'] = name

        output = ['<div class="staticlist_container">']

        # Each selected value is displayed in a small 'value entry' div
        value_entry_template = (
            '<div class="staticlist_value_entry">'
            '<span class="staticlist_value_label">%(label)s</span>'
            '<input type="hidden" name="%(name)s" value="%(value)s" />'
            '</div>'
        )
        output.append('<div class="staticlist_values">')

        if value is None:
            value = []
        # Convert to list if not already
        value = list(value)

        # Show the selected items
        for item_value, item_label in chain(self.choices, choices):
            if item_value in value:
                output.append(
                    value_entry_template % {
                        "label": item_label,
                        "value": item_value,
                        "name": final_attrs['name']
                    }
                )
        output.append('</div>')  # Close .staticlist_values

        # The dropdown to pick a new Society/Académie from existing choices
        output.append('<span class="staticlist_addbox">')
        output.append('<select class="staticlist_helper_select">')

        options = self.render_option_list([value], chain(self.choices, choices))
        if options:
            if self.empty_label:
                options = '<option value="">%s</option>\n%s' % (self.empty_label, options)
            output.append(options)
        output.append('</select>')

        # The "Add" button
        output.append(
            '<button class="staticlist_helper_addbut" '
            'onclick="staticlist_widget.addToList(this, \'%(name)s\'); return false;">'
            '<span>%(add)s</span></button>' % {
                'name': final_attrs['name'],
                'add': self.add_title
            }
        )
        output.append('</span>')  # Close .staticlist_addbox

        # A small hint for the user
        output.append(
            '<span class="staticlist_add_info">'
            'Validez votre sélection avec le bouton <strong>"%s"</strong>'
            '</span>' % self.add_title
        )

        output.append('</div>')  # Close .staticlist_container

        # Template reference for the JS code
        output.append(
            '<script type="text/javascript">'
            'var staticlist_widget = staticlist_widget || {}; '
            'staticlist_widget.templates = staticlist_widget.templates || {}; '
            'staticlist_widget.templates["%(name)s"] = \'%(template)s\';'
            '</script>' % {
                "name": final_attrs['name'],
                "template": value_entry_template
            }
        )

        return mark_safe('\n'.join(output))

    def render_option_list(self, selected_choices, choices):
        output = []
        for option_value, option_label in choices:
            option_value = force_str(option_value)
            selected_html = ' selected="selected"' if option_value in selected_choices else ''
            output.append(
                '<option value="%s"%s>%s</option>' %
                (option_value, selected_html, force_str(option_label))
            )
        return '\n'.join(output)

class DynamicList(forms.SelectMultiple):
    class_prefix = 'dynamiclist'
    jsvarname    = 'dynamiclist_widget'
    
    def __init__(self, rel=None, attrs=None, choices=(), add_title="Add", placeholder=None):
        # Handle ForeignKey or ManyToManyField (if provided)
        if rel is not None:
            if isinstance(rel, models.ForeignKey):
                self.rel = rel.related_model
            elif isinstance(rel, models.ManyToManyField):
                self.rel = rel.related_model
            else:
                self.rel = None
        else:
            self.rel = None

        # Use Python 3 style super()
        super().__init__(attrs)
        self.choices = list(choices)
        self.add_title = add_title
        self.placeholder = placeholder or ""

    #           v---- add renderer=None here
    def render(self, name, value, attrs=None, choices=(), renderer=None):
        """
        Custom rendering to produce a dynamic list UI for M2M relationships.
        Compatible with Django >= 2.1 by accepting 'renderer=None'.
        """
        from fiches.models import Person

        if value is None:
            value = []

        # Ensure we have a 'name' attribute in attrs
        if attrs is None:
            attrs = {}
        attrs['name'] = name

        final_attrs = self.build_attrs(attrs)
        output = [f'<div class="{self.class_prefix}_container">']

        # The existing entries section
        output.append(f'<div class="{self.class_prefix}_values">')

        # Template for each value entry
        value_entry_template = (
            f'<div class="{self.class_prefix}_value_entry">'
            f'<span class="{self.class_prefix}_value_label">%(label)s</span>'
            f'<input type="hidden" name="%(name)s" value="%(value)s" />'
            f'</div>'
        )

        # Separate the IDs vs new text
        id_value = []
        name_value = []
        for val in list(value):
            if isinstance(val, Person):
                id_value.append(val.id)
            elif isinstance(val, str):
                if '|' in val:
                    try:
                        id_value.append(int(val.split("|")[0]))
                    except ValueError:
                        pass
                else:
                    name_value.append(val.strip('|'))
            else:
                id_value.append(val)

        if self.rel:
            id_key = f"{self.rel._meta.pk.name}__in"  # typically "id__in"
            objs = self.rel._default_manager.filter(**{id_key: id_value})
        else:
            objs = []

        # Render existing (DB) objects
        for obj in objs:
            obj_label = str(obj)
            output.append(
                value_entry_template % {
                    "label": obj_label,
                    "value": f"{obj.id}|{obj_label}",
                    "name": final_attrs['name'],
                }
            )

        # Render text-only (new) entries
        for obj_name in name_value:
            output.append(
                value_entry_template % {
                    "label": obj_name,
                    "value": f"|{obj_name}",  # no ID, just text
                    "name": final_attrs['name'],
                }
            )

        output.append('</div>')  # close ._values

        # The input + button area
        output.append('<span class="dynamiclist_addbox">')
        output.append(
            f'<input class="{self.class_prefix}_helper_input" placeholder="{self.placeholder}" />'
            f'<input class="helper_input_value" type="hidden" />'
        )
        output.append(
            f'<button type="button" class="{self.class_prefix}_helper_addbut helper_addbut" '
            f'onclick="{self.jsvarname}.addToList(this, \'{final_attrs["name"]}\'); return false;">'
            f'<span>{self.add_title}</span></button>'
        )
        output.append('</span>')
        output.append(
            f'<span class="dynamiclist_add_info">'
            f'Validez votre sélection avec le bouton <strong>"{self.add_title}"</strong>'
            f'</span>'
        )

        output.append('</div>')  # close ._container

        # For the JS code that references value_entry_template
        output.append(
            f'<script type="text/javascript">'
            f'var {self.jsvarname} = {self.jsvarname} || {{}}; '
            f'{self.jsvarname}.templates = {self.jsvarname}.templates || {{}}; '
            f'{self.jsvarname}.templates["{final_attrs["name"]}"] = \'{value_entry_template}\';'
            f'</script>'
        )

        return mark_safe('\n'.join(output))

