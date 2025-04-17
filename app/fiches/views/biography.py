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
import pprint, time, re
from base64 import b64decode
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.forms.models import modelformset_factory, inlineformset_factory
import json
#from django.utils.encoding import smart_str, smart_unicode
from django.utils.html import escape
from itertools import groupby
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import never_cache

from utils import dbg_logger
from fiches.models import *
from fiches.utils import log_model_activity, get_grouped_objet_activities, supprime_accent, query_fiche, update_object_index, remove_object_index
from django.conf import settings
from fiches.models.person.biography import NoteBiography




#===============================================================================
# BIOGRAPHY
#===============================================================================

def get_bio_formDef(bioForm):
    i=0
    flst = {}
    for f in bioForm.visible_fields():
        flst[f.html_name]=i
        i += 1

    formdef = {
        'fieldsets': ( {
            'title': None,
            'template': "fiches/edition/biography/birth_death.html",
            'fields': ({'name': 'birth_place'},
                       {'name': 'birth_date'},
                       {'name': 'death_place'},
                       {'name': 'death_date'},
                       )
        },{
           'title': None,
           'fields': (
                {'name': 'religion'},
                {'name': 'origin', 'tooltip_id': 'ctxt-help-bio-origin', },
                {'name': 'nationality'},
                {'name': 'activity_places', 'tooltip_id': 'ctxt-help-bio-activity-places', 'class': 'single-line', 'sep': '<br/>'},
            )
        },{
           'title': None,
           'fields': (
                {'name': 'public_functions', 'class': 'single-line', 'sep': '<br/>', 'tooltip_id': 'ctxt-help-bio-public-functions'},
                {'name': 'comments_on_work', 'class': 'single-line', 'sep': '<br/>'},
                {'name': None, 'template': "fiches/edition/biography/profession_formset.html",},
                {'name': None, 'template': "fiches/edition/biography/society_formset.html",},
                {'name': 'education', 'class': 'single-line unused', 'sep': '<br/>' },
                {'name': 'abroad_stays', 'class': 'single-line unused', 'sep': '<br/>'},
            )
        },{
           'title': u"Relations et contacts",
           'fields': (
                {'name': None, 'template': "fiches/edition/biography/relation_formset.html",},
            )
        },{
           'title': "Notes",
           'fields': (
                { 'name': None, 'template': "fiches/edition/note_formset.html" },
            )
        },{
           'title': None,
           'fields': (
                {'name': 'archive', 'class': 'single-line', 'tooltip_id': 'ctxt-help-bio-archive' },
                {'name': None, 'template': 'fiches/display/person_bibliography.html', },
            )
        },
        )
    }
    for fs in formdef['fieldsets']:
        for f in fs['fields']:
            if f['name']:
                try:
                    f['field'] = bioForm.visible_fields()[flst[f['name']]]
                    fs[f['name']] = bioForm.visible_fields()[flst[f['name']]]
                except:
                    del f
    return formdef

DISPLAY_COLLECTOR = True



def person_without_bio(request):
    if not request.user.has_perm('fiches.add_biography'):
        return HttpResponse()
    persons = Person.objects.filter(
                biography__id__isnull=True,
                may_have_biography=True,
                name__isnull=False, modern=False).exclude(name='').order_by('name').distinct()
    return render(request, "fiches/workspace/person_for_bio.html", {'persons': persons})

