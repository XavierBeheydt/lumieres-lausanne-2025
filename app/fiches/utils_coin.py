# -*- coding: utf-8 -*-
#
#    [License Information]
#
#    This file is part of Lumières.Lausanne.
#    [License Details]
#

from django.utils.safestring import mark_safe
from utils.coins import OpenURL
from fiches.models.documents.document import ContributionDoc
from fiches.models.contributiontype import ContributionType

def get_doc_co(doc):
    """
    Constructs a ContextObject to be used in OpenURL coins.
    Refer to lumieres.utils.coins.OpenURL for more details.
    """
    try:
        doc_year = "%s" % doc.date.year
    except AttributeError:
        doc_year = None

    document = {
        'doc_type'            : doc.document_type.code,
        'doc_title'           : doc.title,
        'book_title'          : doc.book_title,
        'book_publisher'      : doc.publisher,
        'pub_place'           : doc.place,
        'edition'             : doc.edition,
        'journal_title'       : doc.journal_title,
        'journal_short_title' : doc.journal_abr,
        'volume'              : doc.volume,
        'journal_issue'       : doc.journal_num,
        'ISBN'                : doc.isbn,
        'pages'               : doc.pages,
        'series'              : doc.serie,
        'doc_year'            : doc_year,
    }

    # Update the related_name from 'contributiondoc_set' to 'contribution_documents_documents'
    people = tuple([
        {
            'doc_relationship': c.contribution_type.code,
            'first_name'      : (c.person.get_first_name() if c.person else None),
            'last_name'       : (c.person.get_last_name() if c.person else None),
        } 
        for c in doc.contribution_documents_documents.all()
    ])

    return mark_safe(OpenURL(document, people))


def get_doc_coins(doc):
    """
    Returns the COinS tag for Zotero.
    """
    return mark_safe('<span class="Z3988" title="%s"></span>' % get_doc_co(doc))
