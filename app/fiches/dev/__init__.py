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

import re, os, os.path
from fiches.models import *
from django.db.models import Count
from django.conf import settings

def renum_all_bio_vers(dry_run=True, verbose=True):
    pl = Person.past_people.annotate(nb_bio=Count('biography')).filter(nb_bio__gt=0)
    for p in pl:
        p.renum_bio(dry_run=True, verbose=True)


def create_docfile_from_urls(dry_run=True, verbose=False):
    nl_re = re.compile(r'''[\n\r]+''')
    http_re = re.compile(r'''(https?://)''')
    biblio_list = Biblio.objects.filter(urls__isnull=False).exclude(urls__exact="")
    for biblio in biblio_list:
        url_list = nl_re.split(biblio.urls)
        for url_entry in url_list:
            if http_re.search(url_entry):
                (url_title, url_protocol, url_url) = http_re.split(url_entry)
                url_title = url_title.strip(':- ')
                df = DocumentFile(title=url_title, url=url_protocol + url_url)
                if not dry_run:
                    df.save()
                    biblio.documentfiles.add(df)
                if verbose:
                    print (u"Create DocumentFile: title=«%s», url=«%s»" % (url_title, url_protocol + url_url))
    
    parse_docfile_url(dry_run=dry_run, verbose=verbose)


def create_docfile_from_manuscript_urls(dry_run=True, verbose=False):
    nl_re = re.compile(r'''[\n\r]+''')
    http_re = re.compile(r'''(https?://)''')
    biblio_list = Manuscript.objects.filter(urls__isnull=False).exclude(urls__exact="")
    for biblio in biblio_list:
        url_list = nl_re.split(biblio.urls)
        for url_entry in url_list:
            if http_re.search(url_entry):
                (url_title, url_protocol, url_url) = http_re.split(url_entry)
                url_title = url_title.strip(':- ')
                df = DocumentFile(title=url_title, url=url_protocol + url_url)
                if not dry_run:
                    df.save()
                    biblio.documentfiles.add(df)
                if verbose:
                    print (u"Create DocumentFile: title=«%s», url=«%s»" % (url_title, url_protocol + url_url))
    
    parse_docfile_url(dry_run=dry_run, verbose=verbose)
    

def parse_docfile_url(dry_run=True, verbose=True):
    from django.db import connections
    original_cursor = connections['original'].cursor()
    
    re_prive = re.compile(r'http://www2.unil.ch/lumieres/uploads-prive/(.*)')
    re_proct = re.compile(r'http://www2.unil.ch/lumieres/admin/download.php\?id=(.*)')
    
    def get_doc_title(file_name):
        new_title = file_name
        if new_title.find(os.path.extsep)>0:
            new_title = " ".join(new_title.split(os.path.extsep)[:-1]).strip()
        new_title = new_title.replace('_', ' ')
        return new_title
    
    df_list = DocumentFile.objects.all()
    original_cursor.execute('SELECT file_id,path,access_level FROM `lumie_original`.`fichiers`;')
    rows = original_cursor.fetchall()
    original_files = {}
    for f in rows:
        original_files[f[0]] = f[1:]
    
    nb_modified_df = 0
    for df in df_list:
        df_modified = False
        if df.url:
            # ----- content of uploads-prive -----
            r_prive = re_prive.match(df.url)
            if r_prive:
                file_name = r_prive.groups()[0]
                if df.title == '':
                    df.title = get_doc_title(file_name)
                df.file.name = 'documents/pre/uploads-prive/%s' % file_name
                
                df.url = ''
                df_modified = True
            
            # ----- content of protected-files -----
            r_proct = re_proct.match(df.url)
            if r_proct:
                file_id = r_proct.groups()[0]
                file_rec = original_files.get(file_id)
                if file_rec:
                    file_name = file_rec[0][27:]
                    if df.title == '':
                        df.title = get_doc_title(file_name)
                        
                    df.file.name = 'documents/pre/protected-files/%s' % file_name
                    df.url = ''
                    df_modified = True
                elif verbose:
                    print (u"Unable to find file_id «%s»" % file_id)
            
            # ----- save modification -----
            if df_modified:
                nb_modified_df += 1
                if not dry_run:
                    df.save()
                if verbose:
                    print (u"Save DocumentFile: id=«%s» title=«%s», file=«%s»" % (df.id, df.title, df.file ))
    
    if verbose:
        print ("%s df modified" % nb_modified_df)
        

