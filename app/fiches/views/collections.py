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
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError,\
    HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
import json
from django.contrib.auth.decorators import login_required

from fiches.models import *
from django.views.decorators.csrf import csrf_exempt
from fiches.templatetags.collector import editable_projects
from django.apps import apps
from fiches.forms import ObjectCollectionForm
from django.urls import reverse

def get_default_col_name(user):
    user_name = user.get_full_name() if user.get_full_name() else user.username
    return 'Collection de %s' % user_name


def get_coll(user, coll_id=None, create_if_none=False):
    coll = None
    if create_if_none and (coll_id is None or ObjectCollection.objects.filter(pk=coll_id).count() == 0):
        coll = ObjectCollection(owner=user, access_owner=user, name=get_default_col_name(user))
        coll.save()
    else:
        try:
            coll = ObjectCollection.objects.get(pk=coll_id)
        except:
            coll = None
    return coll


def get_user_coll_list(user, create_if_none=True):
    try:
        coll_list = user.objectcollections.all()
        if coll_list.count() == 0 and create_if_none:
            # Assure que collection utilisateur existe
            _ = get_coll(user, create_if_none=create_if_none )
            coll_list = user.objectcollections.all()
            
        coll_list = list(coll_list)
        return coll_list
    except:
        return None


def get_writable_shared_coll_list(user):
    coll_list = set()
    etitable_grps = user.usergroup_set.filter(objectcollections__isnull=False).exclude(objectcollections__owner=user).distinct()
    if etitable_grps.count() > 0:
        for g in etitable_grps:
            coll_list |= set(g.objectcollections.all())
    coll_list = sorted(list(coll_list))
    return coll_list


def get_editable_coll_list(user, create_if_none=True):
    coll_dict = {
        'user': get_user_coll_list(user, create_if_none=create_if_none),
        #'contrib':  user.get_profile().get_contrib_coll()
        'contrib':  user.profile.get_contrib_coll()
    }
    return coll_dict



@login_required
def index(request, coll_id=None, coll_slug=None, no_cache=False):
    if request.GET.get('w', None) is not None:
        return display_popup(request, coll_id=coll_id, coll_slug=coll_slug)
    
    user = request.user
    if coll_slug and not coll_id:
        try:
            coll = ObjectCollection.objects.get(slug=coll_slug)
            coll_id = coll.id
        except (ObjectCollection.DoesNotExist, ObjectCollection.MultipleObjectsReturned):
            coll_slug = None
            coll_id = None
    
    # If no id specified for the collection, try with the last collection stored in the session
    if coll_id is None:
        coll = get_coll(request.user, request.session.get('cur_coll'), False)
    else:
        coll = get_coll(request.user, coll_id, False)
    
    # If no collection can be found with the requested id -> 404
    if coll_id is not None and coll is None:
        raise Http404()
     
    # At this point if a user hasn't yet a collection, one will be created by the call to get_user_coll_list
    # After that call, if the collection list is still empty -> 404
    coll_list = get_user_coll_list(request.user)
    if not coll_list:
        raise Http404()
    
    # If we dont't have a current collection yet, select one and save it to the session
    if coll is None:
        coll = coll_list[0]
    request.session['cur_coll'] = coll.id

    # Get all UserGroups this user is member of    
    #user_groups = request.user.get_profile().get_usergroups()
    user_groups = request.user.profile.get_usergroups()
    
    # Access is granted if ACModel.user_access is True OR if the user is member of a change_group
    coll_change = (coll.owner == user) or bool( set(user_groups) & set(coll.change_groups.all()) )
    coll_access = (
        coll.owner == user or 
        user in coll.access_groups.all() or 
        user.groups.filter(id__in=coll.access_groups.values_list('id', flat=True)).exists()
    )
        
    #Shared collections
    try:
        shared_coll = ObjectCollection.objects.exclude(owner=request.user).filter(
            access_groups__in=user_groups
        ).distinct()
    except:
        shared_coll = None

    try:
        contrib_coll = ObjectCollection.objects.exclude(owner=request.user).exclude(access_private=True).filter(change_groups__in=user_groups).distinct()
    except:
        contrib_coll = None
    
    
    # response = render('fiches/collections/index.html',
    #                           { 'coll': coll,
    #                             'coll_access': coll_access,
    #                             'coll_change': coll_change,
    #                             'coll_list': coll_list,
    #                             'shared_coll': shared_coll,
    #                             'contrib_coll': contrib_coll,
    #                           },
    #                           context_instance=RequestContext(request)
    # )

    context = {
        'coll': coll,
        'coll_access': coll_access,
        'coll_change': coll_change,
        'coll_list': coll_list,
        'shared_coll': shared_coll,
        'contrib_coll': contrib_coll,
    }

    response = render(request, 'fiches/collections/index.html', context)

    if no_cache: 
        response['Cache-Control'] = 'no-cache'
    
    return response



