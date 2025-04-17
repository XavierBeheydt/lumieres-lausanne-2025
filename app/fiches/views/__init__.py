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
import unicodedata
import os
from mimetypes import guess_type
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.template import Context, RequestContext, loader
#from django.core.servers.basehttp import FileWrapper
from wsgiref.util import FileWrapper
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, get_object_or_404
import json
from django.utils.encoding import smart_str
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
#from django.views.generic import create_update
from django.contrib.auth.decorators import login_required, permission_required

from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from utils import dbg_logger
from fiches.models import ACModel
from django.contrib.auth.forms import PasswordChangeForm
#from lumieres_project.urls import MyPasswordChangeForm
from fiches.models import Finding, Transcription, FreeContent, News, ActivityLog
from django.core.exceptions import ObjectDoesNotExist

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.apps import apps



def main_index(request):
    u"""
    Affiche la page d'accueil
    """
    text = FreeContent.objects.get_content("home")
    news = News.objects.filter(published=True)[:3]
    findings = Finding.objects.filter(published=True)[:3]
    transcriptions = Transcription.objects.last_published(3)
                                                   
    context = { 'text': text, 'last_findings': findings, 'last_news': news, 'last_transcriptions': transcriptions }

    return render(request, "fiches/home2.html", context)
    #return render("fiches/home2.html", context, context_instance=RequestContext(request))


def maintenance(request):
    try:
        maintenance_enabled = bool(settings.LL_MAINTENANCE)
    except AttributeError:
        maintenance_enabled = False
    
    if maintenance_enabled:
        return render(request, "maintenance.html")
        #return render("maintenance.html", {}, context_instance=RequestContext(request))
    else:
        return main_index(request)



