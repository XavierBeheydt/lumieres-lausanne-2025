from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor.fields import RichTextField

from fiches.models.core.user_group import UserGroup
from fiches.models.content.image import Image


class Project(models.Model):
    name = models.CharField(_("Nom"), max_length=125)
    url = models.SlugField(
        _("Url"),
        db_index=True,
        unique=True,
        help_text=_("ATTENTION, doit être unique. Uniquement caractères non-accentués, tiret et chiffres. Pas d'espaces ni de ponctuation.")
    )
    description = RichTextField(config_name='project_ckeditor', verbose_name=_("Description"), blank=True)
    short_desc = models.CharField(
        _("Description courte"),
        max_length=250,
        blank=True,
        help_text=_("Texte utilisé dans la liste des projets. <strong>250 signes maximum.</strong> Si le champ est vide, le texte de description normal sera utilisé, tronqué à 250 signes")
    )
    image = models.ImageField(
        verbose_name=_("Vignette"),
        upload_to='user_uploads/%Y/%m',
        blank=True
    )

    publish = models.BooleanField(
        _("Publié"),
        default=False,
        help_text=_("Cocher pour donner un accès public. Sinon, accès limité au propriétaire et aux membres")
    )

    owner = models.ForeignKey(User, verbose_name=_("Propriétaire"), on_delete=models.CASCADE)
    members = models.ManyToManyField(User, verbose_name=_("Membres"), related_name='member_projects', blank=True)
    access_groups = models.ManyToManyField(UserGroup, verbose_name=_("Groupes"), related_name='group_projects', blank=True)

    persons = models.ManyToManyField('fiches.Person', related_name='projects', blank=True)
    bibliographies = models.ManyToManyField('fiches.Biblio', blank=True)
    transcriptions = models.ManyToManyField('fiches.Transcription', blank=True)

    images = GenericRelation(Image)
    documents = GenericRelation('fiches.Document')  # Lazy import for Document

    class Meta:
        app_label = "fiches"
        permissions = (("view_unpublished_project", "Peut voir un projet non publié"),)
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['id']

    def __str__(self):
        return str(self.name)

    def is_editable(self, user):
        if user in self.members.all() or user == self.owner:
            return True

        all_users = set()
        all_groups = set()
        for ug in self.access_groups.all():
            all_users |= set(ug.users.all())
            all_groups |= set(ug.groups.all())

        if (user in all_users) or (set(user.groups.all()) & all_groups):
            return True
        return False

    def add_object(self, obj):
        of = self.get_object_field(obj)
        if of:
            of.add(obj)

    def remove_object(self, obj):
        of = self.get_object_field(obj)
        if of:
            of.remove(obj)

    def get_object_field(self, obj):
        from django.db.models.fields.related import ManyToManyField
        object_fields_names = [
            f.name for f in self._meta.get_fields()
            if isinstance(f, ManyToManyField) and f.name not in ('access_groups', 'members')
        ]

        for field_name in object_fields_names:
            obj_field = getattr(self, field_name)
            if obj_field.model == obj.__class__:
                return obj_field
        return None

    def get_transcriptions(self, user):
        from django.db.models import Q
        q = Q(manuscript_b__project=self) & Q(manuscript_b__litterature_type='p')
        if not user.is_authenticated:
            q = q & Q(access_public=True)
        else:
            if not (user.has_perm('fiches.access_unpublished_transcription') or self.is_editable(user)):
                q = q & (
                    Q(access_public=True) |
                    Q(author=user) |
                    Q(author2=user) |
                    Q(access_groups__users=user) |
                    Q(access_groups__groups__user=user) |
                    (Q(access_public=False) & Q(access_private=False) & Q(access_groups__isnull=True))
                )
        from fiches.models.documents.document import Transcription  # Lazy import
        return Transcription.objects.filter(q).distinct()
