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
from itertools import chain
from base64 import b64decode
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render, get_object_or_404 # render_to_response,
from django.template import RequestContext
from django.forms.models import inlineformset_factory
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.template.context_processors import csrf
from django.db import models
import json
from django.utils.dateformat import format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from fiches.models import *
from fiches.models.documents.document import NoteBiblio, Depot
from fiches.forms import NoteFormBiblio, BiblioForm, ContributionDocForm

from fiches.utils import log_model_activity, supprime_accent, get_last_model_activity, query_fiche, update_object_index, remove_object_index

from utils.coins import OpenURL
from utils.aggregates import Concatenate
from utils import dbg_logger

from functools import reduce


#===============================================================================
# BIBLIOGRAPHY
#===============================================================================

def get_biblio_formDef(biblioForm):
    i = 0
    flst = {}
    # Build mapping for visible fields
    for f in biblioForm.visible_fields():
        flst[f.html_name] = i
        i += 1
    i = 0
    # Build mapping for hidden fields
    for f in biblioForm.hidden_fields():
        flst[f.html_name] = i
        i += 1

    formdef = {
        'fieldsets': (
            {
                'title': None,
                'fields': (
                    {'name': 'document_type', 'template': None},
                    {'name': 'litterature_type', 'template': None, 'required': True},
                    {'name': None, 'template': "fiches/edition/document/contribution_formset.html"},
                    {'name': 'title', 'tooltip_id': 'ctxt-help-biblio-title', 'sep': '<br/>', 'template': None, 'class': 'single-line', 'required': True},
                    {'name': 'short_title', 'tooltip_id': 'ctxt-help-biblio-short-title', 'class': 'single-line'},
                    {'name': 'manuscript_type', 'template': None, 'required': True},
                )
            },
            {
                'title': "Recueil",
                'fields': (
                    {'name': 'book_title_man', 'map_to': 'book_title', 'tooltip_id': "ctxt-help-biblio-recueil"},
                    {'name': 'volume_man', 'map_to': 'volume', 'tooltip_id': "ctxt-help-biblio-recueil"}
                )
            },
            {
                'title': None,
                'fields': (
                    {'name': 'book_title', 'required': True},
                    {'name': 'journal_title', 'required': True},
                    {'name': 'journal_num', 'recommanded': True},
                    {'name': 'series_title'},
                    {'name': 'dictionary_title', 'required': True},
                    {'name': 'place', 'tooltip_id': 'ctxt-help-biblio-place', 'recommanded': True},
                    {'name': 'publisher', 'tooltip_id': 'ctxt-help-biblio-publisher'},
                    {'name': 'publisher2'},
                    {'name': 'collection', 'tooltip_id': 'ctxt-help-biblio-collection'},
                    {'name': 'date', 'recommanded': True, 'column_one': True},
                    {'name': 'date_f', 'hidden': True},
                    {'name': 'date2', 'column_two': True},
                    {'name': 'date2_f', 'hidden': True},
                    {'name': 'edition', 'tooltip_id': "ctxt-help-biblio-edition"},
                )
            },
            {
                'title': None,
                'fields': (
                    {'name': 'volume', 'tooltip_id': 'ctxt-help-biblio-volume'},
                    {'name': 'volume_nb', 'tooltip_id': 'ctxt-help-biblio-volume-nb'},
                    {'name': 'pages', 'tooltip_id': 'ctxt-help-biblio-pages', 'recommanded': True},
                    {'name': 'language', 'recommanded': True},
                    {'name': 'language_sec'},
                    {'name': 'depot', 'recommanded': True},
                    {'name': 'cote', 'recommanded': True, 'tooltip_id': "ctxt-help-biblio-cote"},
                )
            },
            {
                'title': "Sujets",
                'fields': (
                    {'name': None, 'class': 'single-line', 'sep': '<br/>', 'template': 'fiches/edition/keywords/simple_keywords.html'},
                    {'name': 'subj_person', 'class': 'single-line', 'sep': '<br/>'},
                    {'name': 'subj_society', 'class': 'single-line', 'sep': '<br/>'},
                )
            },
            {
                'title': None,
                'fields': (
                    {'name': 'abstract', 'class': 'single-line', 'sep': '<br/>'},
                )
            },
            {
                'title': 'Documents',
                'fields': ({
                    'name': None,
                    'template': "fiches/edition/document/doc_documentfile_formlist.html",
                },)
            },
            {
                'title': None,
                'fields': ({
                    'name': None,
                    'template': "fiches/edition/document/transcription_b_set.html",
                },)
            },
            {
                'title': "Notes",
                'fields': ({
                    'name': None,
                    'template': "fiches/edition/note_formset.html"
                },)
            },
            {
                'title': "",
                'fields': (
                    {'name': 'creator'},
                )
            }
        )
    }

    # Safely assign actual form field objects to each fieldset field
    for fs in formdef['fieldsets']:
        for f in fs['fields']:
            if f['name']:
                name = f['name']
                if 'map_to' in f and f['map_to']:
                    name = f['map_to']
                if f.get('hidden', False):
                    fields_list = biblioForm.hidden_fields()
                else:
                    fields_list = biblioForm.visible_fields()
                idx = flst.get(name)
                if idx is not None and idx < len(fields_list):
                    f['field'] = fields_list[idx]
                else:
                    # Field not found: log a warning (optional) and assign None.
                    f['field'] = None
    return formdef





