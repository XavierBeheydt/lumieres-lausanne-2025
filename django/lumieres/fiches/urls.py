# fiches/urls.py

from django.urls import path, re_path
from fiches.views import (
    main_index,
    ajax_search,
    last_activities,
    serve_documentfile,
    documentfile_frame_list,
    documentfile_frame_create,
    documentfile_frame_edit,
    workspace_collections,
    transcription as views_transcription,
    collections as views_collections,
)
from fiches.views.search import biblio_extended_search, filter_builder
from fiches.views.biography import (
    display as biography_display,
    delete as biography_delete,
    edit as biography_edit,
    create as biography_create,
    to_be_validated as biography_to_be_validated,
    validate as biography_validate,
    relations_list as biography_relations_list,
    person_without_bio as biography_person_without_bio,
)
from fiches.views.bibliography import (
    display as bibliography_display,
    edit as bibliography_edit,
    delete as bibliography_delete,
    create as bibliography_create,
    endnote as bibliography_endnote,
    documentfile_change_list as bibliography_documentfile_change_list,
    documentfile_add as bibliography_documentfile_add,
    documentfile_remove as bibliography_documentfile_remove,
    get_person_publications as bibliography_get_person_publications,
    display_man as bibliography_display_man,
)

#app_name = 'fiches'

