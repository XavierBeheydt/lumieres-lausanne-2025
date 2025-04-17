# fiches/models/relation.py

from django.db import models
from django.utils.translation import gettext_lazy as _

# ===============================================================================
# RELATIONS
# ===============================================================================
class RelationType(models.Model):
    name = models.CharField(max_length=256)
    reverse_name = models.CharField(max_length=256)
    sorting = models.IntegerField(editable=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u'Type de relation'
        verbose_name_plural = u'Types de relation'
        app_label = "fiches"
        ordering = ['sorting']


class Relation(models.Model):
    """
    Pour obtenir les relations d'une personne p:
    rs = Relation.objects.filter(bio__person=p).extra(where=["1 GROUP BY related_person_id,relation_type_id"])
    """
    bio = models.ForeignKey(
        "fiches.Biography",
        on_delete=models.CASCADE
    )
    related_person = models.ForeignKey(
        "fiches.Person",
        verbose_name=_("Personne"),
        limit_choices_to={'modern': False},
        related_name='person_back',
        on_delete=models.CASCADE
    )
    relation_type = models.ForeignKey(
        "fiches.RelationType",  # <--- String reference (no import needed)
        verbose_name=_("Type de relation"),
        on_delete=models.CASCADE
    )

    def __str__(self):
        display_str = f"{self.related_person} ({self.relation_type})"
        # If `bio.valid` is a boolean that indicates validity:
        if not self.bio.valid:
            display_str += "*"
        return display_str

    def reverse_str(self):
        # Replaces old `self.person_to` with `self.related_person`
        # If `relation_type.reverse_name` exists on `RelationType`, we display it
        return f"{self.related_person} ({self.relation_type.reverse_name})"

    class Meta:
        app_label = "fiches"
        ordering = ("relation_type__sorting",)
