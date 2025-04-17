# fiches/models/finding.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from sorl.thumbnail import ImageField  # Ensure sorl-thumbnail is installed
from ckeditor.fields import RichTextField

from fiches.models.content.image import Image
from fiches.models.documents.document import Document

class Finding(models.Model):
    title = models.CharField(_("Titre"), max_length=200)

    created_on = models.DateTimeField(verbose_name='créé le', auto_now_add=True)
    modified_on = models.DateTimeField(verbose_name='modifié le', auto_now=True)
    published = models.BooleanField(
        _("Publié"),
        default=False,
        help_text=_("Cocher pour donner un accès public.")
    )
    author = models.ForeignKey(User, verbose_name=_("Auteur"), on_delete=models.SET_NULL, null=True, blank=True)
    author2 = models.ForeignKey(
        User,
        verbose_name=_("2e auteur"),
        related_name="finding_set2",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    description = models.TextField(_("Description"))
    thumbnail = ImageField(_("Vignette"), upload_to='images/%Y/%m')  # Using sorl-thumbnail's ImageField
    content = RichTextField(verbose_name=_("Contenu"), config_name='project_ckeditor')

    images = GenericRelation(Image)
    documents = GenericRelation(Document)

    class Meta:
        verbose_name = _("Trouvaille")
        ordering = ['-created_on']
        app_label = "fiches"

    def __str__(self):
        return self.title
