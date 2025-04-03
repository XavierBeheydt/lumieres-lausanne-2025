# -*- coding: utf-8 -*-
#
#    Copyright (C) 2013 Florian Steffen
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
from fiches.views.publications import (
    finding_index,
    get_finding_description,
    last_transcriptions,
    conference_proceedings,
    studies_ll,
    seminars_and_memoirs,
    videos,
)

urlpatterns = [
    # Trouvailles with optional finding_id
    re_path(r'^trouvailles/(?:(?P<finding_id>\d+)/)?$', finding_index, name='finding-index'),
    
    # Trouvailles with specific finding_id
    path('trouvailles/<int:finding_id>/', finding_index, name='finding-display'),
    
    # Finding description
    path('trouvailles/<int:finding_id>/description/', get_finding_description, name="finding-description"),
    
    # Last transcriptions
    path('dernieres-transcriptions/', last_transcriptions, name="last-transcriptions"),
    
    # Conference proceedings
    path('actes-colloques/', conference_proceedings, name="conference-proceedings"),
    
    # Studies
    path('etudes/', studies_ll, name="studies-ll"),
    
    # Seminars and memoirs
    path('seminaires-memoires/', seminars_and_memoirs, name="seminars-and-memoirs"),
    
    # Videos
    path('videos/', videos, name="videos"),
]
