# models/society.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class Society(models.Model):
    name = models.CharField(_("Société/Académie"), max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Société/Académie")
        verbose_name_plural = _("Sociétés/Académies")
        ordering = ("name",)
        app_label = "fiches"
