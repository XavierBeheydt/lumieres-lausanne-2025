# models/free_content.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor.fields import RichTextField

from fiches.models.content.image import Image
from fiches.models.documents.document import Document

class FreeContentManager(models.Manager):
    def get_content(self, name):
        try:
            return self.get(name=name)
        except:
            return None

class FreeContent(models.Model):
    name            = models.CharField(_("Nom"), unique=True, max_length=200)
    title           = models.CharField(_("Titre"), max_length=200)

    created_on      = models.DateTimeField(verbose_name='créé le', auto_now_add=True)
    modified_on     = models.DateTimeField(verbose_name='modifié le', auto_now=True)
    author          = models.ForeignKey(User, verbose_name=_("Auteur"), on_delete=models.SET_NULL, null=True, blank=True)

    content         = RichTextField(verbose_name=_("Contenu"), config_name='project_ckeditor', blank=True)

    images          = GenericRelation(Image)
    documents       = GenericRelation(Document)

    objects         = FreeContentManager()

    class Meta:
        verbose_name = _("Contenu libre")
        verbose_name_plural = _("Contenus libres")
        ordering = ['title']

    def __str__(self):
        return self.title
