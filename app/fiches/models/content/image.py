# fiches/models/content/image.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from os.path import basename

class Image(models.Model):
    legend = models.TextField(_("Légende"), blank=True)
    image = models.ImageField(upload_to="images/%Y/%m")
    link = models.URLField(_("Lien"), blank=True)
    pos = models.IntegerField(_("Position"), blank=True, null=True)  # Added null=True
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return basename(self.image.name) if self.image and self.image.name else "No image"

    class Meta:
        ordering = ('pos',)
