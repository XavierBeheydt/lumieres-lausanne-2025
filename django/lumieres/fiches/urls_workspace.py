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
from django.urls import path, re_path
from fiches.views import workspace, workspace_collections

urlpatterns = [
    # Main workspace view
    path('', workspace, name='workspace-main'),

    # Collections: root view
    path('collections/', workspace_collections, {'coll_id': None, 'coll_slug': None}, name='workspace-collection-index'),

    # Collections: with ID (integer)
    path('collections/<int:coll_id>/', workspace_collections, name='workspace-collection'),

    # Collections: with slug (alphanumeric + dashes/underscores)
    re_path(r'^collections/(?P<coll_slug>[a-zA-Z0-9-][a-zA-Z0-9_-]+)/$', workspace_collections, name='named-workspace-collection'),
]
