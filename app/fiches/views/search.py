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
import datetime
import calendar
from base64 import b64decode
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
import json
from django.utils.encoding import smart_str
from django.db import models
from utils import dbg_logger
from fiches.models import *
from django.db.models.query import EmptyQuerySet
from django.core.paginator import Paginator, InvalidPage
from fiches.models import UserGroup, ActivityLog, Person
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required

from django.urls import path


from fiches.models.documents.document import Transcription, Biblio
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.apps import apps

from haystack.views import SearchView
#from django.views import View


from django.views.generic import View

from fiches.forms import FichesSearchForm

from fiches.models.search.search import BiblioExtendedSearchForm
#from fiches.models import Journal

def search_index(request):
    """
    This view is used to direct the user to the last kind of search used
    Now, the default is to do a __general__ seaarch (before was Biblio)
    """
    last_type = request.session.get('search_last_type', '__general__')
    if last_type not in ('Person', 'Biblio', '__general__'):
        last_type = '__general__'
    if last_type == '__general__':
        return search_general(request)
    else:
        return filter_builder(request, model_name=last_type)



def search_general(request):
    return render(request, 'fiches/search/search_general.html')




def biblio_extended_search(request):
    user = request.user
    context = {'display_collector': True}
    
    if user.is_authenticated:
        if user.has_perm('fiches.view_unpublished_project'):
            BiblioExtendedSearchForm.base_fields['proj'].queryset = Project.objects.all()
        else:
            BiblioExtendedSearchForm.base_fields['proj'].queryset = Project.objects.filter(
                models.Q(publish=True) | models.Q(members=request.user)
            ).distinct()
    
    doSearch = len(request.GET) > 0
    if doSearch:
        # Update Querydict with initial values defined in the Form
        get_dict = request.GET.copy()
        for fld_name, fld in BiblioExtendedSearchForm.base_fields.items():
            if fld.__getattribute__('initial'):
                get_dict.setdefault(fld_name, fld.initial)
        form = BiblioExtendedSearchForm(get_dict)
    else:
        form = BiblioExtendedSearchForm()
    context.update({'form': form})
    
    #search_action=request.REQUEST.get('search_action', None)
    search_action=request.GET.get('search_action', None)
        
    if doSearch and form.is_valid():
        cd = form.cleaned_data
        q = models.Q()
        
        def q_op(q, q1, op):
            if op == 'or':
                q = q | q1
            elif op == 'and':
                q = q & q1
            else:
                q = q & ~q1
            return q
        
        
        # Expressions
        # @todo: pour les champs, traiter séparément chaque cas pour pouvoir faire des Q
        #        combiné pour 'title', p.ex comme ça on peut chopper title, book_title, revue_title, etc...
        # @note: 14.02.2012 JF: modifié pour pouvoir mettre des tuple de nom de champs, effectue recherche dans tous les champs
        
        fld_map = { 
           'title': ('title', 'short_title', ), 
           'authors': 'contributiondoc__person__name',
           'person': 'subj_person__name',
           'place': 'place',
           'edit': 'publisher'
        }
        for xidx in range(4):
            # val, op, fld = (
            #                cd.get('x%d_val' % xidx), 
            #                cd.get('x%d_op' % xidx, 'and'), 
            #                fld_map.get( cd.get('x%d_fld' % xidx))
            #                )
            val = cd.get('x%d_val' % xidx)
            op = cd.get('x%d_op' % xidx, 'and')
            fld = fld_map.get(cd.get('x%d_fld' % xidx))
    
            if type(fld) != tuple:
                fld = (fld,)
            if val:
                q1 = Q(**{"%s__icontains" % fld[0]: val})
                for f in fld[1:]:
                    q1 |= Q(**{"%s__icontains" % f: val})
                    
                q = q_op(q, 
                         q1 = q1, 
                         op = op
                )
            
        
        # Doctype
        doctype = cd.get('dt')
        # Dirty trick to select only Manuscript with Transcription
        # @TODO: define variables in settings for the id of the DocumentTypes (DOCTYPE_MANUSCRIPT_ID instead of 5)
        DOCTYPE_MANUSCRIPT_ID = 5
        onlyTrans = request.GET.get('dtT')
        if onlyTrans == "1":
            context.update({'onlyTrans': onlyTrans})
            if not doctype:
                doctype = DocumentType.objects.filter(pk=DOCTYPE_MANUSCRIPT_ID)
        
        if doctype:
            print ("search biblio_extended_search() called")
            if onlyTrans != "1":
                # Normal doctype filtering
                q = q & Q(document_type__in=doctype)

            else:
                # Only Manuscript with transcription
                doctype = doctype.exclude(id=DOCTYPE_MANUSCRIPT_ID)  # Remvove Manuscript from selected doctypes)
                
                # Transcription filter
                q_trans = Q(transcription__isnull=False)
                
                # Note that users with the `perm:view_unpublished_project` that are *not* member
                # of the project and doesn't have the `perm:access_unpublished_transcription`,
                # those users won't see results from unpublished transcription.
                # Future will tells if it is a problem or not.
                if not user.is_authenticated:
                    q_trans = q_trans & Q(transcription__access_public=True)
                elif not user.has_perm('fiches.access_unpublished_transcription'):
                    q_trans = q_trans & (
                                Q(transcription__access_public=True) |
                                ( Q(transcription__author=user) |
                                  Q(transcription__author2=user) | 
                                  Q(transcription__access_groups__users=user) | 
                                  Q(transcription__access_groups__groups__user=user) |
                                  Q(transcription__project__members=user) |
                                  ( models.Q(transcription__access_public=False) 
                                    & models.Q(transcription__access_private=False) 
                                    & models.Q(transcription__access_groups__isnull=True)
                                  )
                                )
                            )
                
                # Select all selected doctypes and Manuscript with transcription
                q = q & ( Q(document_type__in=doctype) | (Q(document_type__id=DOCTYPE_MANUSCRIPT_ID) & q_trans) ) 
        
        if onlyTrans != "1":
            user_accessible_trans = Transcription.user_accessible_list(user)
        else:
            user_accessible_trans  = True
        context.update({'user_accessible_trans': user_accessible_trans or [-1]})
        
        
        # Date. Applied only if at least one of `date_from`, `date_to` is defined  
        if cd.get('date_from') or cd.get('date_to'):
            
            date_from_y, date_from_m = (str(cd.get("date_from","")).split('.') + [''])[:2]
            try:
                date_from_y = int(date_from_y)
            except ValueError:
                date_from_y = None
            try:
                date_from_m = int(date_from_m)
                if not 0 < date_from_m < 13: date_from_m = None
            except ValueError:
                date_from_m = None
            date_from = datetime.date(date_from_y or 1, date_from_m or 1, 1)   # If no date_from, default to year 1 ( loooong time ago )

            
            date_to_y, date_to_m = (str(cd.get("date_to","")).split('.') + [''])[:2]
            # If no date_from, default to year 9999
            try:
                date_to_y = int(date_to_y) or 9999
            except ValueError:
                date_to_y = 9999
            try:
                date_to_m = int(date_to_m) or 12
                if not 0 < date_to_m < 13: date_to_m = 12
            except ValueError:
                date_to_m = 12
            date_to   = datetime.date(date_to_y, date_to_m, calendar.monthrange(date_to_y, date_to_m)[1])

            #date_from = datetime.date(cd.get('date_from') or 1, 1, 1)   # If no date_from, default to year 1 ( loooong time ago )
            #date_to   = datetime.date(cd.get('date_to') or 9999, 12, 31)   # If no date_from, default to year 9999 ( loooong time from now )
            q = q & Q(date__range=(date_from, date_to))
            
        # Modification date. Applied only if at least one of `mdate_from`, `mdate_to` is defined  
        if cd.get('mdate_from') or cd.get('mdate_to'):
            mdate_from = cd.get("mdate_from")
            if not mdate_from:
                mdate_from = datetime.date(1, 1, 1)
            mdate_to   = cd.get("mdate_to")
            if not mdate_to:
                mdate_to = datetime.date(9999, 1, 1)
            
            biblio_ids_from_log = ActivityLog.objects.filter(model_name='Biblio', date__range=(mdate_from, mdate_to))\
                                 .values_list('object_id', flat=True)
            trans_ids_from_log = ActivityLog.objects.filter(model_name='Transcription', date__range=(mdate_from, mdate_to))\
                                 .values_list('object_id', flat=True)
            q = q & (Q(pk__in=list(biblio_ids_from_log)) | Q(transcription__pk__in=list(trans_ids_from_log)))
                
        # Language.
        if cd.get('l'):
            q = q & (Q(language=cd.get('l')) | Q(language_sec=cd.get('l')))
        
        # Lieu de dépôt
        depot = cd.get('depot')
        if depot:
            q = q & Q(depot=depot)
        
        # Literature Type
        ltype = cd.get('ltype')
        if ltype:
            q = q & Q(litterature_type__in=ltype)
        
        
        # Projects
        proj = cd.get('proj')

        if proj:
            q = q_op(q, 
                     q1 = Q(project__in=proj), 
                     op = cd.get('proj_op', 'and')
            )
            if cd.get('proj_op', 'and') == 'and':
                q = q & Q(project__isnull=False)

        # Journal
        journal = cd.get('journal')
        if journal:
            q = q & Q(journal_title=journal)

        # society
        society = cd.get('society')
        if society:
            q = q & Q(subj_society=society)
        
        # manuscript type
        mtype = cd.get('mtype')
        if mtype:
            q = q & Q(manuscript_type=mtype)
        
        ### Filter Results
        dbg_logger.debug(q)
        if q.children:
            results = Biblio.objects.filter(q).order_by('document_type')
        else:
            results = Biblio.objects.all()
        
        
        # Mot-cles, needs to chain filters, so evaluate other filters first
        kw_filter_applied = False
        for xidx in range(4):
            op, pkw, skw = (cd.get('kw%d_op' % xidx, 'and'),
                            cd.get('kw%d_p' % xidx), 
                            cd.get('kw%d_s' % xidx))
            if skw:
                kw_filter_applied = True
                if op == 'and':
                    results = results.filter(subj_secondary_kw=skw)
                elif op == 'or':
                    results = results | results.filter(subj_secondary_kw=skw)
                elif op == 'not':
                    results = results.exclude(subj_secondary_kw=skw)

            elif pkw:
                kw_filter_applied = True
                kw_q = Q(subj_primary_kw=pkw) # | Q(subj_secondary_kw__parent=pkw)  ## This works but is also a performence killer
                if op == 'and':
                    results = results.filter(subj_primary_kw=pkw)
                elif op == 'or':
                    results = results | results.filter(subj_primary_kw=pkw)
                elif op == 'not':
                    results = results.exclude(subj_primary_kw=pkw)

        if not q.children and not kw_filter_applied:
            #results = EmptyQuerySet()
            results = Biblio.objects.none()
        
        
        # Grouping and sorting
        sort_map = {
            'a': 'first_author_name',
            'd': 'date',
            '-d': '-date',
            't': 'title',
        }
        
        # Sort according to grouping (first sort, then group)
        grp = cd.get('grp', 'd')
        if (grp == 'd'):
            sort_fields = ['document_type', 'first_author_name']
            context.update({'grpby_1': "doctype", 'grpby_2': "author"})
        elif grp == 'a':
            sort_fields = ['first_author_name', 'document_type']
            context.update({'grpby_1': "author", 'grpby_2': "doctype"})
        else:
            sort_fields = []
            
            
        # Add sorting choice, default to `date`
        sort_fields.append(sort_map.get(cd.get('sort'),'date'))
        sort_fields.append('pages')
        # Apply ordering to qs
        results = results.distinct().order_by(*sort_fields)
        
        if search_action == None:
            paginator = Paginator(results, int(cd.get('nbi') or 25))
            try:
                page = paginator.page(request.GET.get('page', 1))
            except InvalidPage:
                raise Http404
            
            
            context.update({
                'page': page,
                'paginator': paginator,
                'qs': request.META['QUERY_STRING'].replace('&page=%d'%page.number, ''),
            })
        else:
            #qs = request.META['QUERY_STRING'].replace('&page=%d'%request.GET.get('page', 1), '')
            qs = request.META['QUERY_STRING'].replace('&page=%d'%int(request.GET.get('page', 1)), '')
            context.update({
                'results': results,
                'usergroups': UserGroup.objects.all().order_by('name'),
                'qs': qs,
                'qswoaction': qs.replace('search_action=' + search_action + '&', ''),
            })
        
        
    if search_action == 'trans_access':
        return render(request, 'fiches/search/actions/trans_access.html', context)
    else:
        return render(request, 'fiches/search/biblio_extended.html', context)