def ajax_search(request):
    u"""
    Vue generale pour les obtenir des liste d'objet en ajax.
    
    Les paramètres important de la requête sont:
        q: la valeur à chercher, p.ex: "Bolom"
        model_name: le nom du modèle, p.ex Person
        search_field: le champ du modèle dans lequel chercher q, ainsi que l'operateur à utiliser
                      voir la fonction interne "construct_search" dans le code
        
        Optionels
        and_queries: les requêtes additionels qui seront combinées avec un AND
                     au format JSON
        not_queries: les requêtes additionels qui seront utilisée pour exclure des objets
                     au format JSON
        
        outf: le format de sortie:
                "u" -> la valeur retournée par __unicode__ des objets trouvé
                "_f__<field_name>" -> commence par _f__ suivi du nom du champ utilisé pour la sortie, p.Ex _f__first_author
                "_m__<method_name>" -> commence par _m__ suivi du nom du nom de la méthode (sans paramètre) utilisée pour la sortie
              Tout autre valeur (y compris rien) donne __unicode__|id, p. ex: Crousaz|15 
    
        f_distinct: permet d'effectuer un "distinct" sur la liste mise en forme par outf. En effet
                    le distinct au niveau de la base est calculé sur l'ensemble des champs des objets. pas seulement sur le champ
                    spécifié par outf
    
    Inspiré de : http://jannisleidel.com/2008/11/autocomplete-form-widget-foreignkey-model-fields/
    """
    query = request.GET.get('q', None)
    app_label = request.GET.get('app_label', 'fiches')
    model_name = request.GET.get('model_name', None)
    search_field = request.GET.get('search_field', None)
    and_queries = request.GET.get('and_queries', None)
    not_queries = request.GET.get('not_queries', None)
    outformat = request.GET.get('outf', 'u|id')
    f_distinct = bool(request.GET.get('f_distinct', True))     # If true, do a manual distinct after rendering data with specific field output, default to true
    
    
    if and_queries is not None:
        try:
            and_queries = json.loads(and_queries)
        except:
            and_queries = None

    if not_queries is not None:
        try:
            not_queries = json.loads(not_queries)
        except:
            not_queries = None


    if search_field and app_label and model_name:
        def construct_search(field_name):
            # use different lookup methods depending on the notation
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('=='):
                return "%s__exact" % field_name[2:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__icontains" % field_name[1:]
            elif field_name.startswith('$'):
                return "%s__iendswith" % field_name[1:]
            elif field_name.startswith('_null_'):
                return "%s__isnull" % field_name[6:]
            else:
                return "%s__icontains" % field_name
        
        #model = models.get_model(app_label, model_name)
        model = apps.get_model(app_label, model_name)
        if issubclass(model, ACModel):
            if settings.DEBUG:
                return HttpResponseNotFound('ACModel subclass')
            else:
                return HttpResponseNotFound()
        
        q = models.Q()
        #q = Q()
        for bit in query.split():
            q = q | models.Q(**{
                        construct_search(smart_str(search_field)): smart_str(bit)
                    })
        
#        dbg_logger.debug("``and_queries`` -> %s" % and_queries)
         
        if and_queries is not None:
            for and_q in and_queries:
                if and_q['field'].startswith('_null_'):
                    and_q['value'] = bool(and_q['value']=='true')
                try:
                    q = q & models.Q(**{ construct_search(smart_str(and_q['field'])): and_q['value'] })
                except:
                    if settings.DEBUG: raise
                    pass
        
#        dbg_logger.debug("``q`` -> %s" % q)
        
        nq = models.Q()
        #nq = Q()
        if not_queries is not None:
            for not_q in not_queries:
                try:
                    nq = nq & models.Q(**{ construct_search(smart_str(not_q['field'])): not_q['value'] })
                except:
                    pass
        
        if query is None:
            qs = model._default_manager.all()
        else:
            qs = model._default_manager.filter(q).exclude(nq).distinct()
        
        
        #
        # Format data for output
        #
        data_list = []
        if outformat == 'u':
            #data_list = [u"%s\n" % f.__unicode__() for f in qs]   
            data_list = [u"%s\n" % str(f) for f in qs]
            
        elif outformat.startswith('_f__'):
            field = outformat[4:]
            try:
                data_list = [u"%s\n" % f[field] for f in qs.values(field).distinct()]
                if f_distinct:
                    data_set = set(data_list)
                    data_list = list(data_set | data_set)
            except AttributeError:
                #data_list = [u"%s\n" % f.__unicode__() for f in qs]
                data_list = [u"%s\n" % str(f) for f in qs]

        elif outformat.startswith('_m__'):
            method = outformat[4:]
            try:
                data_list = [u"%s\n" % getattr(f, method)() for f in qs]
                if f_distinct:
                    data_set = set(data_list)
                    data_list = list(data_set | data_set)
            except AttributeError:
                dbg_logger.debug("attribute not found" % method)
                #data_list = [u"%s\n" % f.__unicode__() for f in qs]
                data_list = [u"%s\n" % str(f) for f in qs]
            
        else:
            #data_list = [u"%s|%s\n" % (f.__unicode__(), f.pk) for f in qs]
            data_list = [u"%s|%s\n" % (str(f), f.pk) for f in qs]
        
        data = ''.join(data_list)
        return HttpResponse(data)
    
    return HttpResponseNotFound()



def serve_documentfile(request, documentfile_key, attachment=True):
    """
    Retourne le fichier identifié par 'documentfile_key' si l'utilisateur a les permissions nécessaire
    """
    try:
        f_id = int(documentfile_key)
        df = get_object_or_404(DocumentFile, pk=f_id)
    except ValueError:
        df = get_object_or_404(DocumentFile, slug=documentfile_key)
    except:
        raise
    
    if not df.user_access(request.user, any_login=True):
        return HttpResponseForbidden("Access denied")
    
    path_to_file = df.file.path

#   Send a file through Django without loading the whole file into              
#   memory at once. The FileWrapper will turn the file object into an           
#   iterator for chunks of 8KB.

    
    content_type = guess_type(path_to_file)[0]
    if content_type is None: 
        content_type = "application/octet-stream"

    #wrapper = FileWrapper(file(path_to_file))
    # Create a file wrapper around the file
    wrapper = FileWrapper(open(path_to_file, 'rb'))
    response = HttpResponse(wrapper, content_type=content_type)
    response['ETag'] = ""
    response['Content-Length'] = os.path.getsize(path_to_file)
    if attachment:
        # Normalize the filename to ASCII
        filename = os.path.basename(path_to_file)
        ascii_filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
        #attachment_name = unicodedata.normalize('NFKD', path_to_file).encode('ascii','ignore')
        #response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(attachment_name)
        
        # Set the Content-Disposition header
        response['Content-Disposition'] = f'attachment; filename="{ascii_filename}"'
    
    return response


    
    
def documentfile_frame_list(request):
    u"""
    Affiche la liste des documents disponibles dans la dialogue "Ajouter un nouveau document"
    pour l'onglet "Choisir un document existant
    """
    q = request.GET.get("q","")
    if q:
        docfiles = DocumentFile.objects.filter(title__icontains=q) | DocumentFile.objects.filter(url__icontains=q) | DocumentFile.objects.filter(file__icontains=q)
    else:
        docfiles = DocumentFile.objects.all()
        
    if not request.user.is_staff: 
        q_nogroup    = models.Q(access_groups__exact=None)
        q_usergroups = models.Q(access_groups__in=[ g.id for g in request.user.groups.all()])
        docfiles     = docfiles.filter( q_nogroup | q_usergroups ).distinct()
    
    field_id = request.GET.get('field_id', 'id_urls')

    # Order the queryset by title
    docfiles = docfiles.order_by('title')

    paginator = Paginator(docfiles, 15)  # Show 15 items per page

    page = request.GET.get('page')
    try:
        docfiles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        docfiles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        docfiles = paginator.page(paginator.num_pages)

    context = {
        'docfiles': docfiles,
        'field_id': field_id,
        'q': q,
    }

    return render(request, "fiches/edition/document/documentfile_frame_list.html", context)


    # return list_detail.object_list(
    #     request,
    #     queryset = docfiles,
    #     template_object_name = "docfile",
    #     template_name = "fiches/edition/document/documentfile_frame_list.html",
    #     extra_context = { 'field_id': field_id, "q": q },
    #     paginate_by = 15,
    # )
    
    
def documentfile_frame_create(request, doc_id=None, docfile_id=None, create_done=False):
    """
    Ajout de nouveau document depuis la dialogue "Ajouter un nouveau document"
    """
    if request.method == 'POST':
        # Assuming form is submitted and we need to create a new DocumentFile
        docfile = DocumentFile.objects.create(title="Default Title")
        return HttpResponseRedirect(reverse('docfile-frame-create', kwargs={'create_done': True, 'docfile_id': docfile.id}))
    
    # For GET requests or any other request type, prepare the initial form or context
    context = {
        'create_done': create_done,
        'docfile_saved': create_done,
        'docfile_id': docfile_id,
    }
    
    response = render(request, "fiches/edition/document/documentfile_frame_form.html", context)
    response['Cache-Control'] = 'no-cache'
    return response


def documentfile_frame_edit(request, docfile_id, edit_done=False):
    """
    Modification d'un document dans la dialogue "Editer un document"
    """
    if request.method == 'POST':
        pass
        # Juste pour tester temps réponse lent
        #import time
        #time.sleep(2)
    if docfile_id == '#':
        return Http404()
    else:
        return create_update.update_object(
            request,
            DocumentFile,
            object_id = docfile_id,
            template_name = "fiches/edition/document/documentfile_frame_form.html",
            template_object_name = "docfile",
            post_save_redirect = reverse('docfile-frame-edit-done', args=[docfile_id]),
            extra_context = {'editing': True, 'docfile_saved': edit_done}
        )


def server_error(request, template_name='500.html'):
    """
    500 error handler.
    Modified from django.views.default.server_error. 
    Added RequestContext as Context so we can have access to MEDIA_URL

    Templates: `500.html`
    Context: RequestContext
    """
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))


