# -*- coding: iso-8859-1 -*-
#
#    Copyright (C) 2010-2012 Université de Lausanne, RISET
#    < http://www.unil.ch/riset/ >
#
#    This file is part of Lumières.Lausanne.
#    Lumières.Lausanne is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Lumières.Lausanne is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    This copyright notice MUST APPEAR in all copies of the file.
#

from django.db import models
from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.utils.dateformat import format
from django.apps import apps
from fiches.models.misc.notes import NoteBase
#from fiches.fields import PersonField, PersonWidget
from fiches.widgets import PersonWidget

from fiches.constants import DATE_INPUT_FORMATS, DATE_DISPLAY_FORMAT
from fiches.base_forms import NoteFormBase
from ckeditor.fields import RichTextField, RichTextFormField

from fiches.models.person.relation import Relation, RelationType


from fiches.models.person import Person

# Import Relation & RelationType from the new file:
#from fiches.models.person.relation import Relation, RelationType

from fiches.widgets import PersonWidget

#===============================================================================
# Nationality
#===============================================================================
class Nationality(models.Model):
    name = models.CharField(_(u"Nationalité"), max_length=512)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Nationalité")
        verbose_name_plural = _(u"Nationalités")
        app_label = "fiches"


#===============================================================================
# Religion
#===============================================================================
class Religion(models.Model):
    name = models.CharField(_("Confession"), max_length=256)
    sorting = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sorting']
        app_label = "fiches"


#===============================================================================
# BIOGRAPHIES
#===============================================================================
class Biography(models.Model):
    FICHE_TYPE_NAME = _(u"Fiche biographique")
    FICHE_TYPE_NAME_plural = _(u"Fiches biographiques")

    person = models.ForeignKey(
        "fiches.Person",
        verbose_name=_("Personne"),
        editable=False,
        on_delete=models.CASCADE
    )
    version = models.IntegerField(editable=False, default=0)
    valid = models.BooleanField(default=False)

    birth_place = models.CharField(max_length=256, verbose_name=_(u"Lieu de naissance"), blank=True)
    birth_date = models.DateField(verbose_name=_(u"Date de naissance"), blank=True, null=True)
    birth_date_f = models.CharField(max_length=15, blank=True)
    birth_date_approx = models.BooleanField(_(u"Date de naissance approximative"), default=False)

    death_place = models.CharField(max_length=256, verbose_name=_(u"Lieu de décès"), blank=True)
    death_date = models.DateField(verbose_name=_(u"Date de décès"), blank=True, null=True)
    death_date_f = models.CharField(max_length=15, blank=True)
    death_date_approx = models.BooleanField(_(u"Date de décès approximative"), default=False)

    religion = models.ForeignKey(
        Religion,
        verbose_name=_(u"Confession"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    origin = models.CharField(_(u"Lieu d'origine"), max_length=512, blank=True)
    nationality = models.ForeignKey(
        Nationality,
        verbose_name=_(u"Nationalité"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    education = models.TextField(_(u"Formation"), help_text=_(u"NE PAS REMPLIR CE CHAMP!"), blank=True, null=True)
    public_functions = RichTextField(verbose_name=_(u"Biographie"), config_name='note_ckeditor', blank=True, null=True)
    comments_on_work = RichTextField(verbose_name=_(u"Commentaires sur son oeuvre/ses écrits"), config_name='note_ckeditor', blank=True, null=True)

    activity_places = models.TextField(_(u"Etat civil"), blank=True, null=True)
    abroad_stays = models.TextField(_(u"Séjours à l'étranger"), help_text=_(u"NE PAS REMPLIR CE CHAMP!"), blank=True, null=True)

    archive = RichTextField(verbose_name=_(u"Fonds d'archives"), config_name='note_ckeditor', max_length=512, blank=True)

    modification_date = models.DateTimeField(_(u"Dernière modification"), auto_now=True)

    def person_name(self):
        person_name = str(self.person)
        if self.birth_date and self.death_date:
            fstr = " ("
            if self.birth_date_approx:
                fstr += "v. "
            fstr += "%s - "
            if self.death_date_approx:
                fstr += "v. "
            fstr += "%s)"
            person_name += fstr % (self.birth_date.year, self.death_date.year)
        return person_name

    def relations(self):
        return self.relation_set.all()

    def reverse_relations(self):
        # Return inverse relations
        return ReverseRelation.objects.filter(related_person=self.person)

    def __str__(self):
        return self.person_name()

    from django.urls import reverse

    def get_absolute_url(self):
        return reverse('biography-display', args=[str(self.person_id)])

    class Meta:
        app_label = "fiches"
        verbose_name = _(u"Fiche biographique")
        verbose_name_plural = _(u"Fiches biographiques")
        permissions = (
            ("validate_biography", "Can validate"),
            ("browse_biography_versions", "Can browse versions"),
            ("access_unvalidated_biography", "Can see not validated Biography")
        )


class BiographyForm(ModelForm):
    birth_place = forms.CharField(label=_(u"Lieu"), required=False)
    birth_date = forms.DateField(widget=forms.DateInput(format=DATE_DISPLAY_FORMAT), input_formats=DATE_INPUT_FORMATS, label=_(u"Date"), required=False)
    birth_date_f = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'vardateformat'}), required=False)

    death_place = forms.CharField(label=_(u"Lieu"), required=False)
    death_date = forms.DateField(widget=forms.DateInput(format=DATE_DISPLAY_FORMAT), input_formats=DATE_INPUT_FORMATS, label=_(u"Date"), required=False)
    death_date_f = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'vardateformat'}), required=False)

    def person_name(self):
        return self.instance.person_name()

    class Meta:
        model = Biography
        fields = '__all__'
        widgets = {
            'archive': forms.Textarea()
        }

    class Media:
        css = {
            'all': ('css/jquery.autocomplete.css',),
        }
        js = (
            'js/lib/jquery/jquery.bgiframe.min.js',
            'js/lib/jquery/jquery.ajaxQueue.js',
            'js/lib/jquery/jquery.autocomplete.min.js'
        )