RESULT_DISPLAY_COLUMNS = {
    'Person': {
        'name':      'on',
        'relation':  'on',
        'prof':      'auto',
        'birth':     'auto',
        'death':     'auto',
        'society':   'auto',
        'religion':  'auto',
        'journal_articles':   'auto',
    }
}


def filter_builder(request, model_name='Person', sfid=None):
    request.session['search_last_type'] = model_name
    
    context = {'fiche_type': 'search', 'model_name': model_name, 'journals': JournaltitleView.objects.all()}
    if model_name.lower() == 'person':
        context.update({
            'societies': Society.objects.all(),
        })
    elif model_name.lower() == 'biblio':
        context.update({
            'doctypes': DocumentType.objects.all()
        })
    
    if request.session.get('display_settings') is None:
        request.session['display_settings'] = RESULT_DISPLAY_COLUMNS.copy()
    display_columns = request.session['display_settings'].get(model_name,{})
    
    context.update({'display_settings': display_columns, 'display_collector': True})
    
    ext_template = "".join(("fiches/search/search_base", request.COOKIES.get('layoutversion', "2"), ".html"))
    context.update({'ext_template': ext_template})
    
    return render(request, 'fiches/search/filters_%s.html' % model_name.lower(), context)




def do_search(request):
    
    def get_Q(params):
        q = models.Q()
        for p in params:
            if p['type']=='date' and p['op'] in ('lt','gt'):
                try:
                    if p['op']=='lt':
                        p['val'] = datetime.date(int(p['val']), 12, 31)
                    else:
                        p['val'] = datetime.date(int(p['val']), 1, 1)
                except ValueError:
                    continue
            
            if p['type']=='number':
                try:
                    p['val'] = int(p['val'])
                except ValueError:
                    continue
            
            #if type(p['val']) in (str, unicode): p['val'] = smart_str(p['val'])
            if isinstance(p['val'], str):
                p['val'] = smart_str(p['val'])
            
            if p['op'] == 'isnull':
                p['val'] = bool(p['val'])
            
            if not p['attr'].startswith('subject'):
                q = q & models.Q(**{
                            smart_str("%s__%s"%(p['attr'],p['op'])): p['val']
                        })
                
            else:
                field_list = ('title', 'subj_primary_kw__word', 'subj_secondary_kw__word', 'subj_person__name')
                if p['attr'] == 'subjecta':
                    try:
                        raw_val = p['val']
                        p['val'] = b64decode(raw_val.split('|')[0])
                        field_list = raw_val.split('|')[1].split(',')
                    except:
                        p['val'] = ""
                        field_list = []
                for f in field_list:
                    q = q | models.Q(**{ '%s__icontains'%f: p['val'] })
                
