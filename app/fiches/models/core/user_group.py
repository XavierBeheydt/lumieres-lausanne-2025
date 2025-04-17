# models/user_group.py

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
  
class UserGroup(models.Model):
    name        = models.CharField(_("Nom"), max_length=125)
    description = models.TextField(_("Description"), blank=True)
    users       = models.ManyToManyField(User, verbose_name=_("Utilisateurs"), blank=True)
    groups      = models.ManyToManyField(Group, verbose_name=_("Groupes"), blank=True)
    sort        = models.IntegerField(_("ordre de tri"), blank=True)

    class Meta:
        verbose_name = _("Groupe d'utilisateurs")
        verbose_name_plural = _("Groupes d'utilisateurs")
        ordering = ['sort']
        app_label = "fiches"

    def __str__(self):
        return str(self.name)
