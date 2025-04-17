# fiches/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from .models.documents import (
    Biblio,
    Manuscript,
    ManuscriptType,
    Transcription,
    ContributionMan,
    NoteBiblio,
    NoteTranscription,
    DocumentLanguage,
    ContributionDoc,
    DocumentFile,
)
from .models.contributions import PrimaryKeyword, SecondaryKeyword
from .models.misc import Society
from .models.person import Person
from .models.contributiontype import ContributionType
from .fields import MultiplePersonField
from .widgets import StaticList, DynamicList, PersonWidget
from .constants import DATE_DISPLAY_FORMAT, DATE_INPUT_FORMATS
from django.contrib.auth.models import User
from .models.misc import ObjectCollection
from .models.documents import TRANSCRIPTION_CHOICES
from django.forms.widgets import RadioSelect

from ckeditor.widgets import CKEditorWidget

# ===============================
# Base Form for Notes
# ===============================
class NoteFormBase(forms.ModelForm):
    def clean_text(self):
        data = self.cleaned_data.get('text', '')
        return data

    class Meta:
        # "abstract" might be omitted, etc.
        fields = []  # or define shared fields here if you want

# ===============================
# BiblioForm Definition
# ===============================
class BiblioForm(forms.ModelForm):
    """Form for editing the Biblio model (the main bibliographic record)."""
    title = forms.CharField(
        label=Biblio._meta.get_field("title").verbose_name,
        widget=forms.Textarea(attrs={"cols": "64", "rows": "3"})
    )
    # Add the "Personne" dynamic M2M field
    subj_person = MultiplePersonField(
        widget=DynamicList(
            rel=Biblio.subj_person,
            add_title="Ajouter une personne",
            placeholder="nom, prénom"
        ),
        label=_("Personne"),
        required=False
    )

        # Add this override
    subj_society = forms.ModelMultipleChoiceField(
        queryset=Society.objects.all(),
        widget=StaticList(
            add_title="Ajouter une société",
            empty_label="[ choisir une société ou académie ]"
        ),
        required=False,
        label=_("Société/Académie")
    )

    abstract = forms.CharField(
        label=_("Résumé"),
        widget=CKEditorWidget(config_name='note_ckeditor'),
        required=False
    )

    documentfiles = forms.ModelMultipleChoiceField(
        queryset=DocumentFile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("Documents")
    )

    class Meta:
        model = Biblio
        fields = '__all__'  # or list them explicitly
        widgets = {
            'short_title': forms.Textarea(attrs={"cols": "64", "rows": "1"}),
            'litterature_type': RadioSelect,
            # optionally override any other Biblio fields
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Example: make "litterature_type" required
        self.fields['litterature_type'].required = True

        # Remove any blank choice inserted by Django for the litterature_type
        choices_without_blank = [
            choice for choice in self.fields['litterature_type'].choices
            if choice[0] != ''
        ]
        self.fields['litterature_type'].choices = choices_without_blank

    def clean(self):
        cleaned_data = super().clean()
        doctype = cleaned_data.get("document_type")
        book_title = cleaned_data.get("book_title")
        journal_title = cleaned_data.get("journal_title")
        dictionary_title = cleaned_data.get("dictionary_title")
        manuscript_type = cleaned_data.get("manuscript_type")

        msg = _("Ce champ est obligatoire.")
        if doctype:
            # Example logic from your old code:
            if doctype.id == 2 and not book_title:
                self.add_error("book_title", msg)
            elif doctype.id == 3 and not journal_title:
                self.add_error("journal_title", msg)
            elif doctype.id == 4 and not dictionary_title:
                self.add_error("dictionary_title", msg)
            elif doctype.id == 5 and not manuscript_type:
                self.add_error("manuscript_type", msg)

        primary_kw_msg = _("Au moins un mot-clé primaire est obligatoire.")
        if not cleaned_data.get('subj_primary_kw'):
            self.add_error("subj_primary_kw", primary_kw_msg)

        return cleaned_data
    
    def clean_subj_person(self):
        """
        Convert each '336|Name' string to a real Person object.
        This ensures we return a list of Person instances for the M2M field.
        """
        # We'll override the default cleaned_data list by re-parsing the raw POST data:
        raw_list = self.data.getlist('subj_person')  
        # e.g. ["336|Seigneux, Jean-Daniel (1725-1795)", "999|Another Name", ...]

        persons = []
        for item in raw_list:
            item = item.strip()
            if not item:
                continue
            if '|' in item:
                pk_str, label = item.split('|', 1)
                try:
                    pk = int(pk_str)
                    p = Person.objects.get(pk=pk)
                    persons.append(p)
                except (ValueError, Person.DoesNotExist):
                    # Raise a validation error or just skip it
                    raise forms.ValidationError(
                        f"La personne «{item}» n'existe pas dans la base."
                    )
            else:
                # If there's no "|" in the string, it means user typed a new name
                # that didn't match any Person in the DB. You can skip or raise an error.
                continue

        return persons



# ===============================
# NoteFormBiblio Definition
# ===============================
class NoteFormBiblio(NoteFormBase):
    """
    Form for editing the NoteBiblio model (notes referencing a Biblio).
    It should NOT contain fields that belong to Biblio, like subj_person, etc.
    """

    class Meta(NoteFormBase.Meta):
        model = NoteBiblio
        fields = '__all__'  # Or just ['text', 'owner'] if that's all you need

    # If your NoteBiblio model has its own fields, define them or custom widgets here.
    # e.g.
    # text = forms.CharField(widget=forms.Textarea, label="Contenu de la note", required=True)
    #
    # def clean_text(self):
    #     # do any special validation
    #     return super().clean_text()



# ===============================
# Other Form Definitions
# ===============================
class ManuscriptForm(forms.ModelForm):
    title = forms.CharField(
        label=Manuscript._meta.get_field("title").verbose_name,
        widget=forms.Textarea(attrs={"cols": "64", "rows": "3"})
    )
    manuscript_type = forms.ModelChoiceField(
        label=Manuscript._meta.get_field("manuscript_type").verbose_name,
        queryset=ManuscriptType.objects.all(),
        initial='1'
    )
    date = forms.DateField(
        widget=forms.DateInput(format=DATE_DISPLAY_FORMAT),
        input_formats=DATE_INPUT_FORMATS,
        label=_("Date"),
        required=False
    )
    date_f = forms.CharField(
        widget=forms.HiddenInput(attrs={'class': 'vardateformat'}),
        required=False
    )
    subj_primary_kw = forms.ModelMultipleChoiceField(
        queryset=PrimaryKeyword.objects.all(),
        widget=StaticList(),
        required=False,
        label=Manuscript._meta.get_field("subj_primary_kw").verbose_name
    )
    subj_secondary_kw = forms.ModelMultipleChoiceField(
        queryset=SecondaryKeyword.objects.all(),
        widget=StaticList(),
        required=False,
        label=Manuscript._meta.get_field("subj_secondary_kw").verbose_name
    )
    subj_society = forms.ModelMultipleChoiceField(
        queryset=Society.objects.all(),
        widget=StaticList(),
        required=False,
        label=Manuscript._meta.get_field("subj_society").verbose_name
    )
    access_date = forms.DateField(
        label=Manuscript._meta.get_field("access_date").verbose_name,
        required=False,
        input_formats=DATE_INPUT_FORMATS,
        widget=forms.DateInput(format="%d/%m/%Y")
    )

    class Meta:
        model = Manuscript
        exclude = ('urls', 'biblio_man')  # Ensure these fields exist and are correctly excluded


class TranscriptionForm(forms.ModelForm):
    manuscript = forms.CharField(widget=forms.HiddenInput(), required=False)
    manuscript_b = forms.CharField(widget=forms.HiddenInput(), required=False)
    author = forms.ModelChoiceField(queryset=User.objects.all().order_by('username'))
    author2 = forms.ModelChoiceField(queryset=User.objects.all().order_by('username'), required=False)
    reviewers = forms.ModelMultipleChoiceField(queryset=User.objects.all().order_by('username'), required=False)
    status = forms.IntegerField(
        widget=forms.RadioSelect(choices=TRANSCRIPTION_CHOICES['status']),
        label=_("État"),
        initial=0
    )
    scope = forms.IntegerField(
        widget=forms.RadioSelect(choices=TRANSCRIPTION_CHOICES['scope']),
        label=_("Transcription"),
        initial=0
    )

    class Meta:
        model = Transcription
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        manuscript_id = cleaned_data.get("manuscript")
        manuscript_b_id = cleaned_data.get("manuscript_b")

        if manuscript_id:
            try:
                cleaned_data["manuscript"] = Manuscript.objects.get(pk=manuscript_id)
            except Manuscript.DoesNotExist:
                self.add_error("manuscript", _("Manuscript does not exist."))
                del cleaned_data["manuscript"]
        else:
            del cleaned_data["manuscript"]

        if manuscript_b_id:
            try:
                cleaned_data["manuscript_b"] = Biblio.objects.get(pk=manuscript_b_id)
            except Biblio.DoesNotExist:
                self.add_error("manuscript_b", _("Bibliography does not exist."))
                del cleaned_data["manuscript_b"]
        else:
            del cleaned_data["manuscript_b"]

        return cleaned_data


class ContributionManForm(forms.ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            fk_field=ContributionMan._meta.get_field('person'),
            attrs={'placeholder': 'nom, prénom'}
        ),
        label='',
        required=False
    )
    contribution_type = forms.ModelChoiceField(
        queryset=ContributionType.objects.filter(type__in=('man', 'any')),
        empty_label=None
    )

    class Meta:
        model = ContributionMan
        fields = '__all__'


