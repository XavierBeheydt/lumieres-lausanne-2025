# models/notes.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from django.contrib.auth.models import Group
from ckeditor.fields import RichTextField

from fiches.models.contributions.ac_model import ACModel


class NoteBase(ACModel):
    """
    Abstract base model for notes.
    """
    text = RichTextField(verbose_name=_("Note"), config_name='note_ckeditor', blank=True)
    groups = models.ManyToManyField(Group, blank=True, verbose_name=_("Visible pour"))

    class Meta:
        abstract = True
        permissions = (
            ("can_see_note", "Can see Note"),
            ("can_publish_note", "Can publish note"),
        )

    def __str__(self):
        return strip_tags(self.text[:30])


# Concrete implementation of NoteBase
class Note(NoteBase):
    """
    Concrete implementation of the NoteBase model.
    """
    pass


# Commented out NoteForm for now to prevent issues
# class NoteForm(ModelForm):
#     """
#     Form for the concrete Note model.
#     """
#     class Meta:
#         model = Note
#         fields = '__all__'

#     def clean_text(self):
#         data = self.cleaned_data['text']
#         return data
