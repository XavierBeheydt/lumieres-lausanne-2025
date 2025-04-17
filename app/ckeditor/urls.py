from django.conf.urls import url
from ckeditor import views as ckeditor_views

urlpatterns = [
    #'',
    url(r'^upload/', ckeditor_views.upload, name='ckeditor_upload'),
    url(r'^browse/', ckeditor_views.browse, name='ckeditor_browse'),
]
