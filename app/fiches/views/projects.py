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
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from fiches.models import *
from django.views.decorators.csrf import csrf_exempt
from fiches.templatetags.collector import editable_projects

from django.apps import apps

from django.db.models import Q


def index_project(request, proj_slug=None):
    q = Q()
    if request.user.is_authenticated:
        if not request.user.has_perm('fiches.view_unpublished_project'):
            q = q & (
                Q(publish=True) |
                Q(members=request.user) |
                Q(access_groups__users=request.user) |
                Q(access_groups__groups__user=request.user)
            )
    else:
        q = q & Q(publish=True)
    
    project_list = Project.objects.filter(q).distinct()

    opened_project = None
    if proj_slug is not None:
        project = Project.objects.get(url=proj_slug)
        if project is not None:
            opened_project = project.id
    
    context = {'project_list': reversed(project_list), 'opened_element': opened_project}
    return render(request, 'fiches/display/project_index.html', context)



def display_project(request, proj_id=None, proj_slug=None):
    project = None
    if proj_id is not None:
        try:
            project = Project.objects.get(pk=proj_id)
        except Project.DoesNotExist:
            project = None
    
    if project is None:
        project = get_object_or_404(Project, url=proj_slug)
    
    if not (
            project.publish or (
                request.user.is_authenticated() and (
                    request.user.has_perm('fiches.view_unpublished_project') or
                    project.is_editable(request.user)
                )
            )
        ):
        return HttpResponseForbidden(u"Accès non autorisé")

    
    
    lit_prim = project.bibliographies.filter(litterature_type='p').exclude(document_type__id=5).order_by('document_type__id', 'first_author')
    lit_sec = project.bibliographies.filter(litterature_type='s').order_by('document_type__id', 'first_author')    
    transcriptions = project.get_transcriptions(request.user)
    
    ext_template = "".join(("fiches/display/display_base", request.COOKIES.get('layoutversion', "2"), ".html"))
    
    context = {
        'ext_template': ext_template,
        'proj': project,
        'lit_prim': lit_prim,
        'lit_sec': lit_sec,
        'transcriptions': transcriptions,
        'print': bool(request.GET.get('print')),
        'noprint_popup': bool(request.GET.get('w')),
    }
    
    template = 'fiches/print/project.html' if request.GET.get('print') else 'fiches/display/project.html'
    
    return render(request, template, context)


def get_project_description(request, proj_id=None):
    project = get_object_or_404(Project, pk=proj_id)
    
    if not (
            project.publish or (
                request.user.is_authenticated and (
                    request.user.has_perm('fiches.view_unpublished_project') or
                    project.is_editable(request.user)
                )
            )
        ):
        return HttpResponseForbidden(u"Accès non autorisé")
    
    lit_prim = project.bibliographies.filter(litterature_type='p').exclude(document_type__id=5).order_by('document_type__id', 'first_author')
    lit_sec = project.bibliographies.filter(litterature_type='s').order_by('document_type__id', 'first_author')    
    transcriptions = project.get_transcriptions(request.user)
    
    context = {
        'proj': project,
        'lit_prim': lit_prim,
        'lit_sec': lit_sec,
        'transcriptions': transcriptions,
    }
    
    return render(request, 'fiches/ajax/project_description.html', context)


def get_project_transcription(request, proj_id=None):
    """
    """
    
    project = get_object_or_404(Project, pk=proj_id)
    transcription_list = project.get_transcriptions(request.user)
    
    ordering = []
    orderby = request.GET.get("orderby", "d")
    if orderby == 'd':
        ordering.extend(['manuscript_b__date', 'manuscript_b__first_author'])
    elif orderby == 'a':
        ordering.extend(['manuscript_b__first_author', 'manuscript_b__date'])
    ordering.extend(['manuscript_b__title'])
    transcription_list = transcription_list.order_by(*ordering)
    
    nbitem = request.GET.get("nbitem", "20")
    try:
        nbitem = int(nbitem)
    except ValueError:
        nbitem = 20
    
    showTitle = request.GET.get("showTitle", False)
    
    context = {'transcription_list': transcription_list, 'nbitem': nbitem, 'orderby': orderby, 'showTitle': showTitle}

    return render(request, "fiches/list/project_transcription_list.html", context)