@login_required
def tab_index(request, coll_id=None, coll_slug=None, no_cache=False):
    """
    Collection Index to be used inside a tab. For the workspace collection's tab
    """
    
    print("DEBUG: tab_index was called with coll_id =", coll_id)

    if request.GET.get('w', None) is not None:
        return display_popup(request, coll_id=coll_id, coll_slug=coll_slug)
    
    user = request.user
    if coll_slug and not coll_id:
        try:
            coll = ObjectCollection.objects.get(slug=coll_slug)
            coll_id = coll.id
        except (ObjectCollection.DoesNotExist, ObjectCollection.MultipleObjectsReturned):
            coll_slug = None
            coll_id = None
    
    # If no id specified for the collection, try with the last collection stored in the session
    if coll_id is None:
        coll = get_coll(request.user, request.session.get('cur_coll'), False)
    else:
        coll = get_coll(request.user, coll_id, False)
    
    # If no collection can be found with the requested id -> 404
    if coll_id is not None and coll is None:
        raise Http404()
     
    # At this point if a user hasn't yet a collection, one will be created by the call to get_user_coll_list
    # After that call, if the collection list is still empty -> 404
    coll_list = get_user_coll_list(request.user)
    if not coll_list:
        raise Http404()
    
    # If we dont't have a current collection yet, select one and save it to the session
    if coll is None:
        coll = coll_list[0]
    request.session['cur_coll'] = coll.id

    # Get all UserGroups this user is member of  
    #user_groups = request.user.get_profile().get_usergroups()
    user_groups = request.user.profile.get_usergroups()
    
    # Access is granted if ACModel.user_access is True OR if the user is member of a change_group
    coll_change = (coll.owner == user) or bool( set(user_groups) & set(coll.change_groups.all()) )
    coll_access = coll.user_access(user) or coll_change
    
    #Shared collections
    try:
        contrib_coll = ObjectCollection.objects.exclude(owner=request.user).exclude(access_private=True).filter(change_groups__in=user_groups).distinct()
    except:
        contrib_coll = None
    
    try:
        shared_coll = ObjectCollection.objects.exclude(owner=request.user).exclude(access_private=True).exclude(change_groups__in=user_groups).filter(access_groups__in=user_groups).distinct()
    except:
        shared_coll = None
    
    response = render(request,
                      'fiches/workspace/collection.html',
                      { 'coll': coll,
                        'coll_access': coll_access,
                        'coll_change': coll_change,
                        'coll_list': coll_list,
                        'shared_coll': shared_coll,
                        'contrib_coll': contrib_coll,
                      }
    )
    return response

@login_required
def display_popup(request, coll_id=None, coll_slug=None):
    coll = None

    if coll_id:
        coll = get_coll(request.user, coll_id, False)
    elif coll_slug:
        try:
            coll = ObjectCollection.objects.get(slug=coll_slug)
        except (ObjectCollection.DoesNotExist, ObjectCollection.MultipleObjectsReturned):
            coll = None

    if coll is None:
        raise Http404("Collection not found")
    
    # Determine access.
    # First, check using the existing logic.
    coll_access = coll.user_access(request.user) or coll.change_groups.filter(id__in=request.user.groups.all()).exists()
    # Force access if the current user is the owner.
    if coll.owner == request.user:
        coll_access = True

    return render(request, 'fiches/collections/display_popup.html', {
        'coll': coll,
        'coll_access': coll_access,
    })