#                q = models.Q(                               
#                    models.Q(title__icontains=p['val']) |
#                    models.Q(subj_primary_kw__word__icontains=p['val']) |
#                    models.Q(subj_secondary_kw__word__icontains=p['val']) |
#                    models.Q(subj_person__name__icontains=p['val'])
#                )
            
        return q
    
    q = request.GET.get('q',"")
    try:
        q = b64decode(q)
    except:
        pass
    query_def = json.loads(q)
    
    order_by = request.GET.get('o')
    if not order_by: order_by = 'title'
    if order_by == 'author':
        order_by = 'first_author_name'
    
    model_name = query_def.get('model_name')
    if model_name is None:
        raise Http404
    
    if request.session.get('display_settings') is None:
        request.session['display_settings'] = RESULT_DISPLAY_COLUMNS.copy()
    display_columns = request.session['display_settings'].get(query_def['model_name'],{}).copy()
    
    
    #model = models.get_model('fiches', query_def['model_name'])
    model = apps.get_model('fiches', query_def['model_name'])
    #result_qs = model.objects.all()
    result_qs = None
    
    for f_def in query_def['filters']:
        dbg_logger.debug(f_def)
        f_q = get_Q(f_def['params'])
        dbg_logger.debug(f_q)
        if result_qs is None:
            result_qs = model.objects.filter(f_q)
        else:
            if f_def['op'] == 'and':
                result_qs = model.objects.filter(f_q) & result_qs
            else:
                result_qs = model.objects.filter(f_q) | result_qs
        
        # display_column for the class filter needs to be specifically set to False to be hidden, 
        # so if a columns class is not present in RESULT_DISPLAY_COLUMNS it is still shown if corresponding filter is used 
        if display_columns.get(f_def['cl']) != 'off':
            display_columns[f_def['cl']] = 'on'
    
    try:
        result_list = result_qs.order_by(order_by).distinct()
    except:
        result_list = []
    
    nb_val = result_list.count()
    
    # Convert all values to boolean: True if 'on', False otherwise ('auto' not seen in the query def or 'off')
    for k in display_columns.keys():
        display_columns[k] = display_columns[k] == 'on'
    
    return render(request, 'fiches/search/results_%s.html' % model_name.lower(), { 'object_list': result_list, 'nb_val': nb_val, 'display': display_columns, 'display_collector': True })

    # return render(
    #             'fiches/search/results_%s.html' % model_name.lower(),
    #             { 'object_list': result_list, 'nb_val': nb_val, 'display': display_columns, 'display_collector': True },
    #             context_instance=RequestContext(request)
    # )
    