def login(request):
    """
    La page de login
    """
    from django.contrib.auth.views import login as auth_login 
    return auth_login(request, template_name="login2.html")


def workspace(request):
    u"""
    Affiche l'Espace de travail
    """
    from lumieres_project.urls import MyPasswordChangeForm  # Lazy import inside the function
    instructions = FreeContent.objects.get_content("workspace>instructions")
    return render(request, "fiches/workspace/main.html", { 'form': MyPasswordChangeForm(user=request.user), 'instructions': instructions })
    #return None


def workspace_collections(request, coll_id=None, coll_slug=None):
    """
    Affiche l'Espace de travail en mode Collection
    en sélectionnant la collection donnée par coll_id ou coll_slug.
    
    In the old project, this logic was similar to "tab_index" or "index" in collections.py.
    We fetch the user's collections, pick one, and pass all necessary variables 
    (coll, coll_list, shared_coll, contrib_coll, etc.) to the partial template.

    Typically, you load this partial into main.html via an AJAX call or a tab click 
    (not by directly rendering main.html itself).
    """
    from django.contrib.auth.forms import PasswordChangeForm
    from fiches.models import ObjectCollection
    from fiches.views.collections import get_coll, get_user_coll_list  # Reuse your old helpers
    from django.http import Http404

    # 1) Ensure the user has at least one collection
    coll_list = get_user_coll_list(request.user)
    if not coll_list:
        raise Http404("No collections found for this user.")

    # 2) Select the current collection via coll_id or coll_slug (if provided)
    coll = None
    if coll_id:
        coll = get_coll(request.user, coll_id, create_if_none=False)
    elif coll_slug:
        try:
            coll = ObjectCollection.objects.get(slug=coll_slug)
        except ObjectCollection.DoesNotExist:
            coll = None

    # If coll was never found, default to the first collection
    if not coll:
        coll = coll_list[0]

    # 3) Compute shared or contributed collections
    user_groups = request.user.profile.get_usergroups()
    shared_coll = ObjectCollection.objects.exclude(owner=request.user).filter(
        access_groups__in=user_groups
    ).distinct()

    contrib_coll = ObjectCollection.objects.exclude(owner=request.user) \
        .exclude(access_private=True) \
        .filter(change_groups__in=user_groups).distinct()

    # 4) If you want to replicate old "coll_access"/"coll_change" logic, do so:
    coll_change = (coll.owner == request.user) or bool(
        set(user_groups) & set(coll.change_groups.all())
    )
    coll_access = coll.user_access(request.user) or coll_change

    # 5) Render ONLY the partial template "fiches/workspace/collection.html"
    #    The old code typically loaded this partial dynamically or in a <div> via JS.
    context = {
        'coll': coll,
        'coll_list': coll_list,
        'shared_coll': shared_coll,
        'contrib_coll': contrib_coll,
        'coll_change': coll_change,
        'coll_access': coll_access,
        # If your template or JS needs these:
        'coll_id': coll_id,
        'coll_slug': coll_slug,
        'selected_tab_id': 'collection',
        'form': PasswordChangeForm(user=request.user),
    }
    return render(request, 'fiches/workspace/collection.html', context)


@permission_required("fiches.change_activitylog")
def last_activities(request):
    last_activities = ActivityLog.objects.order_by('-date')[:100]
    return render(request, 'fiches/workspace/last_activities.html', { 'last_activities': last_activities } )

def presentation(request, what="projet"):
    """
    Presentation page
    """
    if what == 'activites':
        title = 'Nos activités'
        page = 'activities'
    elif what == 'qui-sommes-nous':
        title = 'Qui sommes-nous ?'
        page = 'who-are-we'
    elif what == 'partenaires':
        title = 'Partenaires'
        page = 'partners'
    else:
        title = 'Projet Lumières.Lausanne'
        page = 'project'

    content = FreeContent.objects.get_content("presentation>" + page)
    context = { "content": content, "title": title }
    return render(request, "fiches/display/presentation.html", context)

def debug_test(request):
    """
    Pour test et debug
    """
    assert False, "Pour tester"
    return HttpResponse("empty")	


from .bibliography import *
from .biography import *
from .transcription import *