def get_person_biblio(person, output_model=Biblio, modern=False, document_type=None, document_type_id=None, contribution_type=None, contribution_type_id=None):
    """
    Get the list of documents for wich a person p has a contribution.
    Is is possible to filter on the type of contribution and the type of document
    These parameters can be passed as obects (contribution_type and document_type) or
    only the id's of the objetcs. In some situation it is preferable to pass the id, so we can avoid some DB hits
    """

    cd = ContributionDoc.objects.select_related().filter(person=person)

    #----- Filter on litterature type
    if modern is not None:
        lit_type = 'p'
        if modern: lit_type = 's'
        cd = cd.filter(document__litterature_type=lit_type)


    #----- Filter on contribution type
    if contribution_type and not contribution_type_id:
        try:    contribution_type_id = contribution_type.id
        except: contribution_type = contribution_type_id = None
    if contribution_type_id:
        cd = cd.filter(contribution_type__id=contribution_type_id)


    #----- Filter on document type
    if document_type and not document_type_id:
        try:    document_type_id = document_type.id
        except: document_type = document_type_id = None
    if document_type_id:
        cd = cd.filter(document__document_type__id=document_type_id)

    # Ordering
    cd = cd.order_by('document__document_type','document__date', 'document__title')

    # List of the document ids
    doc_ids = cd.values_list('document_id', flat=True)

    #model = models.get_model(app_label, model_name)
    return output_model.objects.filter(pk__in=doc_ids)


DISPLAY_COLLECTOR = True

