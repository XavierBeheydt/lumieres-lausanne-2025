# fiches/admin.py

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.urls import reverse as reverse_url
from django.forms import ModelForm, TextInput, CharField
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
import os

from django.contrib.contenttypes.admin import GenericStackedInline

from fiches.models.content.free_content import FreeContent
from fiches.models.content.news import News
from fiches.models.content.image import Image
from fiches.models.misc.project import Project
from fiches.models.content.publication import Publication
from fiches.models.content.finding import Finding

from fiches.models import (
    ContributionType, UserProfile, Person, PrimaryKeyword, SecondaryKeyword,
    Society, Biography, Biblio, Manuscript, Transcription, DocumentType,
    DocumentLanguage, DocumentFile, ObjectCollection, PlaceView, JournaltitleView, UserGroup,
    Nationality, RelationType, Religion, ManuscriptType, ActivityLog, Document,
    Relation
)
from fiches.forms import ObjectCollectionForm, BiblioForm

from ckeditor.widgets import CKEditorWidget  # Ensure CKEditor is up-to-date

# -----------------------------------------------------------------------------
# Custom Admin Site
# -----------------------------------------------------------------------------

class FichesAdminSite(AdminSite):
    site_header = "Fiches Administration"
    site_title = "Fiches Admin"
    index_title = "Welcome to the Fiches Admin"

fiches_admin = FichesAdminSite(name="fiches_admin")

# -----------------------------------------------------------------------------
# Inline Admin Classes
# -----------------------------------------------------------------------------

class ImageInlineForm(ModelForm):
    legend = CharField(label='Légende', widget=TextInput(attrs={'size': 150}))

    class Meta:
        model = Image
        fields = '__all__'

class ImageInline(GenericStackedInline):
    model = Image
    form = ImageInlineForm
    extra = 0

class DocumentInline(GenericStackedInline):
    model = Document
    extra = 0

# -----------------------------------------------------------------------------
# ModelAdmin Classes
# -----------------------------------------------------------------------------

class ContributionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'name', 'code')
    search_fields = ('type', 'name', 'code')
    list_filter = ('type',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'field_of_research', 'shib_uniqueID')
    search_fields = ('user__username', 'field_of_research', 'shib_uniqueID')
    list_filter = ('user__is_active', 'user__is_staff')
    ordering = ('user__username',)
    readonly_fields = ('user',)

class PersonAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class PrimaryKeywordAdmin(admin.ModelAdmin):
    list_display = ('word',)
    search_fields = ('word',)

class SecondaryKeywordAdmin(admin.ModelAdmin):
    list_display = ('word', 'primary_keyword')
    search_fields = ('word', 'primary_keyword__word')
    list_filter = ('primary_keyword',)

class SocietyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class BiblioAdmin(admin.ModelAdmin):
    form = BiblioForm
    list_display = ('title', 'document_type', 'language')
    search_fields = ('title', 'document_type__name', 'language__name')
    list_filter = ('document_type', 'language')

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    list_display_links = ('name',)
    ordering = ('id',)
    search_fields = ('name',)

class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ('file',)
    search_fields = ('file__name',)

    def file_link(self, obj):
        if obj.file and obj.file.name:
            return format_html('<a href="{}">{}</a>', obj.get_absolute_url(), os.path.basename(obj.file.name))
        return "No file available"
    file_link.short_description = "File Link"

    def view_on_site(self, obj):
        return obj.get_absolute_url()

class FindingAdmin(admin.ModelAdmin):
    list_display = ('description',)
    search_fields = ('description',)

    def save_model(self, request, obj, form, change):
        obj.save()

class FreeContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'title', 'author', 'created_on', 'modified_on')
    list_display_links = ('name', 'title')
    search_fields = ('name', 'title', 'author__username')
    list_filter = ('created_on', 'modified_on', 'author')
    ordering = ('id',)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'content')

class ObjectCollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PlaceView)
class PlaceViewAdmin(admin.ModelAdmin):
    list_display = ('biblio', 'place_name')
    search_fields = ('biblio__title', 'place_name')
    list_filter = ('place_name',)
    ordering = ('place_name',)

