# lumieres/urls.py

from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from fiches.admin import fiches_admin
from fiches import views as fiches_views

from django.contrib.auth.forms import PasswordChangeForm

import os  # Required for os.path.join

# Custom Password Change Form with autocomplete disabled
class MyPasswordChangeForm(PasswordChangeForm):
    pass

MyPasswordChangeForm.base_fields['old_password'].widget.attrs['autocomplete'] = 'off'
MyPasswordChangeForm.base_fields['new_password1'].widget.attrs['autocomplete'] = 'off'
MyPasswordChangeForm.base_fields['new_password2'].widget.attrs['autocomplete'] = 'off'

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    path('fiches_admin/', fiches_admin.urls, name="fiches_admin"),

    # CKEditor URLs
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Authentication URLs using Django's built-in class-based views
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name="registration/login2.html"),
        name='login-page'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(template_name='registration/logged_out2.html'),
        name='logout-page'
    ),
    path(
        'accounts/change_password/',
        auth_views.PasswordChangeView.as_view(
            template_name="fiches/workspace/main.html",
            form_class=MyPasswordChangeForm,
            success_url='/accounts/change_password_done/'
        ),
        name='change-password-page'
    ),
    path(
        'accounts/change_password_done/',
        auth_views.PasswordChangeDoneView.as_view(template_name="fiches/workspace/main.html"),
        name='password_change_done'
    ),
    path(
        'accounts/reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url='/accounts/reset_password_done/'
        ),
        name='reset-password-page'
    ),
    path(
        'accounts/reset_password_done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'accounts/reset_password_confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/accounts/reset_password_complete/'
        ),
        name='password_reset_confirm'
    ),
    path(
        'accounts/reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'
    ),

    # Home Page
    path('', fiches_views.main_index, name="lumieres-home"),

    # Static About Page
    path('a_propos/', TemplateView.as_view(template_name="fiches/about.html"), name="about"),

    # Include App-specific URLs
    path('fiches/', include('fiches.urls')),
    path('projets/', include('fiches.urls_project')),
    path('publications/', include('fiches.urls_publication')),
    path('actualites/', include('fiches.urls_news')),
    path('presentation/<str:what>/', fiches_views.presentation, name="presentation"),
    path('espace_de_travail/', include('fiches.urls_workspace')),
    path('chercher/', include('fiches.urls_search')),

    # Test Debug View
    path('testdebug/', fiches_views.debug_test, name='test-debug'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^user-media/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'media', 'user_uploads'),
            'show_indexes': True
        }),
        re_path(r'^site-media/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'static'),
            'show_indexes': True
        }),
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True
        }),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler500 = 'fiches.views.server_error'