def build_person_biblio_dict(person):
    def cd_grouper_doctype(cd):
        return cd.document.document_type
    def cd_grouper_ctype(cd):
        return cd.contribution_type.name

    #refs_prim = get_person_biblio(person).select_related().order_by('document_type__id')
    refs_prim = Biblio.objects.exclude(document_type__id=5).filter(litterature_type='p', contributiondoc__person=person).select_related().order_by('document_type__id','date','title')
    cd = ContributionDoc.objects.select_related().exclude(document__document_type__id=5).filter(person=person, document__litterature_type='p').order_by('document__document_type','contribution_type','document__date', 'document__title')

    grouped_refs_prim = [{
                          'grouper': g[0],
                          'list': [ {'grouper': gg[0], 'list': [ cd_item.document for cd_item in list(gg[1]) ]}  for gg in groupby(g[1], cd_grouper_ctype) ]
                         }  for g in groupby(cd, cd_grouper_doctype) ]


    # Biblio - litt�rature secondaire
    #refs_sec = Biblio.objects.exclude(document_type__id=5).select_related().filter(subj_person=person).order_by('document_type__id','date','title')
    litt_prim = Biblio.objects.exclude(contributiondoc__person=person)\
                .select_related().filter(litterature_type='p', subj_person=person)\
                .order_by('document_type__id','date','title')
    litt_sec = Biblio.objects.select_related()\
               .filter(litterature_type='s', subj_person=person)\
               .order_by('document_type__id','date','title')

    # Manuscripts
    contrib_man = ContributionDoc.objects.select_related().filter(document__document_type__id=5).filter(person=person, document__litterature_type='p').order_by('contribution_type__id', 'document__date', 'document__title')

    return {
        'contrib_man': contrib_man,
        #'trans_list': trans_list,
        #'grouped_refs': grouped_refs,
        'ref_list': refs_prim,
        'grouped_refs_prim': grouped_refs_prim,
        'litt_prim': litt_prim,
        'litt_sec': litt_sec,
        #'grouped_refs_sec': grouped_refs_sec,
    }


from fiches.views.bibliography import get_person_biblio

def display(request, person_id, version=0):

    person = get_object_or_404(Person, pk=person_id)

    # If the user has the permission to access biography versions, use the required version number
    if request.user.has_perm('fiches.access_unvalidated_biography'):
        bio = person.get_biography(version)
    # Otherwise use the validated version of the bio.
    else:
        bio = person.get_valid_biography()

    if bio is None:
        raise Http404()

    referer = request.META.get('HTTP_REFERER')
    if referer:
        edit_url = reverse('biography-edit', args=[person_id])
        display_url = reverse('biography-display', args=[person_id])
        if not edit_url in referer and not display_url in referer:
            request.session['bio_from'] = request.META.get('HTTP_REFERER')

    # Version informations
    nb_version = person.biography_set.all().count()
    version_info = {
        'need_validation' : (nb_version > 1) or not bio.valid,
        'has_versions': nb_version > 1,
        'nb_versions': nb_version,
        'last_version': bio.version == (nb_version-1),
    }

    # Relations
    if version == 0:
        relations = person.get_relations()
    else:
        relations = bio.relation_set.all()

    reverse_relations = person.get_reverse_relations()

    # Biblio - publications
    ctx = build_person_biblio_dict(person)

    # Activities
    activities = get_grouped_objet_activities(person)

    ctx.update({
      'person' : person,
      'bio'    : bio,
      'version_info': version_info,
      'model': Biography,
      'relations': relations,
      'reverse_relations': reverse_relations,
      'activities': activities,
      'display_collector': DISPLAY_COLLECTOR,
    })

    bio_template = "fiches/display/biography2.html"
   
    return render(request,bio_template, ctx)
    #return render(bio_template, ctx, context_instance=RequestContext(request))



def to_be_validated(request):
    if not request.user.has_perm('fiches.validate_biography'):
        return HttpResponseForbidden(u"Acc�s non autoris�")
    tobevalidated = Biography.objects.filter(valid=False,version=0).order_by('person__name')
    return render(request, 'fiches/workspace/biography_avalider.html', { 'tobevalidated' : tobevalidated } )



def create(request, person_id):
    if not request.user.has_perm('fiches.add_biography'):
        return HttpResponseForbidden(u"Acc�s non autoris�")
    return edit(request, person_id, create_bio=True)