def get_project_bibliography(request, proj_id=None, litt_type='p'):
    """
    """
    
    project = get_object_or_404(Project, pk=proj_id)
    # box 'littérature primaire' displays all bibliographies except the manuscripts 
    # (they are shown in the transcriptions box).
    # box 'littérature secondaire' displays all the bibliographies.
    bibliography_list = project.bibliographies.filter(litterature_type=litt_type)
    if litt_type == 'p':
        bibliography_list = bibliography_list.exclude(document_type__id=5)
    
    ordering = []
    orderby = request.GET.get("orderby", "d")
    if orderby == 'd':
        ordering.extend(['date', 'first_author'])
    elif orderby == 'a':
        ordering.extend(['first_author', 'date'])
    ordering.extend(['title'])
    bibliography_list = bibliography_list.order_by(*ordering)
    
    nbitem = request.GET.get("nbitem", "20")
    try:
        nbitem = int(nbitem)
    except ValueError:
        nbitem = 20

    showTitle = request.GET.get("showTitle", False)
    
    context = {'bibliography_list': bibliography_list, 'nbitem': nbitem, 'orderby': orderby, 'litt_type': litt_type, 'showTitle': showTitle}

    return render(request, "fiches/list/project_bibliography_list.html", context)





@login_required
@csrf_exempt
def add_object(request):
    """
    Add an object to a project, 
    object and project specifications (id and type) are passed by POST variables
    """
    
    if not request.user.has_perm('fiches.change_project'):
        return
    
    def return_error(msg=""):
        return HttpResponseBadRequest('Error: %s' % msg)
    
    if request.method != 'POST':
        return return_error("method error")
    
    item_id   = request.POST.get('item_id','')
    item_type = request.POST.get('item_type','')
    proj_id   = request.POST.get('proj_id','')

    # Validation
    if not re.match(r'\d+', item_id) or not re.match(r'\d+', proj_id):
        return return_error("validation error")
    
    # Get the project
    try:
        project = Project.objects.get(pk=proj_id)
        request.session['cur_proj'] = proj_id
    except Project.DoesNotExist:
        return return_error("project error") 

    # Verify change permission
    if not project.is_editable(request.user):
        return return_error("project permission error")
    
    # Get the model of the object, given by item_type
    try:
        #model = models.get_model('fiches', item_type)
        model = apps.get_model('fiches', item_type)
    except LookupError:
        return return_error("item type error")
    
    # Get the object
    try:
        obj = model._default_manager.get(pk=item_id)
    except model.DoesNotExist:
        return return_error("object error")
    
    # Add the object to the collection
    #project.add_object(obj)
    if hasattr(project, 'add_object'):
        project.add_object(obj)
    
    # if model == Transcription:
    #     project.add_object(obj.manuscript_b)
    # Special case for Transcription
    if model == apps.get_model('fiches', 'Transcription'):
        if hasattr(project, 'add_object'):
            if hasattr(obj, 'manuscript_b'):
                project.add_object(obj.manuscript_b)
    
    return HttpResponse('ok', content_type="text/plain")


@login_required
def remove_object(request):
    """
    Remove an object from a project, 
    object and collection specifications (id and type) are passed by POST variables
    """
    
    if not request.user.has_perm('fiches.change_project'):
        return
    
    def return_error(msg=""):
        return HttpResponseBadRequest('Error: %s' % msg)
    
    if request.method != 'POST':
        return return_error("method error")
    
    item_id   = request.POST.get('item_id','')
    item_type = request.POST.get('item_type','')
    proj_id   = request.POST.get('proj_id','')
    
    
    # Validation
    if not re.match(r'\d+', item_id) or not re.match(r'\d+', proj_id):
        return return_error("validation error")
    
    
    # Get the model and the object, given by item_type and item_id
    try:
        model = models.get_model('fiches', item_type)
    except:
        return return_error("item type error")
    try:
        obj = model._default_manager.get(pk=item_id)
    except:
        return return_error("object error")
    
    # Get the project
    try:
        project = Project.objects.get(pk=proj_id)
        request.session['cur_proj'] = proj_id
    except Project.DoesNotExist:
        return return_error("project error") 
     
    project.remove_object(obj)
    
    return HttpResponse('ok', content_type="text/plain")
    
    
