# -*- coding: utf-8 -*-
#
#    [License and copyright information]
#

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from utils.fields import DictField
from fiches.models.documents.document import DocumentType, Biblio, ManuscriptType, Depot
from fiches.models.contributions.keyword import PrimaryKeyword, SecondaryKeyword
from fiches.models.documents.document import LITTERATURE_TYPE_CHOICES, DocumentLanguage
from fiches.models.misc.society import Society


class SearchFilters(models.Model):
    title = models.CharField(_("Titre"), max_length=30)
    model_name = models.CharField(max_length=30)
    query_def = models.TextField(blank=True)
    display_columns = models.TextField(blank=True)
    display_settings = DictField(blank=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    groups = models.ManyToManyField(Group, blank=True)
    
    class Meta:
        verbose_name = _("Filtre de recherche")
        verbose_name_plural = _("Filtre de recherche")
        app_label = "fiches"

    def __str__(self):
        return self.title

class PlaceView(models.Model):
    biblio = models.ForeignKey(
        Biblio,  # Changed from 'document.Biblio' to Biblio
        verbose_name=_("Biblio"),
        null=True,          # Added null=True
        blank=True,         # Allows the field to be optional in forms
        on_delete=models.SET_NULL,
        related_name='place_views'  # Prevents reverse accessor clashes
    )
    place_name = models.CharField(
        max_length=255,
        verbose_name=_("Place Name")
    )
    # Add other relevant fields here

    def __str__(self):
        return f"PlaceView for {self.place_name} ({self.biblio.title if self.biblio else 'No Biblio'})"

    class Meta:
        app_label = "fiches"
        verbose_name = _("Place View")
        verbose_name_plural = _("Place Views")
        ordering = ['place_name']

#from django.db import models
#from django.utils.translation import gettext_lazy as _

class JournaltitleView(models.Model):
    journal_title = models.CharField(max_length=512, primary_key=True, verbose_name=_("Journal Title"))

    def __str__(self):
        return self.journal_title

    class Meta:
        managed = False  # Prevent Django from modifying the view
        db_table = 'fiches_journaltitleview'
        verbose_name = _("Journal Title View")
        verbose_name_plural = _("Journal Title Views")
        ordering = ['journal_title']



from django import forms
from fiches.models import Project


class BiblioExtendedSearchForm(forms.Form):
    """
    """
    
    # Recherche libre dans les champs
    EXPR_FIELDS_CHOICE = (
        ('title', u"Titre du document"),
        ('authors', u"Auteur / Contributeur"),
        ('person', u"Personne"),
        ('edit', u"Editeur"),
        ('place', u"Lieu d'édition"),
    )
    OP_FIELD_CHOICES = (('or', 'Ou'), ('and', 'Et'), ('not', 'Sauf'))
    
    sort = forms.ChoiceField(required=False, initial='',  choices=(('d', u"Date croissante"), ('-d', u"Date décroissante"), ('t', u"Titre")))
    nbi  = forms.ChoiceField(required=False, initial='',  choices=(('10', "10"), ('', "25"), ('50', "50"), ('75', "75")))
    grp  = forms.ChoiceField(required=False, initial='d', choices=(('d', u"Type et auteur"), ('a', u"Auteur et type"), ('', '– sans regroupement –')) )
    
    x0_fld = forms.ChoiceField(required=False, choices=EXPR_FIELDS_CHOICE, initial='title', )
    x0_val = forms.CharField(required=False)

    x1_op  = forms.ChoiceField(required=False, choices=OP_FIELD_CHOICES, initial='and', )
    x1_fld = forms.ChoiceField(required=False, choices=EXPR_FIELDS_CHOICE, initial='authors', )
    x1_val = forms.CharField(required=False)

    x2_op  = forms.ChoiceField(required=False, choices=OP_FIELD_CHOICES, initial='and', )
    x2_fld = forms.ChoiceField(required=False, choices=EXPR_FIELDS_CHOICE, initial='place', )
    x2_val = forms.CharField(required=False)

    x3_op  = forms.ChoiceField(required=False, choices=OP_FIELD_CHOICES, initial='and', )
    x3_fld = forms.ChoiceField(required=False, choices=EXPR_FIELDS_CHOICE, initial='edit', )
    x3_val = forms.CharField(required=False)


    # Type de documents
    dt = forms.ModelMultipleChoiceField(required=False, queryset=DocumentType.objects.all().order_by('id'), 
                                        widget=forms.CheckboxSelectMultiple())
    #dt_op = forms.ChoiceField(required=False, initial='and', choices=OP_FIELD_CHOICES)
    
    
    # Type de littérature
    ltype = forms.MultipleChoiceField(required=False, choices = LITTERATURE_TYPE_CHOICES,
                                      widget=forms.CheckboxSelectMultiple())
    
    
    # Date
    date_from = forms.DecimalField(required=False, max_digits=6, decimal_places=2, widget=forms.TextInput(attrs={'maxlength':"7", 'placeholder':"aaaa.mm"}))
    date_to   = forms.DecimalField(required=False, max_digits=6, decimal_places=2, widget=forms.TextInput(attrs={'maxlength':"7", 'placeholder':"aaaa.mm"}))
    
    # Modification date
    mdate_from = forms.DateField(required=False, input_formats=('%Y.%m.%d',), 
                                 widget=forms.DateInput(attrs={'size': '10', 'maxlength':"10", 'placeholder':"aaaa.mm.jj"}))
    mdate_to   = forms.DateField(required=False, input_formats=('%Y.%m.%d',),
                                 widget=forms.DateInput(attrs={'size': '10', 'maxlength':"10", 'placeholder':"aaaa.mm.jj"}))
    
    # Langue
    language_choices = (('', u"< toutes >"),) + tuple(DocumentLanguage.objects.values_list('id', 'name'))
    #language = forms.ModelChoiceField(required=False, queryset=DocumentLanguage.objects.all(), empty_label = "< toutes >")
    l = forms.ChoiceField(required=False, choices=language_choices)
    

    # Lieu de dépôt
    depot = forms.ModelChoiceField(required=False, queryset=Depot.objects.all())
    
    # Projets
    proj = forms.ModelMultipleChoiceField(required=False, queryset=Project.objects.filter(publish=True),
                                          widget=forms.CheckboxSelectMultiple())
    proj_op = forms.ChoiceField(required=False, initial='and', choices=OP_FIELD_CHOICES)

    # Société/Académie
    society = forms.ModelChoiceField(required=False, queryset=Society.objects.all())
    
    # Revue
    journal = forms.ChoiceField(required=False, choices=(('', '---------'),) + 
                                tuple(Biblio.objects.exclude(journal_title='').values_list('journal_title', 'journal_title')\
                                .order_by('journal_title').distinct()))
    
    # Type de manuscrit
    mtype = forms.ModelChoiceField(required=False, queryset=ManuscriptType.objects.all())
    
    # Mots clés
    kw0_op = forms.ChoiceField(required=False, initial='and', choices=OP_FIELD_CHOICES)
    kw0_p  = forms.ModelChoiceField(required=False, queryset=PrimaryKeyword.objects.all(),
                                   empty_label = "< mot-clé primaire >", widget=forms.Select(attrs={'class':"pkw"}))
    kw0_s  = forms.ModelChoiceField(required=False, queryset=SecondaryKeyword.objects.all())
    
    
    kw1_op = forms.ChoiceField(required=False, initial='and', choices=OP_FIELD_CHOICES)
    kw1_p  = forms.ModelChoiceField(required=False, queryset=PrimaryKeyword.objects.all(),
                                   empty_label = "< mot-clé primaire >", widget=forms.Select(attrs={'class':"pkw"}))
    kw1_s  = forms.ModelChoiceField(required=False, queryset=SecondaryKeyword.objects.all())
    
    
    kw2_op = forms.ChoiceField(required=False, initial='and', choices=OP_FIELD_CHOICES)
    kw2_p  = forms.ModelChoiceField(required=False, queryset=PrimaryKeyword.objects.all(),
                                   empty_label = "< mot-clé primaire >", widget=forms.Select(attrs={'class':"pkw"}))
    kw2_s  = forms.ModelChoiceField(required=False, queryset=SecondaryKeyword.objects.all())
    
    
    kw3_op = forms.ChoiceField(required=False, initial='and', choices=OP_FIELD_CHOICES)
    kw3_p  = forms.ModelChoiceField(required=False, queryset=PrimaryKeyword.objects.all(),
                                   empty_label = "< mot-clé primaire >", widget=forms.Select(attrs={'class':"pkw"}))
    kw3_s  = forms.ModelChoiceField(required=False, queryset=SecondaryKeyword.objects.all())
    

    # Etat collapsed/expanded des groupe de champs
    cl1 = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput(attrs={'class': "collapse_status"}))
    cl2 = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput(attrs={'class': "collapse_status"}))
    cl3 = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput(attrs={'class': "collapse_status"}))
    cl4 = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput(attrs={'class': "collapse_status"}))