@never_cache
def edit(request, person_id, version=0, create_bio=False):
    if not request.user.has_perm('fiches.change_biography'):
        return HttpResponseForbidden(u"Acc�s non autoris�")

    person = get_object_or_404(Person, pk=person_id)

    if create_bio:
        bio = Biography()
        bio.person = person
        bio.valid = False

    else:
        bio = person.get_biography(version=version)
        if bio is None:
            raise Http404()

#    dbg_logger.debug("relation_set -> %s" % bio.relation_set)

    #------------------------- Formsets ---------------------------------------#
    NoteFormset       = inlineformset_factory(Biography, NoteBiography, extra=0, form=NoteFormBiography)
    def get_notebioformset_qs(bio):
        note_qs = NoteBiography.objects.filter(owner=bio)
        if not request.user.is_staff:
            note_qs = note_qs.filter(models.Q(access_owner = request.user) |
                ( models.Q(access_groups__isnull = True) |
                  models.Q(access_groups__in     = request.user.usergroup_set.all()) )).distinct()
        if not request.user.has_perm('fiches.can_publish_note'):
            note_qs = note_qs.filter(~models.Q(access_public = True)).distinct()
        return note_qs

    RelationFormset   = inlineformset_factory(Biography, Relation, form=RelationForm, extra=1, fields='__all__')
    SocietyFormset    = inlineformset_factory(Biography, SocietyMembership, form=SocietyMembershipForm, extra=1, fields='__all__')
    ProfessionFormset = inlineformset_factory(Biography, Profession, form=ProfessionForm, extra=1, fields='__all__')

    exclude_from_duplication = ('NoteBiography','SocietyMembership','Profession','Relation')

    if request.method == 'POST':
        bioForm = BiographyForm(request.POST, request.FILES, instance=bio)
        note_qs = get_notebioformset_qs(bio)
        noteFormset = NoteFormset(request.POST, instance=bio, queryset=note_qs)
        relationFormset = RelationFormset(request.POST, instance=bio)
        societyFormset  = SocietyFormset(request.POST, instance=bio)
        professionFormset = ProfessionFormset(request.POST, instance=bio)

        # store the old notes id
        prev_version_note_ids = []
        for note in note_qs:
            prev_version_note_ids.append(note.id)
        #dbg_logger.debug("relationFormset.is_valid() -> %s" % relationFormset.is_valid())

        if bioForm.is_valid() and relationFormset.is_valid() and professionFormset.is_valid() and societyFormset.is_valid():
            bio = bioForm.save(commit=False)
            id_prev_version = bio.id
            if create_bio:
                bio.save()
            else:
                bio.id = None
                bio.version = 0
                bio.save()
                person.renum_bio()
                #new_bio = duplicate(bio, 'version', '0', exclude_models=exclude_from_duplication)
                #new_bio.person.renum_bio()

            # Modifie les donn�es des formsets de sorte que tous les �l�ments du formset soient pris comme nouveaux �l�ments.
            # Comme �a on provoque une duplication des objets li�s
            posted_data = request.POST.copy()
            for excluded_modelname in exclude_from_duplication:
                formset_prefix = '%s_set' % excluded_modelname.lower()
                for i in range(0,int(posted_data['%s-INITIAL_FORMS'%formset_prefix])):
                    posted_data['%s-%s-id'%(formset_prefix,i)] = ""
                posted_data['%s-INITIAL_FORMS'%formset_prefix] = 0


            # Write to the activity log
            log_model_activity(bio.person, request.user)

            noteFormset = NoteFormset(posted_data, instance=bio, queryset=get_notebioformset_qs(bio))
            if noteFormset.is_valid():
                noteFormset.save()
            else:
                dbg_logger.debug("noteFormset invalid")

            # we must also duplicate the notes the user cannot access
            if not create_bio:
                for note in NoteBiography.objects.filter(owner=id_prev_version).exclude(id__in=prev_version_note_ids):
                    print("Found note the user has no access")
                    note.id = None
                    note.owner = bio
                    note.save()

            relationFormset = RelationFormset(posted_data, instance=bio)
            if relationFormset.is_valid():
                for form in relationFormset.forms:
                    if form.is_valid():
                        if form.cleaned_data.get("related_person", None):
                            r = form.save(commit=False)
                            if form.cleaned_data.get("DELETE",True):
                                if r.id:
                                    r.delete()
                                else:
                                    r = None
                            else:
                                r.related_person.save()
                                form.save()
                    else:
                        dbg_logger.debug("relationFormset.form not valid")

            else:
                dbg_logger.debug("relationFormset.errors -> %s " % relationFormset.errors)

            societyFormset = SocietyFormset(posted_data, instance=bio)
            if societyFormset.is_valid():
                sty_list = societyFormset.save()

            else:
                dbg_logger.debug("societyFormset is not valid")

            professionFormset  = ProfessionFormset(posted_data, instance=bio)
            if professionFormset.is_valid():
                professionFormset.save()

            # Update Haystack index
            update_object_index(person)

            if request.POST.get('__continue', '') == 'on':
                return HttpResponseRedirect(reverse('biography-edit', args=[person_id]))
            else:
                return HttpResponseRedirect(reverse('biography-display', args=[person_id]))


        else:
            # bioForm is not valid
            dbg_logger.debug("bioForm.errors -> %s" % bioForm.errors)

    # request.method == 'GET'
    else:
        bioForm           = BiographyForm(instance=bio)
        noteFormset       = NoteFormset(instance=bio, queryset=get_notebioformset_qs(bio))
        relationFormset   = RelationFormset(instance=bio)
        societyFormset    = SocietyFormset(instance=bio)
        professionFormset = ProfessionFormset(instance=bio)

    bio_formdef = get_bio_formDef(bioForm)

    public_notes = None
    if bio is not None and not request.user.has_perm("fiches.can_publish_note"):
        public_notes = NoteBiography.objects.filter(owner=bio).filter(access_public = True)

    # Biblio - publications
    ctx = build_person_biblio_dict(person)

    ext_template = "fiches/edition/edit_base2.html"
    ctx.update({
      'edition': True,
      'ext_template': ext_template,
      'person_id': person_id,
      'form': bioForm,
      'model': Biography,
      'new_object': create_bio,
      'bio_formdef': bio_formdef,
      'noteFormset': noteFormset,
      'publicNotes': public_notes,
      'relationFormset': relationFormset,
      'societyFormset': societyFormset,
      'professionFormset': professionFormset,
      'prev_url': request.META.get('HTTP_REFERER', None),
      'reverse_relations': person.get_reverse_relations(),
    })
    #return render('fiches/edition/biography.html', ctx, context_instance=RequestContext(request))
    return render(request, 'fiches/edition/biography.html', ctx)