#------------------------------------------------------------------------------
#    Note Biographie
#------------------------------------------------------------------------------
class NoteBiography(NoteBase):
    owner = models.ForeignKey("fiches.Biography", on_delete=models.CASCADE)

    class Meta(NoteBase.Meta):
        app_label = "fiches"


class NoteFormBiography(NoteFormBase):
    class Meta:
        model = NoteBiography
        fields = '__all__'





class ReverseRelation(Relation):
    """
    Pour obtenir les relations inverses d'une personne p:
    rrs = ReverseRelation.objects.select_related().filter(related_person=p).extra(where=["1 GROUP BY fiches_biography.person_id,fiches_relation.relation_type_id"])

    Voir aussi Biography.reverse_relations.__doc__
    """
    class Meta:
        app_label = "fiches"
        proxy = True

    def __str__(self):
        try:
            u = "%s (%s)" % (self.bio.person.__str__(), self.relation_type.reverse_name)
            if not self.bio.valid:
                u += "*"
            return u
        except Exception as e:
            return str(e)




class RelationForm(ModelForm):
    related_person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        label='',  # or "Personne"
        required=False
    )
    relation_type = forms.ModelChoiceField(
        queryset=RelationType.objects.all(),
        required=False
    )

    class Meta:
        model = Relation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Attach PersonWidget to the 'related_person' field so it uses autocomplete
        self.fields['related_person'].widget = PersonWidget(
            fk_field=Relation._meta.get_field('related_person'),
            attrs={'placeholder': 'nom, prénom'}
        )

    def clean(self):
        cleaned_data = super().clean()
        related_person = cleaned_data.get("related_person")
        relation_type = cleaned_data.get("relation_type")

        # If no `related_person` is chosen, remove `relation_type`
        if related_person is None:
            cleaned_data["relation_type"] = None

        return cleaned_data



#===============================================================================
# PROFESSION
#===============================================================================
class Profession(models.Model):
    bio = models.ForeignKey(
        "fiches.Biography",
        on_delete=models.CASCADE
    )

    begin_date = models.DateField(verbose_name=_(u"Début"), blank=True, null=True)
    begin_date_f = models.CharField(max_length=15, blank=True, null=True)
    begin_date_approx = models.BooleanField(_(u"Date de début approximative"), default=False)
    end_date = models.DateField(verbose_name=_(u"Fin"), blank=True, null=True)
    end_date_f = models.CharField(max_length=15, blank=True, null=True)
    end_date_approx = models.BooleanField(_(u"Date de fin approximative"), default=False)
    position = models.CharField(_(u"Poste"), max_length=256)
    place = models.CharField(_(u"Lieu"), max_length=256, blank=True)

    def get_formatted_dates(self):
        if self.begin_date:
            begin_date = format(self.begin_date, self.begin_date_f.replace('%', '').replace('-', '.'))
        else:
            begin_date = "?"
        if self.begin_date_approx:
            begin_date = "v. %s" % begin_date

        if self.end_date:
            end_date = format(self.end_date, self.end_date_f.replace('%', '').replace('-', '.'))
        else:
            end_date = "?"
        if self.end_date_approx:
            end_date = "v. %s" % end_date

        return (begin_date, end_date)

    def __str__(self):
        return "%s %s, %s" % (" - ".join(self.get_formatted_dates()), self.position, self.place)

    class Meta:
        app_label = "fiches"
        ordering = ('begin_date', 'end_date')