urlpatterns = [
    # Home Page (relative to 'fiches/' prefix)
    path('', main_index, name="home"),
    
    # AJAX Search
    path('ajax_search/', ajax_search, name='ajax-search'),

    # Last Activities
    path('last_activities/', last_activities, name="last-activities-list"),

    # Bibliography URLs
    path('biblio/', biblio_extended_search, name='bibliography-index'),
    path('biblio/ref/', biblio_extended_search, name='bibliography-references'),
    path('biblio/<int:doc_id>/', bibliography_display, name='display-bibliography'),
    path('biblio/edit/<int:doc_id>/', bibliography_edit, name='bibliography-edit'),
    path('biblio/delete/<int:doc_id>/', bibliography_delete, name='bibliography-delete'),
    re_path(r'^biblio/new/(?:(?:type_(?P<doctype>[1-5])/))?$', bibliography_create, name='bibliography-create'),
    path('biblio/endnote/<int:doc_id>/', bibliography_endnote, name="endnote-biblio-one"),
    path('biblio/endnote/', bibliography_endnote, {'getid': True, 'doc_id': None}, name="endnote-biblio-list"),
    path('biblio/documents/change_list/<int:doc_id>/', bibliography_documentfile_change_list, name="bibliography-documentfile-change-list"),
    re_path(r'^biblio/(?P<doc_id>\d+)/document/(?P<docfile_id>\d+)/add/$', bibliography_documentfile_add, name="bibliography-documentfile-add"),
    re_path(r'^biblio/(?P<doc_id>\d+)/document/(?P<docfile_id>\d+)/remove/$', bibliography_documentfile_remove, name="bibliography-documentfile-remove"),
    path('biblio/person/<int:person_id>/', bibliography_get_person_publications, name='get-person-publications'),

    # Biography URLs
    path('bio/', filter_builder, {'model_name': 'Person'}, name='biography-index'),
    path('bio/a_valider/', filter_builder, {'model_name': 'Person'}, name='biography-2b-validated'),
    path('bio/need_validation/', biography_to_be_validated, name='biography-need-validation-list'),
    path('bio/list/', filter_builder, {'model_name': 'Person'}, name='biography-list'),
    re_path(r'^bio/(?P<person_id>\d+)/(?:v/(?P<version>\d+))?$', biography_display, name='biography-display'),
    re_path(r'^bio/edit/(?P<person_id>\d+)/(?:v/(?P<version>\d+))?$', biography_edit, name='biography-edit'),
    re_path(r'^bio/delete/(?P<person_id>\d+)/(?:v/(?P<version>\d+))?$', biography_delete, name='biography-delete'),
    re_path(r'^bio/validate/(?P<person_id>\d+)/v/(?P<version>\d+)?$', biography_validate, name='biography-validate'),
    path('bio/new/<int:person_id>/', biography_create, name='biography-create'),
    path('bio/<int:person_id>/relations/', biography_relations_list, name='biography-relations-list'),
    path('bio/pfnb/', biography_person_without_bio, name='persons-for-new-biography'),

    # Manuscript URLs
    path('man/<int:man_id>/', bibliography_display_man, name="manuscript-display"),

    # Transcription URLs
    path('trans/', views_transcription.index, name='transcription-index'),
    path('trans/list/', views_transcription.index, name='transcription-list'),
    path('trans/<int:trans_id>/', views_transcription.display, name='transcription-display'),
    path('trans/edit/<int:trans_id>/', views_transcription.edit, name='transcription-edit'),
    path('trans/new/<int:doc_id>/', views_transcription.create, name='transcription-b-add'),
    path('trans/delete/<int:trans_id>/', views_transcription.delete, name='transcription-delete'),

    # Document URLs
    re_path(r'^documents/get/(?P<documentfile_key>[a-zA-Z0-9_-]+)/$', serve_documentfile, name="serve-file"),
    re_path(r'^documents/download/(?P<documentfile_key>[a-zA-Z0-9_-]+)/$', serve_documentfile, {'attachment': True}, name="download-file"),
    path('document/f_list/', documentfile_frame_list, name="docfile-frame-list"),
    path('document/f_create/', documentfile_frame_create, name="docfile-frame-create"),
    path('document/f_create/<int:docfile_id>/done/', documentfile_frame_create, {'create_done': True}, name="docfile-frame-create-done"),
    re_path(r'^document/f_edit/(?P<docfile_id>\d+)/$', documentfile_frame_edit, name="docfile-frame-edit"),
    path('document/f_edit/<int:docfile_id>/done/', documentfile_frame_edit, {'edit_done': True}, name="docfile-frame-edit-done"),

    # Collections URLs

    # 1. Fixed underscore‑prefixed URLs (these are exact matches)
    path('collection/_new/', views_collections.edit, {'coll_id': '#', 'create_coll': True}, name='collection-new'),
    path('collection/_edit/<int:coll_id>/', views_collections.edit, name='collection-edit'),
    path('collection/_saved/<int:coll_id>/', views_collections.edit, {'coll_saved': True}, name='collection-saved'),
    path('collection/_delete/<int:coll_id>/', views_collections.delete, name='collection-delete'),
    path('collection/_list/json/', views_collections.get_user_list, {'format': 'json'}, name='collection-user-list-json'),
    path('collection/_list/', views_collections.get_user_list, {'format': 'select'}, name='collection-user-list-select'),
    path('collection/_incollection/', views_collections.get_in_collection_list, name='collection-in-collection-list'),
    path('collection/_add-object/', views_collections.add_object, name='collection-add-object'),
    path('collection/_remove-object/', views_collections.remove_object, name='collection-remove-object'),
    path('collection/_display/<int:coll_id>/', views_collections.display, name='collection-display'),
    re_path(r'^collection/_display_short/(?P<coll_id>\d+)/$', views_collections.short_info, name='collection-shortinfo'),
    path('collection/_display/<int:coll_id>/popup/', views_collections.display_popup, name='collection-display-popup'),

    # 2. Tab index URLs (if you need them before general ones)
    re_path(r'^collection/t/(?:(?P<coll_id>\d+)/)?$', views_collections.tab_index, name='tab-collection-index'),
    path('collection/t/<slug:coll_slug>/', views_collections.tab_index, name='tab-named-collection-index'),

    # 3. Popup URLs based on slug or id for display (more specific than generic views)
    path('collection/<slug:coll_slug>/popup/', views_collections.display_popup, name='named-collection-display-popup'),
    path('collection/<int:coll_id>/popup/', views_collections.display_popup, name='named-collection-display-popup'),

    # 4. Generic collection display/index URLs
    re_path(r'^collections?/(?:(?P<coll_id>\d+)/)?$', workspace_collections, name='collection-index'),
    path('collection/<slug:coll_slug>/', workspace_collections, name='named-collection-index'),

]
