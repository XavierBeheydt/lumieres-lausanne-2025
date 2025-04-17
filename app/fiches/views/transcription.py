# -*- coding: iso-8859-1 -*-
#
#    Copyright (C) 2010-2012 Universit� de Lausanne, RISET
#    < http://www.unil.ch/riset/ >
#
#    This file is part of Lumi�res.Lausanne.
#    Lumi�res.Lausanne is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Lumi�res.Lausanne is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    This copyright notice MUST APPEAR in all copies of the file.
#
from base64 import b64decode
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotFound,\
    HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.forms.models import modelformset_factory, inlineformset_factory
import json
from itertools import groupby
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import never_cache
from django.db.models import Q

from utils import dbg_logger
from fiches.models import *
from fiches.utils import query_fiche, get_last_model_activity, log_model_activity, supprime_accent, update_object_index
from utils.aggregates import Concatenate
from urllib.parse import quote as urlquote
from fiches.models.documents import NoteTranscription


#==============================================================================#
#----------- TRANSCRIPTION ----------------------------------------------------#
#==============================================================================#
FICHE_TYPE_NAME = 'Transcription'

DISPLAY_COLLECTOR = True
def index(request):
    return HttpResponseRedirect(''.join((reverse('search-biblio'), '?dtT=1&cl1=1&cl3=1&cl4=1')))

    
def display(request, trans_id):
    trans = get_object_or_404(Transcription, pk=trans_id)
    trans_user_access = (
        request.user.has_perm('fiches.access_unpublished_transcription') or
        trans.user_access(request.user)
    )
    last_activity = get_last_model_activity(trans)
    
    note_qs = NoteTranscription.objects.filter(owner=trans)
    if request.user.is_authenticated and not request.user.is_staff:
        note_qs = note_qs.filter(
            models.Q(access_public=True) |
            models.Q(access_owner=request.user) |
            (
                models.Q(access_groups__isnull=True) |
                models.Q(access_groups__in=request.user.usergroup_set.all())
            )
        ).distinct()
    
    context = {
        'trans': trans,
        'last_activity': last_activity,
        # 'man': trans.manuscript,  # If unused, remove or uncomment if needed
        'model': Transcription,
        'trans_user_access': trans_user_access,
        'display_collector': DISPLAY_COLLECTOR,
        'note_qs': note_qs,
    }
    
    ext_template = f"fiches/display/display_base{request.COOKIES.get('layoutversion', '2')}.html"
    context.update({'ext_template': ext_template})
    
    return render(request, 'fiches/display/transcription.html', context)



@permission_required(perm='fiches.add_transcription')
def create(request, man_id=None, doc_id=None):
    if not (bool(man_id) ^ bool(doc_id)):
        return HttpResponseBadRequest("one and only one of 'man_id', 'doc_id' is required")
    return edit(request, man_id=man_id, doc_id=doc_id, trans_id=None, new_trans=True)


@permission_required(perm='fiches.delete_transcription')
def delete(request, trans_id):
    trans = get_object_or_404(Transcription, pk=trans_id)
    if trans.manuscript_b:
        response = HttpResponseRedirect(reverse('display-bibliography', args=[trans.manuscript_b.id]))
    else:
        response = HttpResponseServerError("no manuscript for this transcription")
    trans.delete()
    return response