def save_settings(request):
    new_display_settings = json.loads(request.POST.get('display_settings',"{}"))
    
    if request.session.get('display_settings') is None:
        request.session['display_settings'] = RESULT_DISPLAY_COLUMNS.copy()
    
    ds = request.session['display_settings']
    ds.update(new_display_settings)
    request.session['display_settings'] = ds
    
    return HttpResponse( "%s" % ds)


def save_filters(request):
    q = request.GET.get('q', "")
    query_def = json.loads(q)
    
    sf_id = request.GET.get('sfid')
    sf = SearchFilters.objects.get_or_create(pk=sf_id)
    


def relations(request):
    try:
        person_id = int(request.GET.get('p',''))
    except:
        return HttpResponseNotFound()
    person = get_object_or_404(Person, pk=person_id)
    relation_type = RelationType.objects.all()
    
    return render(request, 'fiches/search/relations.html', { 'person': person, 'JQUI': True, 'relation_type': relation_type })

    # return render(
    #                 'fiches/search/relations.html',
    #                 { 'person': person, 'JQUI': True, 'relation_type': relation_type },
    #                 context_instance=RequestContext(request)
    # )

@require_POST
@permission_required(perm='fiches.change_any_transcription')
def transcriptions_change_access(request):
    public = 'access_public' in request.POST
    private = 'access_private' in request.POST
    groups = UserGroup.objects.filter(id__in=request.POST.getlist('access_groups'))
    for biblio in Biblio.objects.filter(id__in=request.POST.getlist('transcriptions')):
        for transcription in biblio.transcription_set.all():
            transcription.access_public = public
            transcription.access_private = private
            transcription.access_groups.clear()
            transcription.access_groups.add(*groups)
            transcription.save()
    return HttpResponseRedirect(reverse('search-biblio') + '?' + request.POST.get('searchparams', ''))

def list_persons(request):
    first_letter = request.GET.get('q')
    filter_params = { 'may_have_biography': True,
                      'biography__isnull': False }
    if first_letter:
        filter_params['name__istartswith'] = first_letter
    persons = Person.objects.filter(**filter_params).order_by('name').distinct()
    return render(request, 'fiches/search/list_persons.html', {'persons': persons, 'first_letter': first_letter})
    # return render('fiches/search/list_persons.html', 
    #                           { 'persons': persons, 'first_letter': first_letter }, 
    #                           context_instance=RequestContext(request))


from django.http import HttpResponse

# Placeholder view to disable search functionality temporarily
def req_search_view(request):
    return HttpResponse("Search functionality is temporarily disabled.")