def display(request, doc_id):
    doc = get_object_or_404(Biblio, pk=doc_id)
    contributions = doc.contributiondoc_set.all()

    # Format the document date(s)
    if doc.date:
        doc_date = format(doc.date, doc.date_f.replace('%', '').replace('-', ' / '))
        if doc.date2:
            doc_date += '-' + format(doc.date2, doc.date2_f.replace('%', '').replace('-', ' / '))
    else:
        doc_date = ""
    last_activity = get_last_model_activity(doc)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        edit_url = reverse('bibliography-edit', args=[doc_id])
        if not referer.endswith(edit_url):
            request.session['biblio_from'] = referer

    # 1) Fetch "top-level" primary keywords
    primary_kw = (
        PrimaryKeyword.objects
        .filter(biblio__id=doc_id)
        .distinct()
    )

    # 2) Fetch secondary keywords, each referencing .primary_keyword
    #    We select_related('primary_keyword') to access primary_keyword.word easily
    secondary_kw = (
        SecondaryKeyword.objects
        .select_related('primary_keyword')
        .filter(biblio__id=doc_id)
        .order_by('primary_keyword__word')
    )

    # We'll build a kw_dict = { "PrimaryWord": { 'id': pkw.id, 'word': pkw.word, 'skw': [ ... ] }, ... }
    kw_dict = {}

    # Insert each PrimaryKeyword into the dict, no sub-keywords yet
    for pkw in primary_kw:
        kw_dict[pkw.word] = {
            'id': pkw.id,
            'word': pkw.word,
            'skw': [],
        }

    # Now handle the SecondaryKeywords, nest them under their .primary_keyword
    for skw in secondary_kw:
        if skw.primary_keyword:
            parent_word = skw.primary_keyword.word  # e.g. "Histoire", "Politique", etc.
            # If the parent isn't in the dict (rare corner-case), add it
            if parent_word not in kw_dict:
                kw_dict[parent_word] = {
                    'id': skw.primary_keyword.id,
                    'word': parent_word,
                    'skw': [],
                }
            # Add this secondary kw to the parent's 'skw' list
            kw_dict[parent_word]['skw'].append({
                'id': skw.id,
                'word': skw.word,
            })
        else:
            # If a SecondaryKeyword has no primary_keyword, treat it as top-level or skip
            if skw.word not in kw_dict:
                kw_dict[skw.word] = {
                    'id': skw.id,
                    'word': skw.word,
                    'skw': [],
                }
            # Optionally do nothing else, or add logic as needed

    # Decide on your base template
    ext_template = "fiches/display/display_base2.html"

    from fiches.constants import DOCTYPE

    context = {
        'ext_template': ext_template,
        'doc': doc,
        'model': Biblio,
        'doc_date': doc_date,
        'contributions': contributions,
        'last_activity': last_activity,
        'display_collector': DISPLAY_COLLECTOR,
        'kw_dict': kw_dict,
        'SHOW_EMPTY_FIELDS': True,
        'DOCTYPE' : DOCTYPE,
        'subj_person': doc.subj_person.all(),
    }

    return render(request, 'fiches/display/bibliography.html', context)



def create(request, doctype=1):
    if not request.user.has_perm('fiches.add_biblio'):
        return HttpResponseForbidden(u"Accès non autorisé")
    return edit(request, None, new_doc=True, new_doctype=doctype)


from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.db import models, connection
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from functools import reduce
import json