@login_required
def get_user_list(request, format='select'):
    """
    Return the list of the collections that belongs to the current user
    """
    user_coll_list = get_user_coll_list(request.user)
    #shared_coll_list = request.user.get_profile().get_contrib_coll()
    shared_coll_list = request.user.profile.get_contrib_coll()
    
    current_collection = request.session.get('cur_coll','-1')
    if format == 'json':
        return HttpResponse(json.dumps([{'data':None}]), content_type='application/json')
    elif format == 'select':
        output = []
        if user_coll_list:
            if shared_coll_list: output.append('<optgroup label="Collections personnelles">')
            for c in user_coll_list:
                selected = ' selected="selected"' if c.id == current_collection else ''
                output.append('<option value="%s"%s>%s</option>\n' % (c.id, selected, c.name))
            if shared_coll_list: 
                output.append('</optgroup>')
                output.append(u'<optgroup label="Collections partagées">')
                for c in shared_coll_list:
                    selected = ' selected="selected"' if c.id == current_collection else ''
                    output.append('<option value="%s"%s>%s</option>\n' % (c.id, selected, c.name))
                output.append('</optgroup>')
        else:
            output.append('<option value="-1">Collection de %s</option>' % (
                          request.user.get_full_name() if request.user.get_full_name() else request.user.username,)
            )
        
        return HttpResponse("".join(output))
    else:
        return HttpResponse('not implemented yet')

@login_required
def get_in_collection_list(request):
    """
    Return the list of user accessible collections and projects the requested item belongs to
    """
    if ( request.GET['type'] == 'Person' ):
        collections = ObjectCollection.objects.filter(persons=request.GET['id'])
        projects = Project.objects.filter(persons=request.GET['id'])
    elif ( request.GET['type'] == 'Biblio' ):
        collections = ObjectCollection.objects.filter(bibliographies=request.GET['id'])
        projects = Project.objects.filter(bibliographies=request.GET['id'])
    elif ( request.GET['type'] == 'Transcription' ):
        collections = ObjectCollection.objects.filter(transcriptions=request.GET['id'])
        projects = Project.objects.filter(transcriptions=request.GET['id'])

    # filter out the collections/projects the user cannot access
    # accessible_coll = set(get_user_coll_list(request.user)) \
    #                   | set(request.user.get_profile().get_contrib_coll())
    accessible_coll = set(get_user_coll_list(request.user)) \
                      | set(request.user.profile.get_contrib_coll())
    collections = set(collections) & accessible_coll
    accessible_proj = editable_projects(request.user)
    projects = set(projects) & accessible_proj

    content = { 'incollection': ', '.join(c.name for c in collections), 
                'inproject': ', '.join(p.name for p in projects) }
        
    return HttpResponse(json.dumps(content), content_type="application/json")

@login_required
@csrf_exempt
def add_object(request):
    """
    Add an object to a collection, 
    object and collection specifications (id and type) are passed by POST variables
    """
    def return_error(msg=""):
        return HttpResponseBadRequest('Error: %s' % msg)
    
    if request.method != 'POST':
        return return_error("method error")
    
    item_id   = request.POST.get('item_id','')
    item_type = request.POST.get('item_type','')
    coll_id   = request.POST.get('coll_id','')
    
    # Get the model of the object, given by item_type
    # try:
    #     model = models.get_model('fiches', item_type)
    # except:
    #     return return_error("item type error")
    try:
        model = apps.get_model('fiches', item_type)
        if model is None:
            raise ValueError(f"Model for item_type '{item_type}' not found.")
    except Exception as e:
        return return_error(f"item type error: {str(e)}")
    
    # Validation
    if not re.match(r'\d+', item_id) or not re.match(r'-?\d+', coll_id):
        return return_error("validation error")

    # Get the collection, 
    # if the coll_id is -1, use the first existing collection of the user or create a new one.
    try:
        coll_id = int(coll_id)
        if coll_id == -1:
            if ObjectCollection.objects.filter(owner=request.user).count() == 0:
                user_name = request.user.get_full_name() if request.user.get_full_name() else request.user.username
                coll = ObjectCollection(owner=request.user, name='Collection de %s' % user_name)
                coll.save()
            else:
                coll = ObjectCollection.objects.filter(owner=request.user)[0]
        else:
            coll = ObjectCollection.objects.get(pk=coll_id)
        coll_id = coll.id
        request.session['cur_coll'] = coll_id
    except:
        return return_error("collection error")
    
    # Verify change permission
    #can_change_coll = (coll.owner == request.user) or ( request.user.usergroup_set.all() & coll.change_groups.all() )
    #can_change_coll = (coll.owner == request.user) or ( request.user.get_profile().get_contrib_coll().filter(pk=coll.id) )
    can_change_coll = (coll.owner == request.user) or ( request.user.profile.get_contrib_coll().filter(pk=coll.id) )
    if not can_change_coll:
        return return_error("collection permission error")
    
    # Get the object
    try:
        obj = model._default_manager.get(pk=item_id)
    #except:
    except model.DoesNotExist:
        return return_error("object error")
    
    # Add the object to the collection
    coll.add_object(obj)
    
    return HttpResponse('ok', content_type="text/plain")
    
    