class ObjectCollectionForm(forms.ModelForm):
    """
    Form for the ObjectCollection model.
    """
    class Meta:
        model = ObjectCollection
        # Exclude the owner field so it won't be rendered or expected in POST data.
        exclude = ['owner']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Enter collection name')}),
            # Add other widgets as needed
        }

    def clean(self):
        cleaned_data = super().clean()
        # Remove or update the following if not needed:
        # person = cleaned_data.get("person")
        # contribution_type = cleaned_data.get("contribution_type")
        # if person is None:
        #     cleaned_data["contribution_type"] = None
        return cleaned_data



from haystack.forms import ModelSearchForm
from haystack.query import RelatedSearchQuerySet
from fiches.models import Person, Biblio, Transcription

class FichesSearchForm(ModelSearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_models(self):
        """Return an alphabetical list of model classes in the index."""
        search_models = super().get_models()
        if not search_models:
            # If no models are found, retrieve them from the Haystack unified index
            search_models = connections['default'].get_unified_index().get_indexed_models()
        return search_models

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        query = self.cleaned_data.get('q')
        if not query:
            return self.no_query_found()

        # Restrict results based on user permissions and access
        if self.request and self.request.user.is_authenticated:
            if not self.request.user.has_perm('fiches.access_unpublished_transcription'):
                self.searchqueryset = RelatedSearchQuerySet().load_all_queryset(
                    Transcription,
                    Transcription.objects.filter(
                        Q(access_public=True) |
                        Q(author=self.request.user) |
                        Q(author2=self.request.user) |
                        Q(access_groups__users=self.request.user) |
                        Q(access_groups__groups__user=self.request.user) |
                        Q(project__members=self.request.user) |
                        Q(access_public=False, access_private=False, access_groups__isnull=True)
                    )
                )
        else:
            self.searchqueryset = RelatedSearchQuerySet()

        # Apply the search query
        sqs = self.searchqueryset.auto_query(query)

        if self.load_all:
            sqs = sqs.load_all()

        # Filter and order results based on models
        models = self.get_models()
        ordered_models = [m for m in (Person, Biblio, Transcription) if m in models]

        result_list = []
        for model in ordered_models:
            model_results = sqs.models(model)
            result_list.extend(list(model_results))

        return result_list
    

class ContributionDocForm(forms.ModelForm):
    # 1) Use a simple CharField, not ModelChoiceField
    person = forms.CharField(
        widget=PersonWidget(
            fk_field=ContributionDoc._meta.get_field("person"),
            attrs={'class': 'dynamiclist_helper_input', 'placeholder': 'nom, prénom'}
        ),
        required=False
    )
    contribution_type = forms.ModelChoiceField(
        queryset=ContributionType.objects.filter(type__in=('doc', 'any')),
        empty_label=None,
        required=False
    )

    class Meta:
        model = ContributionDoc
        fields = "__all__"

    #
    # 2) Parse out pk from “123|Name” in clean_person()
    #
    def clean_person(self):
        raw_value = self.cleaned_data.get("person", "")  # e.g. "1735|Usteri, Paul..."
        if not raw_value.strip():
            # User typed nothing or cleared field
            return None

        if "|" in raw_value:
            pk_str, display_name = raw_value.split("|", 1)
            try:
                pk = int(pk_str)
                # Retrieve the Person instance
                return Person.objects.get(pk=pk)
            except (ValueError, Person.DoesNotExist):
                raise forms.ValidationError(
                    "Cette personne est introuvable dans la base."
                )
        else:
            # No pipe => user typed something but no ID
            return None

    #
    # 3) Optionally skip entire row if no person was set
    #
    def clean(self):
        cleaned_data = super().clean()
        person = cleaned_data.get("person")  # now a Person instance or None
        if not person:
            # If no person is chosen, treat row as empty => remove keys
            cleaned_data.pop("person", None)
            cleaned_data.pop("contribution_type", None)
        return cleaned_data