@never_cache
def edit(request, doc_id=None, new_doc=False, new_doctype=1):
    """ Handles creation and modification of bibliography records (fiches bibliographiques). """

    # -------------------------------
    # Permission Checks
    # -------------------------------
    if not request.user.has_perm('fiches.change_biblio'):
        return HttpResponseForbidden(_("Accès non autorisé"))

    doc = None

    # Handle existing bibliography
    if doc_id:
        doc = get_object_or_404(Biblio, pk=doc_id)

        # Ensure user has permission to edit the document
        if not request.user.has_perm('fiches.change_any_biblio') and doc.creator != request.user:
            return HttpResponseForbidden(_("Accès non autorisé"))

    # Handle new bibliography creation (without saving immediately)
    if new_doc:
        if not request.user.has_perm('fiches.add_biblio'):
            return HttpResponseForbidden(_("Accès non autorisé"))

        doc = Biblio(creator=request.user, legacy_depot="n/a")

        # Assign document type if provided
        if new_doctype and request.method == 'GET':
            doc.document_type = get_object_or_404(DocumentType, pk=new_doctype)

    # -------------------------------
    # Keywords Query
    # -------------------------------
    primary_kw = secondary_kw = None
    if doc and doc.id:
        primary_kw = PrimaryKeyword.objects.filter(biblio=doc).exclude(secondarykeyword__biblio=doc)
        secondary_kw = SecondaryKeyword.objects.filter(biblio=doc).order_by('parent__word')

    # -------------------------------
    # Exclusive Fields Setup
    # -------------------------------
    try:
        exclusive_fields_dct = {
            itm[0]: [x.strip() for x in itm[1].split(",") if x.strip()]
            for itm in DocumentType.objects.all().values_list('id', 'exclusive_fields')
        }
        allexclusive_fields_lst = tuple(set(reduce(lambda x, y: x + y, exclusive_fields_dct.values(), [])))
    except Exception:
        exclusive_fields_dct, allexclusive_fields_lst = {}, ()

    doctype_exclusive_fields_js = mark_safe(json.dumps(exclusive_fields_dct))
    doctype_allexclusive_fields_js = mark_safe(json.dumps(allexclusive_fields_lst))

    # -------------------------------
    # Formsets Setup
    # -------------------------------
    NoteFormset = inlineformset_factory(Biblio, NoteBiblio, extra=0, form=NoteFormBiblio)
    note_qs = NoteBiblio.objects.filter(owner=doc) if doc and doc.id else NoteBiblio.objects.none()

    # Restrict notes visibility based on user permissions
    if not request.user.is_staff:
        note_qs = note_qs.filter(
            Q(access_owner=request.user) |
            Q(access_groups__isnull=True) |
            Q(access_groups__in=request.user.usergroup_set.all())
        ).distinct()

    if not request.user.has_perm('fiches.can_publish_note'):
        note_qs = note_qs.exclude(access_public=True)
    
    ContributionFormset = inlineformset_factory(Biblio, ContributionDoc, form=ContributionDocForm, extra=1)
    NoteFormset = inlineformset_factory(Biblio, NoteBiblio, extra=0, form=NoteFormBiblio)

    # -------------------------------
    # Form Handling (POST Request)
    # -------------------------------
    if request.method == 'POST':
        biblioForm = BiblioForm(request.POST, instance=doc)

        if biblioForm.is_valid():
            doc = biblioForm.save(commit=False)

            # Ensure creator remains unchanged unless permission is granted
            if not request.user.has_perm('fiches.change_manuscript_ownership'):
                doc.creator = request.user

            doc.save()
            biblioForm.save_m2m()

            # Set a default depot for newly created documents
            if new_doc:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE fiches_biblio SET depot = %s WHERE id = %s",
                        ["n/a", doc.id]
                    )

            log_model_activity(doc, request.user)

            # Process note formset
            noteFormset = NoteFormset(request.POST, instance=doc, queryset=note_qs)
            if noteFormset.is_valid():
                noteFormset.save()

            # Process contribution formset
            if biblioForm.cleaned_data.get('litterature_type') == 's':
                ContributionFormset = inlineformset_factory(Biblio, ContributionDoc, form=ContributionDocSecForm, extra=1)

            contributionFormset = ContributionFormset(request.POST, instance=doc)
            if contributionFormset.is_valid():
                contributionFormset.save()

            # Update first author cache & re-index the document
            doc.updateFirstAuthor()
            update_object_index(doc)

            # Redirect after successful form submission
            if request.POST.get('__continue', '') == 'on':
                return HttpResponseRedirect(reverse('bibliography-edit', args=[doc.id]))
            return HttpResponseRedirect(reverse('display-bibliography', doc.id))
        else:
            noteFormset = NoteFormset(request.POST, instance = doc, queryset=note_qs)
            contributionFormset = ContributionFormset(request.POST, instance=doc)

    else:
        # Initialize forms for GET requests
        biblioForm = BiblioForm(instance=doc) if doc else BiblioForm()
        noteFormset = NoteFormset(instance=doc, queryset=note_qs)
        contributionFormset = ContributionFormset(instance=doc)

    # -------------------------------
    # Public Notes (Read-only display)
    # -------------------------------
    public_notes = None
    if doc and not request.user.has_perm("fiches.can_publish_note"):
        public_notes = NoteBiblio.objects.filter(owner=doc, access_public=True)

    # -------------------------------
    # Template Rendering
    # -------------------------------
    ext_template = "fiches/edition/edit_base2.html"

    return render(request, 'fiches/edition/bibliographie.html', {
        'ext_template': ext_template,
        'doc': doc,
        'form': biblioForm,
        'model': Biblio,
        'new_object': new_doc,
        'biblio_formdef': get_biblio_formDef(biblioForm),
        'noteFormset': noteFormset,
        'publicNotes': public_notes,
        'contributionFormset': contributionFormset,
        'doctype_exclusive_fields_js': doctype_exclusive_fields_js,
        'doctype_allexclusive_fields_js': doctype_allexclusive_fields_js,
        'primary_kw': primary_kw,
        'secondary_kw': secondary_kw,
        'prev_url': request.META.get('HTTP_REFERER', None),
    })





