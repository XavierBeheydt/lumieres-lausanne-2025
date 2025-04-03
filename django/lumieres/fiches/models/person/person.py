# models/person.py

import re
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from django.db.models import Q
from collections import OrderedDict

from fiches.models.person.relation import Relation

class ModernPeople(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(modern=True)

class PastPeople(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(modern=False)

class Person(models.Model):
    name = models.CharField(_("Nom"), max_length=215)
    # Replace NullBooleanField with BooleanField(null=True, blank=True)
    modern = models.BooleanField(_("Personne littérature secondaire"), null=True, blank=True)
    may_have_biography = models.BooleanField(_("Peut avoir une biographie"), default=True)

    # Managers
    people = models.Manager()
    modern_people = ModernPeople()
    past_people = PastPeople()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Personne")
        verbose_name_plural = _("Personnes")
        ordering = ['name']
        app_label = "fiches"

    def __str__(self):
        return self.name

    def format_for_ajax_search(self):
        out = self.name
        bio = self.get_biography()
        if bio and (bio.birth_date or bio.death_date):
            out += " ["
            if bio.birth_date:
                out += str(bio.birth_date.year)
            out += "-"
            if bio.death_date:
                out += str(bio.death_date.year)
            out += ']'
        out += f"|{self.pk}"
        return out

    def get_absolute_url(self):
        return reverse('biography-display', args=[str(self.id)])

    def has_biography(self):
        # Use the related manager instead of importing Biography
        return self.biography_set.exists()
    has_biography.short_description = _("Biographie ?")
    has_biography.boolean = True

    def _get_name_parts(self, part='first'):
        name_parts = re.compile(r',\s*').split(self.name)
        if len(name_parts) < 2:
            name_parts.append("")
        if part == 'first':
            return name_parts[0]
        elif part == 'last':
            return name_parts[1]
        else:
            raise ValueError("Unattended part value in Person._get_name_parts")

    def get_first_name(self):
        return self._get_name_parts('first')

    def get_last_name(self):
        return self._get_name_parts('last')

    def get_biography(self, version=0):
        """
        Return the current biography for the Person.
        The lowest version is returned and then the highest id.
        If no version specified or invalid, defaults to 0.
        """
        if version is None:
            version = 0
        else:
            try:
                version = int(version)
            except ValueError:
                version = 0

        if version < 0:
            version = 0

        try:
            return self.biography_set.get(version=version)
        except models.ObjectDoesNotExist:
            # If no biography with the given version, return the last created
            latest_bio = self.biography_set.all().order_by('-id').first()
            return latest_bio

    def get_valid_biography(self, version=0):
        """
        Return the validated biography for the Person.
        Return None if no valid biography found, but no errors
        """
        try:
            bio = list(self.biography_set.filter(valid=True).order_by('id')).pop()
        except:
            bio = None
        return bio



    def get_relations(self, only_people=None, exclude_people=None, only_relations=None):
        """
        Return a *deduplicated* list of Relation objects where:
        - relation.bio.person = self
        - biography is valid OR version=0
        - optionally filters by only_people, exclude_people, only_relations
        and we eliminate duplicates by (relation_type_id, related_person_id).
        """
        if only_people is None:
            only_people = []
        if exclude_people is None:
            exclude_people = []
        if only_relations is None:
            only_relations = []

        # 1) Base queryset filtering by person, valid or version=0
        qs = (
            Relation.objects
            .filter(bio__person=self)
            .filter(Q(bio__valid=True) | Q(bio__version=0))
            .select_related('relation_type', 'related_person')
            .order_by('relation_type__sorting', 'related_person_id', 'id')
        )

        # 2) Filter if needed
        if only_people:
            qs = qs.filter(related_person_id__in=only_people)
        if exclude_people:
            qs = qs.exclude(related_person_id__in=exclude_people)
        if only_relations:
            qs = qs.filter(relation_type_id__in=only_relations)

        # 3) Deduplicate in Python by (relation_type_id, related_person_id)
        unique_keys = set()
        results = []
        for r in qs:
            key = (r.relation_type_id, r.related_person_id)
            if key not in unique_keys:
                unique_keys.add(key)
                results.append(r)

        return results


    def get_reverse_relations(self, only_people=None, exclude_people=None, only_relations=None):
        """
        Return Relation rows where THIS Person is the `related_person_id`
        (the 'destination'), for all valid or 0-version Biographies.
        Mirrors the pattern of get_relations(), but reversed, WITHOUT raw SQL.
        """
        if only_people is None:
            only_people = []
        if exclude_people is None:
            exclude_people = []
        if only_relations is None:
            only_relations = []

        # Build a Q object with your conditions
        # (b.valid=True OR b.version=0) and (r.related_person_id = self.id)
        filters = Q(related_person_id=self.id) & (Q(bio__valid=True) | Q(bio__version=0))

        if only_people:
            filters &= Q(bio__person_id__in=only_people)
        if exclude_people:
            filters &= ~Q(bio__person_id__in=exclude_people)
        if only_relations:
            filters &= Q(relation_type_id__in=only_relations)

        # Run a normal ORM query
        # - Order by relation_type.sorting (then by ids if needed)
        qs = (
            Relation.objects.filter(filters)
            .select_related('bio', 'bio__person', 'relation_type')
            .order_by('relation_type__sorting', 'bio_id', 'related_person_id', 'id')
        )

        # Now deduplicate in Python by (bio_id, related_person_id, relation_type_id)
        unique_keys = set()
        results = []
        for rel in qs:
            key = (rel.bio_id, rel.related_person_id, rel.relation_type_id)
            if key not in unique_keys:
                unique_keys.add(key)
                results.append(rel)

        return results




