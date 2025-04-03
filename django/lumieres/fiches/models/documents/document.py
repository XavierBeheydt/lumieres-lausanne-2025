# fiches/models/documents/document.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

from fiches.models.person.person import Person
from fiches.models.misc.society import Society
from fiches.models.contributions.keyword import PrimaryKeyword, SecondaryKeyword
from fiches.models.misc.notes import NoteBase
from fiches.models.contributions.ac_model import ACModel

from fiches.models.contributiontype import ContributionType

from utils.utils_coins import get_doc_coins

from django.core.cache import cache

#===============================================================================
# DOCUMENTS
#===============================================================================

LITTERATURE_TYPE_CHOICES = (
    ('p', _("Primaire")),
    ('s', _("Secondaire"))
)

from fiches.models.documents.document_file import DocumentFile
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Document(models.Model):
    title = models.CharField(_(u'Titre'), max_length=250, blank=True)
    file = models.FileField(_(u'Fichier'), upload_to="files/%Y/%m")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # def __unicode__(self):
    #     if self.title:
    #         return self.title
    #     return basename(self.file.name)

    def __str__(self):
        if self.title:
            return self.title
        return basename(self.file.name)

class DocumentType(models.Model):
    """
    Le type de document d'une fiche Bibliographique

    Cette valeur est utilisé pour l'affichage conditionel des champs spécifiques
    au type de document.

    Ex: on affiche le champ 'book_title' que pour le type "Chapitre de livre"
    """
    name = models.CharField(max_length=30)
    code = models.IntegerField(default=-1)
    exclusive_fields = models.CharField(
        max_length=512,
        blank=True,
        help_text=_("Liste des nom de champs du document qui n'apparaissent que pour ce type de document. Liste séparée par des virgules.")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Type de document")
        verbose_name_plural = _("Types de document")
        app_label = "fiches"
        ordering = ['-code', '-id']


class DocumentLanguage(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=10, blank=True)
    ordering = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Langue de document")
        verbose_name_plural = _("Langues de document")
        app_label = "fiches"
        ordering = ['ordering', 'name']


class Depot(models.Model):
    name = models.CharField(_("Nom"), max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Lieu de dépôt")
        verbose_name_plural = _("Lieux de dépôt")
        app_label = "fiches"
        ordering = ['name']


class ManuscriptType(models.Model):
    name = models.CharField(max_length=128)
    sorting = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Type de manuscrit")
        verbose_name_plural = _("Types de manuscrit")
        app_label = "fiches"
        ordering = ['sorting']

class Biblio(models.Model):
    """
    Fiche bibliographique
    """

    FICHE_TYPE_NAME = _("Fiche bibliographique")
    FICHE_TYPE_NAME_plural = _("Fiches bibliographiques")

    LITTERATURE_TYPE_CHOICES = (
        ('p', _('Primaire')),
        ('s', _('Secondaire')),
    )

    title = models.TextField(_("Titre"))
    short_title = models.CharField(_("Titre court"), max_length=512, blank=True, null=True)
    litterature_type = models.CharField(
        _("Type de littérature"),
        max_length=2,
        choices=LITTERATURE_TYPE_CHOICES
    )
    document_type = models.ForeignKey(
        "DocumentType",
        verbose_name=_("Type de document"),
        on_delete=models.CASCADE
    )

    # Book Type ( Chapitre de Livre )
    book_title = models.CharField(_("Titre du livre"), max_length=512, blank=True)
    collection = models.CharField(_("Collection et n° du volume"), max_length=512, blank=True)

    # Journal Type ( Revue )
    journal_title = models.CharField(_("Titre de la revue"), max_length=512, blank=True)
    journal_num = models.CharField(_("N° de la revue"), max_length=30, blank=True)
    journal_abr = models.CharField(_("Abréviation de la revue"), max_length=60, blank=True)
    series_title = models.CharField(_("Titre du numéro"), max_length=512, blank=True)
    series_text = models.CharField(_("Texte de la série"), max_length=512, blank=True)

    # Dictionary Type ( Dictionnaire )
    dictionary_title = models.CharField(_("Titre de dictionnaire"), max_length=256, blank=True)

    # Manuscript type
    inscription = models.CharField(_("Dédicace"), max_length=256, blank=True)
    manuscript_type = models.ForeignKey(
        "ManuscriptType",
        verbose_name=_("Type d'écrit"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    place = models.CharField(_("Lieu"), max_length=64, blank=True)
    publisher = models.CharField(_("Editeur"), max_length=256, blank=True)
    place2 = models.CharField(_("2e Lieu"), max_length=64, blank=True)
    publisher2 = models.CharField(_("2e Editeur"), max_length=256, blank=True)
    edition = models.CharField(_("Date de 1ère Edition"), max_length=128, blank=True)
    date = models.DateField(_("Date"), blank=True, null=True)
    date_f = models.CharField(max_length=15, blank=True, null=True)
    date2 = models.DateField(_("Date fin"), blank=True, null=True)
    date2_f = models.CharField(max_length=15, blank=True, null=True)
    volume = models.IntegerField(
        _("Volume"),
        validators=[MinValueValidator(0), MaxValueValidator(128)],
        blank=True,
        null=True,
        default=None
    )
    volume_nb = models.IntegerField(_("Nb de volumes"), blank=True, null=True, default=None)
    pages = models.CharField(_("Pages"), max_length=64, blank=True)

    urls = models.TextField(_("URLs"), blank=True)
    documentfiles = models.ManyToManyField("DocumentFile", blank=True)
    abstract = RichTextField(verbose_name=_("Résumé"), config_name='note_ckeditor', blank=True)

    # Subjects
    subj_primary_kw = models.ManyToManyField("PrimaryKeyword", verbose_name=_("Mot clé principal"), blank=True)
    subj_secondary_kw = models.ManyToManyField("SecondaryKeyword", verbose_name=_("Mot clé secondaire"), blank=True)
    subj_person = models.ManyToManyField("Person", verbose_name=_("Personne"), blank=True)
    subj_society = models.ManyToManyField("Society", verbose_name=_("Société/Académie"), blank=True)

    isbn = models.CharField(_("ISBN"), max_length=24, blank=True)
    serie = models.CharField(_("Série"), max_length=64, blank=True)
    serie_num = models.CharField(_("N° de la série"), max_length=64, blank=True)

    def get_default_language():
        return DocumentLanguage.objects.get_or_create(name='Français')[0].id

    language = models.ForeignKey(
        "DocumentLanguage",
        verbose_name=_("Langue"),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        default=get_default_language
    )
    language_sec = models.ForeignKey(
        "DocumentLanguage",
        verbose_name=_("Langue secondaire"),
        related_name='sec_biblio_set',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    depot = models.ForeignKey(
        "Depot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Lieu de dépôt",
    )

    legacy_depot = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        db_column='depot',
        verbose_name=_(u"Lieu de dépôt (texte)")
    )

    cote = models.CharField(_("Cote"), max_length=150, blank=True)

    authorization = models.BooleanField(_("Autorisation"), default=False, blank=True)
    access_date = models.DateField(_("Accédé le"), blank=True, null=True)
    extra = models.CharField(_("Extra"), max_length=128, blank=True)

    creator = models.ForeignKey(
        User,
        verbose_name=_("Auteur de la fiche"),
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    )

    first_author = models.ForeignKey(
        "Person",
        verbose_name=_("Premier Auteur"),
        related_name="biblio_asfirstauthor_set",
        editable=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    first_author_name = models.CharField(
        max_length=215,
        editable=False,
        blank=True,
        default=""
    )

    def __str__(self):
        return self.title

    @classmethod
    def getDocumentTypes(cls):
        return DocumentType.objects.all()

    def get_absolute_url(self):
        return reverse('display-bibliography', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.depot_id:
            self.depot_id = 66  # Default depot
        super().save(*args, **kwargs)
        cache.delete(f'lumieres__biblioref__{self.id}')

    class Meta:
        app_label = "fiches"
        verbose_name = _("Fiche bibliographique")
        verbose_name_plural = _("Fiches bibliographiques")
        ordering = ['first_author_name', 'title']
        permissions = (
            ('change_biblio_ownership', "Can change ownership of Bibliography"),
            ('change_any_biblio', "Can change any Bibliography"),
            ('delete_any_biblio', "Can delete any Bibliography"),
            ('can_add_listitem', "Can add item in autocomplete lists"),
        )



class ContributionDoc(models.Model):
    person = models.ForeignKey(
        Person,
        verbose_name=_("Contributeur"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='contribution_biblio'  # Restores old "contribution_biblio" usage
    )
    document = models.ForeignKey(
        Biblio,  # The old project called this "document," but it points to Biblio
        verbose_name=_("Biblio"),
        null=True,
        blank=True,
        on_delete=models.CASCADE  # or SET_NULL if you prefer
    )
    contribution_type = models.ForeignKey(
        ContributionType,
        verbose_name=_("Type de contribution"),
        limit_choices_to={'type__in': ['doc', 'any']},
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    in_brackets = models.BooleanField(
        _(u"Entre crochets"),
        default=False
    )

    def __str__(self):
        # If person or contribution_type is None, avoid error by using safe strings
        person_str = str(self.person) if self.person else _("(Aucun contributeur)")
        contrib_str = str(self.contribution_type) if self.contribution_type else _("(Aucun type)")
        return f"{person_str} ({contrib_str})"

    class Meta:
        app_label = "fiches"
        verbose_name = _("Contribution pour Document")
        verbose_name_plural = _("Contributions pour Document")
        ordering = ("contribution_type", "person")
        # If the old project had unique constraints, e.g.: 
        # unique_together = (("person", "document", "contribution_type"),)


# .............................................................................
# Les classes suivantes sont utilisées depuis la migration
# des objects `Manuscript` dans `Biblio`
# Je ne sais pas si c'est encore utile ou non.... :'-(
#..............................................................................
class ManuscriptBManager(models.Manager):
    def get_queryset(self):
        return super(ManuscriptBManager, self).get_queryset().filter(document_type__id=5)


class ManuscriptB(Biblio):

    objects = ManuscriptBManager()

    class Meta:
        proxy = True
        app_label = "fiches"
        verbose_name = _("Fiche de manuscrit")
        verbose_name_plural = _("Fiches de manuscrit")
        ordering = ('title', '-date')


#------------------------------------------------------------------------------
#    Note Bibliographie
#------------------------------------------------------------------------------
class NoteBiblio(NoteBase):
    owner = models.ForeignKey(
        Biblio,
        on_delete=models.SET_NULL,  # Prevent deletion of associated notes if Biblio is deleted
        null=True,
        related_name="notes",  # Allows accessing notes via `biblio.notes.all()`
    )

    # Ensure `rte_type` exists and is compatible with note_formset.html
    rte_type = models.CharField(
        max_length=10,
        choices=[("CKE", "CKEditor"), ("TXT", "Plain Text")],  # Example choices
        default="CKE",  # Matches the condition in `note_formset.html`
    )

    class Meta(NoteBase.Meta):
        app_label = "fiches"


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@                                                                         @@
#@@  NE PLUS UTILISER LA CLASS MANUSCRIPT                                   @@
#@@  CETTE CLASS EST INTEGREE DANS BIBLIO, les anciens objets existent      @@
#@@  encore dans la base. Sont encore accessibles pour retro-compatibilité  @@
#@@                                                                         @@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\\
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\\


#===============================================================================
# MANUSCRIT
#===============================================================================
class Manuscript(models.Model):
    """
    Fiche de manuscrit
    """
    FICHE_TYPE_NAME = _("Fiche de manuscrit")
    FICHE_TYPE_NAME_plural = _("Fiches de manuscrit")

    title = models.CharField(_("Titre"), max_length=512)
    short_title = models.CharField(_("Titre court"), max_length=512, blank=True)

    inscription = models.CharField(max_length=256, blank=True)
    abstract = models.TextField(_("Résumé"), blank=True)
    manuscript_type = models.ForeignKey(
        ManuscriptType,
        verbose_name=_("Type"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL  # on_delete argument added
    )

    place = models.CharField(_("Lieu"), max_length=256, blank=True)
    date = models.DateField(_("Date"), blank=True, null=True)
    date_f = models.CharField(max_length=15, blank=True, null=True)
    pages = models.CharField(_("Pages"), max_length=128, blank=True, null=True)

    lang_main = models.ForeignKey(
        DocumentLanguage,
        verbose_name=_("Langue principale"),
        related_name='manuscript_main_set',
        blank=True,
        null=True,
        on_delete=models.SET_NULL  # on_delete argument added
    )
    lang_sec = models.ForeignKey(
        DocumentLanguage,
        verbose_name=_("Langue secondaire"),
        related_name='manuscript_sec_set',
        blank=True,
        null=True,
        on_delete=models.SET_NULL  # on_delete argument added
    )

    urls = models.TextField(_("URLs"), blank=True)
    documentfiles = models.ManyToManyField(DocumentFile, blank=True)  # , null=True
    access_date = models.DateField(_("Accédé le"), blank=True, null=True)
    depot = models.CharField(_("Lieu de dépôt"), max_length=128, blank=True)

    cote = models.CharField(_("Cote"), max_length=150, blank=True)
    authorization = models.BooleanField(_("Autorisation"), default=False, null=True, blank=True)

    extra = models.CharField(_("Extra"), max_length=128, blank=True)

    subj_primary_kw = models.ManyToManyField(
        PrimaryKeyword,
        verbose_name=_("Mot clé principal"),
        blank=True
    )  # null=True
    subj_secondary_kw = models.ManyToManyField(
        SecondaryKeyword,
        verbose_name=_("Mot clé secondaire"),
        blank=True
    )  # null=True
    subj_society = models.ManyToManyField(
        Society,
        verbose_name=_("Société"),
        blank=True
    )  # null=True

    creator = models.ForeignKey(
        User,
        verbose_name=_("Auteur de la fiche"),
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    )

    first_author = models.ForeignKey(
        Person,
        verbose_name=_("Premier Auteur"),
        editable=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    biblio_man = models.ForeignKey(
        Biblio,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )  # Add on_delete here

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('manuscript-display', kwargs={'pk': str(self.id)})

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        try:
            first_author_person = self.contributionman_set.filter(contribution_type__code=0).order_by('pk')[0].person
        except IndexError:
            first_author_person = None
        self.first_author = first_author_person
        super(Manuscript, self).save(force_insert, force_update, *args, **kwargs)

    def getFirstAuthorName(self):
        try:
            first_author_name = self.contributionman_set.filter(contribution_type__code=0).order_by('pk')[0].person.name
        except IndexError:
            first_author_name = None
        return first_author_name

    class Meta:
        app_label = "fiches"
        verbose_name = _("Fiche de manuscrit")
        verbose_name_plural = _("Fiches de manuscrit")
        ordering = ('title', '-date')
        permissions = (
            ('change_manuscript_ownership', "Can change ownership of Manuscript"),
            ('change_any_manuscript', "Can change any Manuscript"),
            ('delete_any_manuscript', "Can delete any Manuscript"),
        )


#------------------------------------------------------------------------------
#    Note Manuscrit
#------------------------------------------------------------------------------
class NoteManuscript(NoteBase):
    owner = models.ForeignKey(Manuscript, on_delete=models.SET_NULL, null=True)

    class Meta(NoteBase.Meta):
        app_label = "fiches"


#===============================================================================
# CONTRIBUTIONS
#===============================================================================

# class ContributionDoc(models.Model):
#     person = models.ForeignKey(
#         'fiches.Person',
#         verbose_name=_("Contributeur"),
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='contribution_docs'  # Prevents reverse accessor clashes
#     )
#     document = models.ForeignKey(
#         'fiches.Document',
#         verbose_name=_("Document"),
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='contribution_docs_documents'  # Unique related_name
#     )
#     contribution_type = models.ForeignKey(
#         'fiches.ContributionType',
#         verbose_name=_("Type de contribution"),
#         limit_choices_to={'type__in': ['doc', 'any']},
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='contribution_docs_types'  # Unique related_name
#     )
#     biblio = models.ForeignKey(
#         'fiches.Biblio',  # Reference to 'fiches.Biblio'
#         verbose_name=_("Biblio"),
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='contribution_docs_biblio'  # Unique related_name
#     )
#     in_brackets = models.BooleanField(_("Entre crochets"), default=False)

#     def __str__(self):
#         return f"{self.person} ({self.contribution_type})"

#     class Meta:
#         app_label = "fiches"
#         verbose_name = _("Contribution pour Document")
#         verbose_name_plural = _("Contributions pour Document")
#         ordering = ('contribution_type', 'person')
#         unique_together = ('person', 'document', 'contribution_type', 'biblio')



# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\\
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\\
# ---------- Contribution Manuscrit
class ContributionMan(models.Model):
    person = models.ForeignKey(
        Person,
        verbose_name=_("Contributeur"),
        null=True,
        blank=True,  # Allows the field to be optional in forms
        on_delete=models.SET_NULL,
        related_name='contribution_mans'  # Prevents reverse accessor clashes
    )
    document = models.ForeignKey(
        Manuscript,
        verbose_name=_("Manuscrit"),
        null=True,         # Added null=True
        blank=True,        # Allows the field to be optional in forms
        on_delete=models.SET_NULL,
        related_name='contribution_mans_documents'  # Unique related_name
    )
    contribution_type = models.ForeignKey(
        ContributionType,
        verbose_name=_("Type de contribution"),
        limit_choices_to={'type__in': ['man', 'any']},
        null=True,
        blank=True,        # Allows the field to be optional in forms
        on_delete=models.SET_NULL,
        related_name='contribution_mans_types'  # Unique related_name
    )

    def __str__(self):
        return f"{self.person} ({self.contribution_type})"

    class Meta:
        app_label = "fiches"
        verbose_name = _("Contribution pour Manuscrit")
        verbose_name_plural = _("Contributions pour Manuscrit")
        unique_together = ('person', 'document', 'contribution_type')


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@//
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@//


#===============================================================================
# TRANSCRIPTION
#===============================================================================
TRANSCRIPTION_CHOICES = {
    'status': (
        (0, _("En cours")),
        (1, _("Fini"))
    ),
    'scope': (
        (0, _("Intégrale")),
        (1, _("Extrait"))
    ),
}

class TranscriptionManager(models.Manager):
    def last_published(self, count=5):
        return self.raw(
            'SELECT DISTINCT t.* FROM fiches_transcription t '
            'INNER JOIN fiches_activitylog l ON l.object_id = t.id '
            'WHERE l.model_name = "Transcription" AND t.access_public = 1 '
            'GROUP BY t.id '
            'ORDER BY MAX(l.date) DESC'
        )[:count]


from django.contrib.auth.models import User
from django.db import models

class Transcription(ACModel):
    manuscript = models.ForeignKey(
        "fiches.Manuscript",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    manuscript_b = models.ForeignKey(
        "fiches.Biblio",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    author = models.ForeignKey(
        User,
        verbose_name=_("Auteur"),
        related_name="transcriptions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    cite_author = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_("Citer l'auteur")
    )
    author2 = models.ForeignKey(
        User,
        verbose_name=_("2e auteur"),
        related_name="transcriptions2",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    cite_author2 = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_("Citer le 2e auteur")
    )

    status = models.IntegerField(
        _("État"),
        choices=TRANSCRIPTION_CHOICES['status'],
        default=0
    )
    scope = models.IntegerField(
        _("Transcription"),
        choices=TRANSCRIPTION_CHOICES['scope'],
        default=0
    )

    text = RichTextField(config_name='transcription_ckeditor', blank=True)
    envelope = RichTextField(
        verbose_name=_("Enveloppe"),
        config_name='envelope_ckeditor',
        blank=True
    )

    access_private = models.BooleanField(
        blank=True,
        default=True,
        verbose_name=_("Privé")
    )

    objects = TranscriptionManager()

    @property
    def reviewers(self):
        """
        Dynamically fetch the reviewers associated with this transcription.
        """
        return User.objects.filter(
            id__in=TranscriptionReviewer.objects.filter(
                transcription_id=self.id
            ).values_list('user_id', flat=True)
        )

    def __str__(self):
        man = self.manuscript_b or self.manuscript
        return u"%s" % (man.title if man else '---')

    def cite_authors(self):
        authors = []
        if self.cite_author and self.author:
            authors.append(self.author.get_full_name())
        if self.cite_author2 and self.author2:
            authors.append(self.author2.get_full_name())
        if authors:
            return " et ".join(authors) + " pour "
        return ''

    def get_absolute_url(self):
        return reverse('transcription-display', args=[str(self.id)])

    class Meta:
        app_label = "fiches"
        verbose_name = _("Fiche de transcription")
        verbose_name_plural = _("Fiches de transcription")
        ordering = ['manuscript_b__title']
        permissions = (
            ('change_transcription_ownership', "Can change ownership of Transcription"),
            ('change_any_transcription', "Can change any Transcription"),
            ('delete_any_transcription', "Can delete any Transcription"),
            ('publish_transcription', "Can Publish Transcription"),
            ('access_unpublished_transcription', "Can Access Unpublished Transcription"),
        )

class TranscriptionReviewer(models.Model):
    transcription = models.ForeignKey(
        'fiches.Transcription',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'fiches_transcription_reviewers'


#------------------------------------------------------------------------------
#    Note Transcription
#------------------------------------------------------------------------------
class NoteTranscription(NoteBase):
    owner = models.ForeignKey(
        Transcription,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta(NoteBase.Meta):
        app_label = "fiches"
