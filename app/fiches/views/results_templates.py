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
#
result_person = {
                 
    'person_name': '''
        {% if person.has_biography %}
            <a href="{% url 'biography-display' person.id %}" target="_blank">{{ person.get_biography.person_name }}</a>
        {% else %}
            <span>{{ person.name }}</span>
        {% endif %}
    ''',
    
    'birth_date' : '<span title="{{ bio|date_f:"birth_date" }}{% if bio.birth_place %} � {{ bio.birth_place }}{% endif %}">{{ bio.birth_date|date:"Y" }}</span>',
    'birth_date_place' : '{{ bio|date_f:"birth_date" }}{% if bio.birth_place %} � {{ bio.birth_place }}{% endif %}',

    'death_date' : '<span title="{{ bio|date_f:"death_date" }}{% if bio.death_place %} � {{ bio.death_place }}{% endif %}">{{ bio.death_date|date:"Y" }}</span>',
    'death_date_place' : '{{ bio|date_f:"death_date" }}{% if bio.death_place %} � {{ bio.death_place }}{% endif %}',
    
    'profession': '''
        {% if bio.profession_set %}
        <ul>
        {% for p in bio.profession_set.all %}
            <li title="{{ p.get_formatted_dates|join:" - " }}">{{ p.position }}{% if p.place %}&nbsp;�&nbsp;{{ p.place }}{% endif %}</li>
        {% endfor %}
        </ul>
        {% endif %}
    ''',
    
}