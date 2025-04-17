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
from django.db import models
from django.shortcuts import render, get_object_or_404
from fiches.models import Finding, FreeContent
from fiches.models.documents import Transcription


from django.shortcuts import render
from django.db.models import Q
from fiches.models import Finding

def finding_index(request, finding_id=None):
    # Check if the user is authenticated and has the required permission
    if request.user.is_authenticated and request.user.has_perm('fiches.change_finding'):
        q = Q()
    else:
        q = Q(published=True)  # Filter for published findings if the user lacks permission

    # Fetch the findings based on the query
    findings = Finding.objects.filter(q)

    # Prepare the context for the template
    context = {'elements': findings, 'opened_element': finding_id}
    
    # Render the template with the context
    return render(request, 'fiches/display/thumbnail_detail_view.html', context)


def get_finding_description(request, finding_id):
    finding = get_object_or_404(Finding, pk=finding_id)

    context = { 'finding': finding }

    return render(request, 'fiches/ajax/finding_description.html', context)

def last_transcriptions(request):
    """
    Last published transcriptions page
    """

    content = FreeContent.objects.get_content("publications>last_transcriptions")
    transcriptions = Transcription.objects.last_published(15)

    context = { "content": content, "last_transcriptions": transcriptions }
    return render(request, "fiches/publications/last_transcriptions.html", context)

def conference_proceedings(request):
    """
    Conference proceedings page
    """
    content = FreeContent.objects.get_content("publications>proceedings")
    context = { "content": content }
    return render(request, "fiches/publications/proceedings.html", context)

def studies_ll(request):
    """
    Studies LL page
    """
    content = FreeContent.objects.get_content("publications>studies_ll")
    context = { "content": content }
    return render(request, "fiches/publications/studies.html", context)

def seminars_and_memoirs(request):
    """
    Seminars and memoirs publications page
    """
    content = FreeContent.objects.get_content("publications>seminars")
    context = { "content": content }
    return render(request, "fiches/publications/seminars.html", context)

def videos(request):
    """
    Videos pages
    """
    content = FreeContent.objects.get_content("publications>videos")
    context = { "content": content }
    return render(request, "fiches/publications/videos.html", context)