@never_cache
@permission_required(perm='fiches.change_transcription')
def edit(request, trans_id=None, man_id=None, doc_id=None, new_trans=False, del_trans=False):
    
    if new_trans:
        man   = get_object_or_404(Manuscript, pk=man_id) if man_id else None
        doc   = get_object_or_404(Biblio, pk=doc_id) if doc_id else None
        trans = Transcription(manuscript_b=doc, author=request.user, access_owner=request.user, access_public=False)
        trans.access_owner = request.user
    else:
        trans = get_object_or_404(Transcription, pk=trans_id)
        doc       = trans.manuscript_b
    
    last_activity = get_last_model_activity(trans)
    
    context = { 'model': Transcription }
    
    trans_user_access = new_trans or request.user.has_perm('fiches.access_unpublished_transcription') or trans.user_access(request.user)
    access_public_original = trans.access_public
    
    # user needs the publish_transcription permission to modify a published transcription
    if trans.access_public and not request.user.has_perm('fiches.publish_transcription'):
        return HttpResponseForbidden(u"Vous ne disposez pas des permissions n�cessaires pour modifier une transcription publi�e")
    
    NoteFormset = inlineformset_factory(Transcription, NoteTranscription, extra=0, form=NoteFormTranscription)
    def get_notetransformset_qs(bio):
        note_qs = NoteTranscription.objects.filter(owner=bio)
        if not request.user.is_staff:
            note_qs = note_qs.filter(models.Q(access_owner = request.user) |
                ( models.Q(access_groups__isnull = True) |
                  models.Q(access_groups__in     = request.user.usergroup_set.all()) )).distinct()
        if not request.user.has_perm('fiches.can_publish_note'):
            note_qs = note_qs.filter(~models.Q(access_public = True)).distinct()
        return note_qs
    
    if request.method == 'POST':
        transForm   = TranscriptionForm(request.POST, instance=trans)
        if not request.user.has_perm('fiches.change_transcription_ownership') :
            formData = transForm.data.copy()
            formData.update({u'author': u"%s" % (trans.author.id)})
            formData.update({u'author2': u"%s" % (trans.author2.id) if trans.author2 else None})
            transForm.data = formData
        
        noteFormset = NoteFormset(request.POST, instance=trans, queryset=get_notetransformset_qs(trans))
        if transForm.is_valid():
            trans = transForm.save(commit=False)
            trans.access_owner = trans.author
            if not request.user.has_perm('fiches.publish_transcription'):
                trans.access_public = access_public_original
            trans.save()
            transForm.save_m2m()
            
            # Write to the activity log
            log_model_activity(trans, request.user)
            
            # Update global search index (haystack)
            update_object_index(trans)
            
            noteFormset = NoteFormset(request.POST, instance=trans, queryset=get_notetransformset_qs(trans))
            if noteFormset.is_valid():
                noteFormset.save()
                if request.POST.get('__continue', '') == 'on':
                    url = reverse('transcription-edit', args=[trans.id])
                    #if ( request.REQUEST.get('__position') ):
                    if ( request.GET.get('__position') ):
                        #url += "?__position=" + urlquote(request.REQUEST.get('__position'))
                        url += "?__position=" + urlquote(request.GET.get('__position'))
                    return HttpResponseRedirect(url)
                else:
                    return HttpResponseRedirect(reverse('transcription-display', args=[trans.id]))
            else:
                # noteFormset invalid
                dbg_logger.debug("noteFormset invalid")
        else:
            # transForm invalid
            dbg_logger.debug("transForm invalid: %s" % transForm.errors)
            
    else:
        # Dealing with GET
        transForm   = TranscriptionForm(instance=trans)
        noteFormset = NoteFormset(instance=trans, queryset=get_notetransformset_qs(trans))
    
    if not trans_user_access:
        raise Http404()
    
    public_notes = None
    if trans is not None and not request.user.has_perm("fiches.can_publish_note"):
        public_notes = NoteTranscription.objects.filter(owner=trans).filter(access_public = True)
        
    context.update({
       'transcription': trans,
       'last_activity': last_activity,
       'new_object': new_trans,
       'transForm': transForm,
       'noteFormset': noteFormset,
       'publicNotes': public_notes,
       #'savedPosition': request.REQUEST.get('__position', '')
       'savedPosition': request.GET.get('__position', '')
    })
    
    ext_template = "".join(("fiches/edition/edit_base", request.COOKIES.get('layoutversion', "2"), ".html"))
    context.update({'ext_template': ext_template})
    
    return render(request, 'fiches/edition/transcription.html', context)