def setup_user_dates():
    import time
    from django.contrib.auth.models import User
    u_list = User.objects.filter(date_joined__isnull=True)
    for u in u_list:
        u.date_joined = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        u.last_login  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(0)) 
        u.save()
    
   
#def post_migrate_processing():
#    re_endNameDates = re.compile(r'\(\d{4}-\d{4}\)');
#    
#    person_list = Person.objects.all()
#    for p in person_list:
#        if re_endNameDates.search(p.name.strip()):
#            p.name = re_endNameDates.sub('', p.name.strip()).strip()
#            p.save()
#            
#    # Populate biblio's first_author
#    b_list = Biblio.objects.all()
#    for b in b_list:
#        try:
#            b.first_author      = b.contributiondoc_set.filter(contribution_type__code=0).order_by('pk')[0].person
#            b.first_author_name = b.first_author.name
#            b.save()
#        except:
#            b.first_author = None
#            b.first_author_name = None
#            
#    create_docfile_from_urls(dry_run=False, verbose=False)
#    
#    setup_user_dates()
#    
#    

def merge_all_manuscripts():
    manuscripts = Manuscript.objects.all()
    for man in manuscripts:
        merge_manuscript(man.id)

def clear_merged_manuscripts():
    for b in Biblio.objects.filter(document_type=5):
        print ("Delete Biblio %s" % b.id)
        b.delete()

from django.db import connection, transaction
def merge_manuscript(pk=None):
    if pk is None: 
        raise Exception("give the pk of the Manuscript to merge")
    
    man = Manuscript.objects.get(pk=pk)
    
    # =============
    # Simple Fields
    # =============
    
    # ----- common fields (present in both objects)
    common_fields = ('title', 'short_title', 'abstract', 'place', 'date', 'date_f', 
                    'pages', 'access_date', 'depot', 'cote', 'authorization', 'extra', 'creator', 'first_author')
    man_data = dict([(f, getattr(man, f)) for f in common_fields])
    
    # ----- fields newly added to Biblio
    new_fields = ('inscription', 'manuscript_type')
    man_data.update( dict([(f, getattr(man, f)) for f in new_fields]) )
    
    # ----- fields with different names in Biblio
    map_fields = ( ('lang_main', 'language'), ('lang_sec', 'language_sec'), )
    man_data.update( dict([(b_f, getattr(man, m_f)) for m_f,b_f in map_fields]) )
    
    # ----- Static values
    doctype = DocumentType.objects.get(pk=5)
    man_data.update(document_type=doctype, litterature_type='p')
    
    
    # =====================
    # CREATE the new Object
    # =====================
    biblio = Biblio(**man_data)
    biblio.save()
    man.biblio_man = biblio
    man.save()
    
    
    # =================
    # ManyToMany fields
    # =================
    
    # ----- Authors
    man_contribs = man.contributionman_set.all()
    for man_contrib in man_contribs:
        doc_contrib = ContributionDoc.objects.create(
                            person = man_contrib.person,
                            document = biblio,
                            contribution_type = man_contrib.contribution_type
                      )
    
    # ----- DocumentFiles
    biblio.documentfiles.add(*man.documentfiles.all())
    
    # ----- Keywords
    biblio.subj_primary_kw.add(*man.subj_primary_kw.all())
    biblio.subj_secondary_kw.add(*man.subj_secondary_kw.all())
    
    # ----- Society
    biblio.subj_society.add(*man.subj_society.all())
    
    # ----- Notes
    man_notes = man.notemanuscript_set.all()
    for man_note in man_notes:
        biblio_note = NoteBiblio.objects.create(owner=biblio, text=man_note.text, access_public=man_note.access_public, access_owner=man_note.access_owner)
        biblio_note.access_groups.add(*man_note.access_groups.all())
    
    # ----- Collections
    man_collecs = man.objectcollection_set.all()
    for man_collec in man_collecs:
        man_collec.bibliographies.add(biblio)
    
    
    # ----- Transcriptions
    man_transcriptions = man.transcription_set.all()
    for trans in man_transcriptions:
        trans.manuscript_b = biblio
        trans.save()
    
    
    # ============
    # Activity Log
    # ============
    
    model_name = biblio.__class__.__name__
    a_logs = ActivityLog.objects.filter(object_id=man.id, model_name=man.__class__.__name__)
    if a_logs.count() > 0:
        values = ",".join(
                    [ "".join(
                        ('(', 
                         ",".join(("%s" % biblio.id, "'%s'" % model_name, "%s" % a.user_id, "'%s'" % a.date, "1" if a.p_orphan else "0")),
                         ')')
                        ) for a in a_logs
                    ]
        )
        
        cursor = connection.cursor()
        query = """INSERT INTO `fiches_activitylog` 
          (`object_id`, `model_name`, `user_id`, `date`, `p_orphan`) VALUES
          %s;
        """ % values
        
        print (query)
        
        cursor.execute(query)
        transaction.commit_unless_managed()
    
    print ("Biblio id %s, created from Manuscript id %s" % (biblio.id, man.id))



