# models/attached_document.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from os.path import basename

class AttachedDocument(models.Model):  # Renamed from Document
    title = models.CharField(_("Titre"), max_length=250, blank=True)
    file = models.FileField(_("Fichier"), upload_to="files/%Y/%m")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        if self.title:
            return self.title
        return basename(self.file.name)
