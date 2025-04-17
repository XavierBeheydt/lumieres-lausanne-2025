# fiches/models/contributiontype.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class ContributionType(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    code = models.IntegerField(_("Code"), unique=True)
    type = models.CharField(_("Type"), max_length=10)  # e.g., 'doc', 'any'

    def __str__(self):
        return self.name

    # Define constants for easier reference
    PUBLISHER_ID = 4
    TRANSLATOR_ID = 3
    DIRECTOR_ID = 7
    AUTHOR_CODE = 0