from django.contrib import admin
from .models import JournaltitleView

@admin.register(JournaltitleView)
class JournaltitleViewAdmin(admin.ModelAdmin):
    list_display = ('journal_title',)
    search_fields = ('journal_title',)


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class NationalityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class RelationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'reverse_name', 'sorting')

class ReligionAdmin(admin.ModelAdmin):
    list_display = ('name', 'sorting')
    search_fields = ('name',)
    list_editable = ('sorting',)
    ordering = ('sorting', 'id')

class ManuscriptTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sorting')
    search_fields = ('name',)
    list_editable = ('sorting',)
    ordering = ('sorting', 'id')

class ManuscriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'creator')
    search_fields = ('title', 'creator__username')
    list_filter = ('creator',)
    ordering = ('id',)

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'date')
    list_filter = ('model_name', 'date', )
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-date',)

class BiographyAdmin(admin.ModelAdmin):
    list_display = ('person',)
    search_fields = ('person__name', 'bio')
    list_filter = ('person',)

class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('id',)
    list_filter = ('status',)

# -----------------------------------------------------------------------------
# Image Admin Class (If Needed)
# -----------------------------------------------------------------------------

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'legend')
    search_fields = ('legend', 'image')
    ordering = ('id',)

# -----------------------------------------------------------------------------
# User and Group Admins
# -----------------------------------------------------------------------------

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Informations supplémentaires'
    fields = ('field_of_research', 'shib_uniqueID')

class FichesUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    list_filter = ('groups', 'is_staff', 'is_active', 'is_superuser')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'userActivities')
    list_per_page = 25

    def userActivities(self, obj):
        return format_html('<a href="{}">[ suivi ]</a>', reverse_url('fiches_admin:fiches_activitylog_changelist') + f'?user__id__exact={obj.id}')
    userActivities.short_description = "Suivi de l'activité"

class FichesGroupAdmin(GroupAdmin):
    pass

# -----------------------------------------------------------------------------
# Registering Models with Custom AdminSite
# -----------------------------------------------------------------------------

fiches_admin.register(ContributionType, ContributionTypeAdmin)
fiches_admin.register(UserProfile, UserProfileAdmin)
fiches_admin.register(Person, PersonAdmin)
fiches_admin.register(PrimaryKeyword, PrimaryKeywordAdmin)
fiches_admin.register(SecondaryKeyword, SecondaryKeywordAdmin)
fiches_admin.register(Society, SocietyAdmin)
fiches_admin.register(Biography, BiographyAdmin)
fiches_admin.register(Biblio, BiblioAdmin)
fiches_admin.register(ManuscriptType, ManuscriptTypeAdmin)  # Correctly registering ManuscriptType
fiches_admin.register(Manuscript, ManuscriptAdmin)          # Correctly registering Manuscript
fiches_admin.register(Transcription, TranscriptionAdmin)
fiches_admin.register(DocumentType, DocumentTypeAdmin)
fiches_admin.register(DocumentLanguage)                    # Assuming default admin
fiches_admin.register(DocumentFile, DocumentFileAdmin)
fiches_admin.register(Finding, FindingAdmin)
fiches_admin.register(FreeContent, FreeContentAdmin)
fiches_admin.register(Image, ImageAdmin)                    # Corrected registration
fiches_admin.register(News, NewsAdmin)
fiches_admin.register(ObjectCollection, ObjectCollectionAdmin)
fiches_admin.register(Project, ProjectAdmin)
fiches_admin.register(PlaceView, PlaceViewAdmin)
fiches_admin.register(JournaltitleView, JournaltitleViewAdmin)
fiches_admin.register(UserGroup, UserGroupAdmin)
fiches_admin.register(Nationality, NationalityAdmin)
fiches_admin.register(RelationType, RelationTypeAdmin)
fiches_admin.register(Religion, ReligionAdmin)
fiches_admin.register(ActivityLog, ActivityLogAdmin)
fiches_admin.register(Group, FichesGroupAdmin)

# -----------------------------------------------------------------------------
# End of `fiches/admin.py`
# -----------------------------------------------------------------------------