def validate(request, person_id, version=0):
    """
    Validate the version of a biography
    """
    if not request.user.has_perm('fiches.validate_biography'):
        return HttpResponseForbidden(u"Acc�s non autoris�")

    person = get_object_or_404(Person, pk=person_id)
    bio = person.get_biography(version=version)
    if bio is None:
        raise Http404()

    # Delete other versions
    person.biography_set.all().exclude(id=bio.id).delete()

    # Set flags of the new validated version
    bio.version=0
    bio.valid = True
    bio.save()

    # Update Haystack index
    update_object_index(person)
    return HttpResponseRedirect(reverse('biography-display', args=[person.id]))



def delete(request, person_id, version=0):
    """
    Delete a biography version and call renum_bio on the person instance
    """
    if not request.user.has_perm('fiches.delete_biography'):
        return HttpResponseForbidden(u"Acc�s non autoris�")

    person = get_object_or_404(Person, pk=person_id)
    bio = person.get_biography(version=version)
    if bio is None:
        raise Http404()

    try:
        version = int(version)
    except:
        version = 0

    nb_versions = person.biography_set.count()
    if nb_versions == 1 or bio.valid:
        return_url = request.session.get('bio_from') or reverse('search-person')
    else:
        if version > 0: version -= 1
        return_url = reverse('biography-display', args=[person.id, version])

    bio.delete()
    person.renum_bio()

    # Update Haystack index
    update_object_index(person)

    return HttpResponseRedirect(return_url)