# ===========================
# Permission management tools
# ===========================
# These are used to serialize the group permissions
# in a id-independant way.
# This is absolutely useless, as the -n flag of the dumpdata management
# comand, handles it already. And certainly in a better way.
# RTFM, Julien, RTFM.
# No, you are a bit rude. This is still usfull. a little bit






DEFAULT_GROUP_PERMS = {
u'__test__': [(u'fiches', u'add_project'),
               (u'fiches', u'change_project'),
               (u'fiches', u'delete_project'),
               (u'fiches', u'view_unpublished_project')],
 u'assistants': [(u'fiches', u'add_activitylog'),
                 (u'fiches', u'add_biblio'),
                 (u'fiches', u'can_add_listitem'),
                 (u'fiches', u'change_any_biblio'),
                 (u'fiches', u'change_biblio'),
                 (u'fiches', u'change_biblio_ownership'),
                 (u'fiches', u'delete_any_biblio'),
                 (u'fiches', u'delete_biblio'),
                 (u'fiches', u'access_unvalidated_biography'),
                 (u'fiches', u'add_biography'),
                 (u'fiches', u'browse_biography_versions'),
                 (u'fiches', u'change_biography'),
                 (u'fiches', u'validate_biography'),
                 (u'fiches', u'add_documentfile'),
                 (u'fiches', u'change_any_documentfile'),
                 (u'fiches', u'change_documentfile'),
                 (u'fiches', u'delete_any_documentfile'),
                 (u'fiches', u'delete_documentfile'),
                 (u'fiches', u'add_manuscript'),
                 (u'fiches', u'change_any_manuscript'),
                 (u'fiches', u'change_manuscript'),
                 (u'fiches', u'change_manuscript_ownership'),
                 (u'fiches', u'delete_any_manuscript'),
                 (u'fiches', u'delete_manuscript'),
                 (u'fiches', u'view_unpublished_project'),
                 (u'fiches', u'access_unpublished_transcription'),
                 (u'fiches', u'change_any_transcription'),
                 (u'fiches', u'delete_any_transcription'),
                 (u'fiches', u'can_see_all_usergroups')],
 u'directeurs': [(u'auth', u'add_user'),
                 (u'auth', u'change_user'),
                 (u'auth', u'delete_user'),
                 (u'fiches', u'add_activitylog'),
                 (u'fiches', u'change_activitylog'),
                 (u'fiches', u'delete_activitylog'),
                 (u'fiches', u'add_biblio'),
                 (u'fiches', u'can_add_listitem'),
                 (u'fiches', u'change_any_biblio'),
                 (u'fiches', u'change_biblio'),
                 (u'fiches', u'change_biblio_ownership'),
                 (u'fiches', u'delete_any_biblio'),
                 (u'fiches', u'delete_biblio'),
                 (u'fiches', u'access_unvalidated_biography'),
                 (u'fiches', u'add_biography'),
                 (u'fiches', u'browse_biography_versions'),
                 (u'fiches', u'change_biography'),
                 (u'fiches', u'delete_biography'),
                 (u'fiches', u'validate_biography'),
                 (u'fiches', u'add_contributiondoc'),
                 (u'fiches', u'change_contributiondoc'),
                 (u'fiches', u'delete_contributiondoc'),
                 (u'fiches', u'add_contributionman'),
                 (u'fiches', u'change_contributionman'),
                 (u'fiches', u'delete_contributionman'),
                 (u'fiches', u'add_contributiontype'),
                 (u'fiches', u'change_contributiontype'),
                 (u'fiches', u'delete_contributiontype'),
                 (u'fiches', u'add_documentfile'),
                 (u'fiches', u'change_any_documentfile'),
                 (u'fiches', u'change_documentfile'),
                 (u'fiches', u'delete_any_documentfile'),
                 (u'fiches', u'delete_documentfile'),
                 (u'fiches', u'add_documentlanguage'),
                 (u'fiches', u'change_documentlanguage'),
                 (u'fiches', u'delete_documentlanguage'),
                 (u'fiches', u'add_documenttype'),
                 (u'fiches', u'change_documenttype'),
                 (u'fiches', u'delete_documenttype'),
                 (u'fiches', u'add_journaltitleview'),
                 (u'fiches', u'change_journaltitleview'),
                 (u'fiches', u'delete_journaltitleview'),
                 (u'fiches', u'add_keyword'),
                 (u'fiches', u'change_keyword'),
                 (u'fiches', u'delete_keyword'),
                 (u'fiches', u'add_manuscript'),
                 (u'fiches', u'change_any_manuscript'),
                 (u'fiches', u'change_manuscript'),
                 (u'fiches', u'change_manuscript_ownership'),
                 (u'fiches', u'delete_any_manuscript'),
                 (u'fiches', u'delete_manuscript'),
                 (u'fiches', u'add_manuscripttype'),
                 (u'fiches', u'change_manuscripttype'),
                 (u'fiches', u'delete_manuscripttype'),
                 (u'fiches', u'add_nationality'),
                 (u'fiches', u'change_nationality'),
                 (u'fiches', u'delete_nationality'),
                 (u'fiches', u'add_notebiblio'),
                 (u'fiches', u'change_notebiblio'),
                 (u'fiches', u'delete_notebiblio'),
                 (u'fiches', u'add_notebiography'),
                 (u'fiches', u'change_notebiography'),
                 (u'fiches', u'delete_notebiography'),
                 (u'fiches', u'add_notemanuscript'),
                 (u'fiches', u'change_notemanuscript'),
                 (u'fiches', u'delete_notemanuscript'),
                 (u'fiches', u'add_notetranscription'),
                 (u'fiches', u'change_notetranscription'),
                 (u'fiches', u'delete_notetranscription'),
                 (u'fiches', u'add_objectcollection'),
                 (u'fiches', u'change_objectcollection'),
                 (u'fiches', u'delete_objectcollection'),
                 (u'fiches', u'add_person'),
                 (u'fiches', u'change_person'),
                 (u'fiches', u'delete_person'),
                 (u'fiches', u'add_placeview'),
                 (u'fiches', u'change_placeview'),
                 (u'fiches', u'delete_placeview'),
                 (u'fiches', u'add_primarykeyword'),
                 (u'fiches', u'change_primarykeyword'),
                 (u'fiches', u'delete_primarykeyword'),
                 (u'fiches', u'add_profession'),
                 (u'fiches', u'change_profession'),
                 (u'fiches', u'delete_profession'),
                 (u'fiches', u'add_project'),
                 (u'fiches', u'change_project'),
                 (u'fiches', u'delete_project'),
                 (u'fiches', u'view_unpublished_project'),
                 (u'fiches', u'add_relation'),
                 (u'fiches', u'add_reverserelation'),
                 (u'fiches', u'change_relation'),
                 (u'fiches', u'change_reverserelation'),
                 (u'fiches', u'delete_relation'),
                 (u'fiches', u'delete_reverserelation'),
                 (u'fiches', u'add_relationtype'),
                 (u'fiches', u'change_relationtype'),
                 (u'fiches', u'delete_relationtype'),
                 (u'fiches', u'add_religion'),
                 (u'fiches', u'change_religion'),
                 (u'fiches', u'delete_religion'),
                 (u'fiches', u'add_searchfilters'),
                 (u'fiches', u'change_searchfilters'),
                 (u'fiches', u'delete_searchfilters'),
                 (u'fiches', u'add_secondarykeyword'),
                 (u'fiches', u'change_secondarykeyword'),
                 (u'fiches', u'delete_secondarykeyword'),
                 (u'fiches', u'add_society'),
                 (u'fiches', u'change_society'),
                 (u'fiches', u'delete_society'),
                 (u'fiches', u'add_societymembership'),
                 (u'fiches', u'change_societymembership'),
                 (u'fiches', u'delete_societymembership'),
                 (u'fiches', u'access_unpublished_transcription'),
                 (u'fiches', u'add_transcription'),
                 (u'fiches', u'change_any_transcription'),
                 (u'fiches', u'change_transcription'),
                 (u'fiches', u'change_transcription_ownership'),
                 (u'fiches', u'delete_any_transcription'),
                 (u'fiches', u'delete_transcription'),
                 (u'fiches', u'publish_transcription'),
                 (u'fiches', u'add_usergroup'),
                 (u'fiches', u'can_see_all_usergroups'),
                 (u'fiches', u'change_usergroup'),
                 (u'fiches', u'delete_usergroup')],
 u'doctorants': [(u'fiches', u'add_biblio'),
                 (u'fiches', u'can_add_listitem'),
                 (u'fiches', u'change_any_biblio'),
                 (u'fiches', u'change_biblio'),
                 (u'fiches', u'delete_biblio'),
                 (u'fiches', u'access_unvalidated_biography'),
                 (u'fiches', u'add_biography'),
                 (u'fiches', u'browse_biography_versions'),
                 (u'fiches', u'change_biography'),
                 (u'fiches', u'add_documentfile'),
                 (u'fiches', u'change_documentfile'),
                 (u'fiches', u'delete_documentfile'),
                 (u'fiches', u'add_manuscript'),
                 (u'fiches', u'change_manuscript'),
                 (u'fiches', u'delete_manuscript'),
                 (u'fiches', u'add_transcription'),
                 (u'fiches', u'change_transcription'),
                 (u'fiches', u'delete_transcription')],
 u'editeurs_projet': [],
 u'experts': [(u'fiches', u'access_unpublished_transcription')],
 u'\xe9tudiants': [(u'fiches', u'add_biblio'),
                   (u'fiches', u'can_add_listitem'),
                   (u'fiches', u'change_biblio'),
                   (u'fiches', u'delete_biblio'),
                   (u'fiches', u'access_unvalidated_biography'),
                   (u'fiches', u'add_manuscript'),
                   (u'fiches', u'change_manuscript'),
                   (u'fiches', u'delete_manuscript'),
                   (u'fiches', u'add_transcription'),
                   (u'fiches', u'change_transcription'),
                   (u'fiches', u'delete_transcription')]
}