def delete(request, doc_id):
    '''
    Delete the Bibliography entry
    '''

    if not request.user.has_perm('fiches.delete_biblio'):
        return HttpResponseForbidden(u"Accès non autorisé")

    doc = get_object_or_404(Biblio, pk=doc_id)

    # Remove Haystack index
    remove_object_index(doc)

    doc.delete()

    from_url = request.session.get('biblio_from')
    if from_url:
        return HttpResponseRedirect(from_url)
    else:
        return HttpResponseRedirect(reverse('search-biblio'))



def documentfile_change_list(request, doc_id):
    doc = get_object_or_404(Biblio, pk=doc_id)
    # return render('fiches/edition/document/documentfile_change_list.html',
    #                           {
    #                            'doc': doc,
    #                            },
    #                           context_instance=RequestContext(request)
    # )

    return render(request, 'fiches/edition/document/documentfile_change_list.html', {'doc': doc})


def documentfile_add(request, doc_id, docfile_id):
    doc = get_object_or_404(Biblio, pk=doc_id)
    docfile = get_object_or_404(DocumentFile, pk=docfile_id)
    doc.documentfiles.add(docfile)
    doc.save()
    return HttpResponse('ok')


@csrf_protect
def documentfile_remove(request, doc_id, docfile_id):
    """
    If a df is only linked to the document from whitch we remove,
    it is possible to delete completely the df record.
    Ex: On Biliography A, we find DocumentFile B. If we remove B from A,
    it is possible to delete it completely. Otherwise, if Biblio C is also liked to B,
    it won't be possible to remove it.
    """
    c = {}
    c.update(csrf(request))

    doc = get_object_or_404(Biblio, pk=doc_id)
    docfile = get_object_or_404(DocumentFile, pk=docfile_id)
    remove_done = False

    # Number of Biblio objects linked to this documentfile
    nb_ref = docfile.biblio_set.count()

    if request.method == 'POST':
        if request.POST.get('doc_id','') == doc_id and request.POST.get('docfile_id') == docfile_id:
            doc.documentfiles.remove(docfile)
            if request.POST.get('docfile_delete') and docfile.biblio_set.count() == 0:
                docfile.delete()
            doc.save()
            remove_done = True

    # c.update({
    #    'doc': doc,
    #    'docfile': docfile,
    #    'nb_ref': nb_ref,
    #    'remove_done': remove_done,
    #    'framed': True,
    # })
    c = {
       'doc': doc,
       'docfile': docfile,
       'nb_ref': nb_ref,
       'remove_done': remove_done,
       'framed': True,
    }
    #return render('fiches/edition/document/documentfile_remove.html', c, context_instance=RequestContext(request))

    return render(request, 'fiches/edition/document/documentfile_remove.html', c)



def get_person_publications(request, person_id):
    journal_title = request.GET.get('j')
    try:
        journal_title = b64decode(journal_title)
        publications = Biblio.objects.filter(journal_title__icontains=journal_title).filter(contributiondoc__person__id=person_id).order_by('title').distinct()
        #return render('fiches/bibliography_references/publication_list.html', {'publications': publications} , context_instance=RequestContext(request))
        return render(request, 'fiches/bibliography_references/publication_list.html', {'publications': publications})
    except (TypeError, ValueError, ObjectDoesNotExist) as e:
        return HttpResponseServerError('Error: {}'.format(e))



