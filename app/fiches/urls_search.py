from django.urls import path  # Ensure path is imported
from fiches.views.search import req_search_view, filter_builder, list_persons, do_search, save_settings, relations, transcriptions_change_access, biblio_extended_search

urlpatterns = [
    path('', req_search_view, name="search-index"),
    path('person/', filter_builder, {'model_name': 'Person'}, name="search-person"),
    path('person/list', list_persons, name="list-person"),
    path('bibliographie/', biblio_extended_search, name="search-biblio"),
    path('do/', do_search, name="do-search"),
    path('display_settings/save/', save_settings, name="save-settings"),
    path('person/relations/', relations, name="search-relations"),
    path('actions/changer-acces-transcriptions/', transcriptions_change_access, name="trans-change-access"),
]
