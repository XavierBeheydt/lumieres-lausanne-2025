from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.forms import ModelForm, Textarea
from django.db.models.fields.related import ManyToManyField
from django.apps import apps  # For lazy imports

from fiches.models.contributions.ac_model import ACModel
from fiches.models.core.user_group import UserGroup
from fiches.models.person import Person


class ObjectCollection(ACModel):
    name = models.CharField(_("Nom de la collection"), max_length=125)
    slug = models.SlugField(editable=False, blank=True, null=True, unique=True)
    description = models.TextField(_("Description"), blank=True)
    owner = models.ForeignKey(
        User, verbose_name=_("Utilisateur"), related_name='objectcollections', on_delete=models.CASCADE
    )
    change_groups = models.ManyToManyField(
        UserGroup, verbose_name=_("Groupes contributeurs"), related_name='objectcollections', blank=True
    )
    access_private = models.BooleanField(
        blank=True, default=True, verbose_name=_("Privé"),
        help_text=_("Accessible pour le propriétaire seulement")
    )

    # Fields for related objects
    persons = models.ManyToManyField(Person, related_name='objectcollections', blank=True)
    # Use lazy references for Biblio and Transcription
    bibliographies = models.ManyToManyField(
        'fiches.Biblio', blank=True
    )
    transcriptions = models.ManyToManyField(
        'fiches.Transcription', blank=True
    )

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")
        ordering = ['id']

    def __str__(self):
        return str(self.name)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        nb_existing_slug = 0
        if not self.slug:
            if self.name:
                slug_candidate = slugify(self.name)[:50]
                nb_existing_slug = ObjectCollection.objects.filter(slug=slug_candidate).count()
                self.slug = slug_candidate
            else:
                self.slug = None
        super().save(force_insert=force_insert, force_update=force_update, *args, **kwargs)

        if nb_existing_slug > 0:
            old_slug = self.slug
            obj_id = str(self.id)
            new_slug = f"{old_slug}-{obj_id}"
            if len(new_slug) > 50:
                new_slug = f"{old_slug[:50 - len(obj_id) - 1]}-{obj_id}"
            self.slug = new_slug
            super().save(force_insert=force_insert, force_update=force_update, *args, **kwargs)

    def add_object(self, obj):
        of = self.get_object_field(obj)
        if of:
            of.add(obj)

    def remove_object(self, obj):
        of = self.get_object_field(obj)
        if of:
            of.remove(obj)

    def get_object_field(self, obj):
        # Retrieve ManyToMany fields excluding 'access_groups' from ACModel if it exists
        object_fields_names = [
            f.attname for f in self._meta.get_fields()
            if isinstance(f, ManyToManyField) and f.attname != 'access_groups'
        ]

        for f in object_fields_names:
            obj_field = getattr(self, f)
            if obj_field.model == obj.__class__:
                return obj_field
        return None