def relations_list(request, person_id=None):
    try:
        person = get_object_or_404(Person, pk=person_id)

        re_digit_list = re.compile('^\d+$|^(\d+,)+\d+$')
        only_relations = request.GET.get('r','')
        only_relations = only_relations.split(',') if re_digit_list.match(only_relations) else ''

        only_people = request.GET.get('p','')
        only_people = only_people.split(',') if re_digit_list.match(only_people) else ''


        rel  = person.get_relations(only_people=only_people, only_relations=only_relations)
        rrel = person.get_reverse_relations(only_people=only_people, only_relations=only_relations)
        relation_list = [
            {'id':   r.related_person.id,
            #'name': r.related_person.__str__(), #__unicode__(),
            'name': str(r.related_person),
            'type': r.relation_type,
            'rel':  r.related_person.has_relations(exclude_people=[person_id])}
            for r in rel
        ] + [
            {'id':   r.bio.person.id,
            #'name': r.bio.person.__str__(), #__unicode__(),
            'name': str(r.bio.person),
            'type': r.relation_type.reverse_name,
            'rel':  r.bio.person.has_relations(exclude_people=[person_id])}
            for r in rrel
        ]


        # return render('fiches/list/biography_relations_list.html',
        #                           {
        #                            'person': person,
        #                            'relation_list': relation_list,
        #                           },
        #                           context_instance=RequestContext(request)
        # )

        return render(request, 'fiches/list/biography_relations_list.html', {
                'person': person,
                'relation_list': relation_list,
        })
    except Exception as e:
        return HttpResponseServerError('Error: {}'.format(str(e)))

RELATION_MAX_RECURSION_DEPTH = 5
def _get_all_relations(person, excluded_rels=[], depth=0, only_people=[], only_relations=[]):
    rel  = person.get_relations(only_people=only_people, only_relations=only_relations)
    rrel = person.get_reverse_relations(only_people=only_people, only_relations=only_relations)
    relation_list = [
        {'id': r.id,
         #'dst_name': r.related_person.__unicode__(),
         'dst_name': str(r.related_person),
         'src_name': person.name,
         'type': r.relation_type,
         'p': r.related_person
        }
        for r in rel if r.id not in excluded_rels
    ] + [
        {'id': r.id,
         #'dst_name': r.bio.person.__unicode__(),
         'dst_name': str(r.bio.person),
         'src_name': person.name,
         'type': r.relation_type.reverse_name,
         'p': r.bio.person
         }
        for r in rrel if r.id not in rel and r.id not in excluded_rels
    ]

    excluded_rels += [ r['id'] for r in relation_list ]
    if depth<RELATION_MAX_RECURSION_DEPTH:
        depth += 1
        extended_list = []
        for r in relation_list:
            if r['p'].has_relations():
                tmp_list = _get_all_relations(r['p'], excluded_rels=excluded_rels, only_people=only_people, only_relations=only_relations)
                excluded_rels += [ r['id'] for r in tmp_list ]
                extended_list += tmp_list
        relation_list += extended_list

    return relation_list


def relation_dot(request=None, person_id=None, max_depth=3):
    person = get_object_or_404(Person, pk=person_id)

    only_people = []
    only_relations = []

    relation_list = _get_all_relations(person, only_people=only_people, only_relations=only_relations)


    dot_relations = "\n".join('    "%s" -> "%s" [ label = "%s (%s)" ];' % (r['src_name'], r['dst_name'], r['type'], r['id']) for r in relation_list)

    output = "digraph essais {\n" + dot_relations + "\n}\n"
    return output

    response = HttpResponse(output)
    response['mime/type'] = "plain/text"
    return response