class ProfessionForm(ModelForm):
    begin_date = forms.DateField(widget=forms.DateInput(format=DATE_DISPLAY_FORMAT), input_formats=DATE_INPUT_FORMATS, label=_(u"Début"), required=False)
    begin_date_f = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'vardateformat'}), required=False)
    begin_date_approx = forms.BooleanField(required=False)
    end_date = forms.DateField(widget=forms.DateInput(format=DATE_DISPLAY_FORMAT), input_formats=DATE_INPUT_FORMATS, label=_(u"Fin"), required=False)
    end_date_f = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'vardateformat'}), required=False)
    end_date_approx = forms.BooleanField(required=False)
    position = forms.CharField(label=_(u"Poste"))
    place = forms.CharField(widget=forms.TextInput(attrs={'class': 'profession-place'}), label=_(u"Lieu"), required=False)


#===============================================================================
# SocietyMembership
#===============================================================================
class SocietyMembership(models.Model):
    bio = models.ForeignKey(
        "fiches.Biography",
        on_delete=models.CASCADE
    )
    society = models.ForeignKey(
        "fiches.Society",
        verbose_name=_(u"Société"),
        on_delete=models.CASCADE
    )
    begin_date = models.DateField(verbose_name=_(u"Début"), blank=True, null=True)
    begin_date_f = models.CharField(max_length=15, blank=True, null=True)
    begin_date_approx = models.BooleanField(_(u"Date de début approximative"), default=False)
    end_date = models.DateField(verbose_name=_(u"Fin"), blank=True, null=True)
    end_date_f = models.CharField(max_length=15, blank=True, null=True)
    end_date_approx = models.BooleanField(_(u"Date de fin approximative"), default=False)

    def get_formatted_dates(self):
        if self.begin_date:
            begin_date = format(self.begin_date, self.begin_date_f.replace('%', '').replace('-', '.'))
        else:
            begin_date = None
        if self.begin_date_approx and begin_date is not None:
            begin_date = "v. %s" % begin_date

        if self.end_date:
            end_date = format(self.end_date, self.end_date_f.replace('%', '').replace('-', '.'))
        else:
            end_date = '?'
        if self.end_date_approx and end_date != '?':
            end_date = "v. %s" % end_date

        if begin_date and end_date:
            return (begin_date, end_date)
        else:
            return None

    def __str__(self):
        date_str = self.get_formatted_dates()
        if date_str:
            return "%s (%s)" % (self.society, " - ".join(date_str))
        else:
            return str(self.society)

    class Meta:
        app_label = "fiches"


from fiches.models.misc.society import Society

class SocietyMembershipForm(ModelForm):
    society = forms.ModelChoiceField(
        queryset=Society.objects.all(),
        empty_label=_("------ Sélectionner une société/académie -----")
    )
    begin_date = forms.DateField(widget=forms.DateInput(format=DATE_DISPLAY_FORMAT), input_formats=DATE_INPUT_FORMATS, label=_("du"), required=False)
    begin_date_f = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'vardateformat'}), required=False)
    begin_date_approx = forms.BooleanField(required=False)
    end_date = forms.DateField(widget=forms.DateInput(format=DATE_DISPLAY_FORMAT), input_formats=DATE_INPUT_FORMATS, label=_("au"), required=False)
    end_date_f = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'vardateformat'}), required=False)
    end_date_approx = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("society") is None:
            for k in ('begin_date', 'begin_date_f', 'begin_date_approx', 'end_date', 'end_date_f', 'end_date_approx'):
                cleaned_data.pop(k, None)
        return cleaned_data