def endnote(request, doc_id, getid=False):
    """
    Exportation pour EndNote.
    Exporte la bibliographie identifiée par `doc_id`
    Si `getid` est vrai, exporte aussi toutes les bibliographies dont les pk
    sont données dans la variable GET `ids`, séparrée par des virgules.
    """
    doc_ids = []
    if doc_id: doc_ids = [doc_id]
    if getid:
        doc_ids += request.GET.get('ids', "-1").replace(' ','').strip(',').split(',')
    docs = Biblio.objects.filter(pk__in=doc_ids)
    if docs.count() == 0:
        raise Http404()

    references = []
    for doc in docs:
        ref_bit = []
        # Document TYpe
        if doc.document_type.id == 1:
            ref_bit.append(('DT', 'Book'))
        elif doc.document_type.id == 2:
            ref_bit.append(('DT', 'Book Section'))
        elif doc.document_type.id == 3:
            ref_bit.append(('DT', 'Journal Article'))
        elif doc.document_type.id == 4:
            ref_bit.append(('DT', 'Dictionary'))

        # Title
        ref_bit.append(('TI', doc.title))

        # Authors (Contributions)
        for author_name in [ c.person.name for c in doc.contributiondoc_set.all() ]:
            ref_bit.append(('AU', author_name))

        ref_bit.append(('BT',  doc.book_title))
        ref_bit.append(('PU',  doc.journal_title))
        ref_bit.append(('TIS', doc.series_title))
        ref_bit.append(('TXS', doc.series_text))
        ref_bit.append(('AB',  doc.journal_abr))
        ref_bit.append(('TD',  doc.dictionary_title))
        ref_bit.append(('SE',  doc.serie))
        ref_bit.append(('NO',  doc.serie_num))
        ref_bit.append(('VO',  doc.volume))
        ref_bit.append(('NV',  doc.volume_nb))
        ref_bit.append(('EN',  doc.edition))
        ref_bit.append(('LI',  doc.place))
        ref_bit.append(('ET',  doc.publisher))
        try:
            ref_bit.append(('DA',  doc.date.isoformat()))
        except:
            ref_bit.append(('DA',  '000-00-00'))
        try:
            ref_bit.append(('YE',  doc.date.year))
        except:
            ref_bit.append(('YE',  ''))

        ref_bit.append(('PA', doc.pages))
        ref_bit.append(('TC', doc.short_title))
        ref_bit.append(('IS', doc.isbn))
        ref_bit.append(('AB', doc.abstract))

        # Subjects
        ref_bit.append(('KE', "; ".join([ u"%s" % kw for kw in chain(
                                            doc.subj_primary_kw.all(),
                                            doc.subj_secondary_kw.all(),
                                            doc.subj_person.all(),
                                            doc.subj_society.all())
                                        ])
                      ))
        # URLs
        ref_bit.append(('UR', "; ".join(doc.urls.split())))

        try:
            ref_bit.append(('AC', doc.access_date.isoformat()))
        except:
            ref_bit.append(('AC', ''))

        ref_bit.append(('DB', 'lumieres.VD'))
        ref_bit.append(('LG', doc.language ))

        references.append("\n".join(['REF'] + [ u"%s- %s" % (label,value) for label,value in ref_bit] +['END']))

    #return HttpResponse("\n\n".join(references), mimetype="text/plain ; charset=utf-8")
    return HttpResponse("\n\n".join(references), content_type="text/plain; charset=utf-8")



def display_man(request, man_id):
    """
    Redirige les anciens url de type /fiches/man/<id> sur /fiches/biblio/<id>
    Sorte de compatibilité déscendante pour l'affichage des manuscripts des version antérieure
    lorsque les manuscript étaient des objets distinct des Biblio.
    """
    biblio_man = get_object_or_404(Biblio, manuscript__id=man_id)
    return HttpResponseRedirect(reverse("display-bibliography", args=[biblio_man.id]))