from django.contrib.auth.models import Group, Permission
def get_group_permissions():
    perm_dict = dict([
        ( g.name, 
            [ (p.content_type.app_label, p.codename) 
              for p in g.permissions.all()
            ] 
        ) 
        for g in Group.objects.all()
    ])
    
    return perm_dict

def check_group_permissions(perm_dict=DEFAULT_GROUP_PERMS, dry_run=True):
    """
    ATTENTION LA LISTE CI-DESSUS SEMBLE FAUSSE. A VERIFIER !!!!
    """
    dry_run = True
    for grp_name, target_perms in perm_dict.items():
        try:
            grp = Group.objects.get(name=grp_name)
        except:
            continue
        current_perms = [ (p.content_type.app_label, p.codename) for p in grp.permissions.all() ]
        
        target_perms_set = set(target_perms)
        current_perms_set = set(current_perms)
        
        if target_perms_set != current_perms_set:
            missing_perms_set = target_perms_set - current_perms_set
            for app_label, codename in missing_perms_set:
                try:
                    perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
                except Permission.DoesNotExist:
                    print ("Permission %(codename)s %(app_label)s doesnot exists." % {'codename': codename, 'app_label':app_label})
                    continue
                print ("Missing permission %r for group %r" % (perm, grp))
                if not dry_run:
                    print ("    add permission %r" % perm)
                    grp.permissions.add(perm)
            
            excess_perms_set = current_perms_set - target_perms_set
            for app_label, codename in excess_perms_set:
                perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
                print ("Excessive permission %r for group %r" % (perm, grp))
                if not dry_run:
                    print ("    remove permission %r" % perm)
                    grp.permissions.remove(perm)




def find_orphan_documents():
    df_list = DocumentFile.objects.raw('SELECT id,file FROM fiches_documentfile WHERE file != ""')
    linked_files = set([df.file.path for df in df_list])
    
    document_dir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'documents'))
    fs_file_list = []
    for root, dirs, files in os.walk(document_dir):
      if files:
        fs_file_list += [ os.path.join(root, f) for f in files ]
    fs_files = set(fs_file_list)
    
    return linked_files, fs_files