@login_required
def remove_object(request):
    """
    Remove an object from a collection, 
    object and collection specifications (id and type) are passed by POST variables
    """
    def return_error(msg=""):
        return HttpResponse('Error: %s' % msg, status=500)
    
    if request.method != 'POST':
        return return_error("method error")
    
    item_id   = request.POST.get('item_id','')
    item_type = request.POST.get('item_type','')
    coll_id   = request.POST.get('coll_id','')
    
    
    # Validation
    if not re.match(r'\d+', item_id) or not re.match(r'\d+', coll_id):
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
    
    
    # Get the collection
    try:
        coll = ObjectCollection.objects.get(pk=coll_id)
    except:
        return return_error("collection not found error")
    
    #can_change_coll = (coll.owner == request.user) or ( request.user.usergroup_set.all() & coll.change_groups.all() )
    #can_change_coll = (coll.owner == request.user) or ( request.user.get_profile().get_contrib_coll().filter(pk=coll.id) )
    can_change_coll = (coll.owner == request.user) or ( request.user.profile.get_contrib_coll().filter(pk=coll.id) )
    if not can_change_coll:
        return return_error("collection permission error")
    
    coll.remove_object(obj)
    
    return HttpResponse('ok', content_type="text/plain")
    


@login_required
def display(request, coll_id):
    coll = get_object_or_404(ObjectCollection, pk=coll_id)
    coll_access = coll.user_access(request.user) or ( request.user.usergroup_set.all() & coll.change_groups.all() )
    # response = render('fiches/collections/display.html',{
    #                             'coll': coll,
    #                             'coll_access': coll_access,
    #                             }, context_instance=RequestContext(request)
    # )

    context = {
        'coll': coll,
        'coll_access': coll_access,
    }
    
    response = render(request, 'fiches/collections/display.html', context)
    response['Cache-Control'] = 'no-cache'
    return response


@login_required
def short_info(request, coll_id):
    """
    Display a short information about the collection containing
    - description
    - group access
    """
    coll = get_object_or_404(ObjectCollection, pk=coll_id)
    # return render('fiches/collections/shortinfo.html',
    #                           { 'coll': coll },
    #                           context_instance=RequestContext(request)
    # )
    return render(request, 'fiches/collections/shortinfo.html', { 'coll': coll })



@login_required
def edit(request, coll_id=None, create_coll=False, coll_saved=False):
    """
    Edit the collection's attributes.
    Create a new collection if create_coll is defined.
    """
    edit_done_js_callback = request.GET.get('callback', 'collection.edit_done')
    
    if coll_id == '#': 
        coll_id = -1
    
    if create_coll:
        coll = ObjectCollection(owner=request.user, access_owner=request.user)
    else:
        coll = get_object_or_404(ObjectCollection, pk=coll_id)
    
    if request.method == 'POST':
        collForm = ObjectCollectionForm(request.POST, instance=coll)
        if collForm.is_valid():
            coll = collForm.save()
            request.session['cur_coll'] = coll.id
            return HttpResponseRedirect(
                reverse('collection-saved', kwargs={'coll_id': coll.id}) +
                '?callback=' + edit_done_js_callback
            )
        else:
            # Log the form errors for debugging purposes.
            print("Form errors:", collForm.errors)
    else:
        collForm = ObjectCollectionForm(instance=coll)
    
    response = render(request, 'fiches/collections/edit.html', {
        'form': collForm,
        'coll_id': coll_id,
        'coll_saved': coll_saved,
        'edit_done_js_callback': edit_done_js_callback
    })

    response['Cache-Control'] = 'no-cache'
    return response

    
@login_required
def saved(request):
    return HttpResponse('Saved')


@login_required
def delete(request, coll_id):
    """
    Remove the collection.
    """
    coll = get_object_or_404(ObjectCollection, pk=coll_id)
    
    if coll.owner != request.user:
        return HttpResponseForbidden(u"Seul le propriétaire de la collection est autorisé à la supprimer.")
    
    try:
        coll.delete()
    except Exception as e:
        return HttpResponseServerError(u"Problème lors de la suppression de la collection: " + str(e))
    
    # Redirect to the workspace home page.
    # Option 1: If you have a named URL for workspace home:
    return HttpResponseRedirect(reverse('workspace-main'))
    
    # Option 2: Hardcode the URL (uncomment the line below if you prefer)
    # return HttpResponseRedirect('/espace_de_travail')

    
    
    
