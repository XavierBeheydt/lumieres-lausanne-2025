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

from django.urls import re_path, include
from fiches.views.projects import (
    index_project,
    display_project,
    add_object,
    remove_object,
    get_project_description,
    get_project_transcription,
    get_project_bibliography,
)

urlpatterns = [
    # Projet principal avec slug optionnel
    re_path(
        r'^((?P<proj_slug>[a-zA-Z][a-zA-Z0-9_-]+)/)?$',
        index_project,
        name='project-index'
    ),

    # Afficher le projet par ID
    re_path(
        r'^(?P<proj_id>\d+)/$',
        display_project,
        name="project-display-id"
    ),

    # Afficher le projet par slug
    re_path(
        r'^(?P<proj_slug>[a-zA-Z][a-zA-Z0-9_-]+)/$',
        index_project,
        name="project-display"
    ),

    # Ajouter un objet au projet
    re_path(
        r'^_add-object/$',
        add_object,
        name='project-add-object'
    ),

    # Remove Object from Project
    re_path(
        r'^_remove-object/$',
        remove_object,
        name='project-remove-object'
    ),

    # Get Project Description by ID
    re_path(
        r'^(?P<proj_id>\d+)/description/$',
        get_project_description,
        name="project-description"
    ),

    # Get Project Transcription List by ID
    re_path(
        r'^(?P<proj_id>\d+)/list/transcription/$',
        get_project_transcription,
        name="project-transcription-list"
    ),

    # Get Project Primary Bibliography List by ID
    re_path(
        r'^(?P<proj_id>\d+)/list/littprim/$',
        get_project_bibliography,
        {'litt_type': 'p'},
        name="project-littprim-list"
    ),

    # Get Project Secondary Bibliography List by ID
    re_path(
        r'^(?P<proj_id>\d+)/list/littsec/$',
        get_project_bibliography,
        {'litt_type': 's'},
        name="project-littsec-list"
    ),
]
