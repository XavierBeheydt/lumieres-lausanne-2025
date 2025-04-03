# -*- coding: utf-8 -*-
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
from haystack.indexes import *
from haystack import indexes #site
from django.db.models import Q
from fiches.models import DocumentFile, PrimaryKeyword, SecondaryKeyword, Person, Society, NoteBase, ACModel
from fiches.models.document import Biblio, Manuscript, Transcription


# Migrating from haystack 1.x to 2.x
# https://django-haystack.readthedocs.io/en/master/migration_from_1_to_2.html

class BiblioIndex(indexes.SearchIndex, indexes.Indexable):
    text            = indexes.CharField(document=True, use_template=True)
    authors         = indexes.CharField(use_template=True)
    biblio_persons  = indexes.MultiValueField()
    title           = indexes.CharField(model_attr='title')
    modelSort       = indexes.CharField(default="BBB")
    doctype         = indexes.CharField(model_attr="document_type__id")
    sort1           = indexes.CharField(model_attr='first_author_name', null=True)
    sort2           = indexes.CharField(model_attr='date', null=True)

    def prepare_biblio_persons(self, obj):
        result = [str(p) for p in obj.subj_person.all()]
        return result

    # deprecated in haystack 2+
    # def get_queryset(self):
    #     return Biblio.objects.all()

    def get_model(self):
        return Biblio

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated.""" 
        return self.get_model().objects.all()



#class ManuscriptIndex(SearchIndex):
#    text = CharField(document=True, use_template=True, template_name='search/indexes/fiches/biblio_text.txt')
#    title = CharField(model_attr='title')
#    modelSort = CharField(default="CCC")
#    def get_queryset(self):
#        return ManuscriptB.objects.all()
#site.register(ManuscriptB, ManuscriptIndex)


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text        = indexes.CharField(document=True, use_template=True)
    person_name = indexes.CharField(model_attr='name')
    modelSort   = indexes.CharField(default="AAA")
    sort1       = indexes.CharField(model_attr='name', null=True)
    sort2       = indexes.CharField(default="")

    # deprecated in haystack 2+
    # def get_queryset(self):
    #     return Person.objects.filter(biography__isnull=False, biography__valid=True).distinct()

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        #return Person.objects.filter(biography__isnull=False, biography__valid=True).distinct() # works but check if it is the right way
        #print ("results PersonIndex: ", self.get_model().objects.filter(biography__isnull=False, biography__valid=True).distinct())
        return self.get_model().objects.filter(biography__isnull=False, biography__valid=True).distinct() # recommanded way in haystack 2+ documentation


class TranscriptionIndex(indexes.SearchIndex, indexes.Indexable):
    text        = indexes.CharField(document=True, use_template=True)
    modelSort   = indexes.CharField(default="DDD")
    sort1       = indexes.CharField(model_attr='manuscript_b__first_author_name', null=True)
    sort2       = indexes.CharField(model_attr='manuscript_b__date', null=True)

    # deprecated in haystack 2+
    # def get_queryset(self):
    #     return Transcription.objects.all()

    def get_model(self):
        return Transcription
    
    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all() # recommanded way in haystack 2+ documentation
