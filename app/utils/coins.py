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

from urllib.parse import quote_plus

#: Constants for doc_type
DOCTYPE_ARTICLE   = 0
DOCTYPE_BOOK_ITEM = 1
DOCTYPE_BOOK      = 2

def OpenURL(document, people, site_id=None):
    """
    OpenURL() constructs an NISO Z39.88-compliant ContextObject for use in OpenURL links and COinS.  
    It returns the query string, which you must embed in a <span> tag, for example:

        <span class="Z3988" title="%s">Your link text</span> % OpenURL(document, people)

    :param document: A dictionary describing the document. Expected keys:
        doc_type             -> 0 = Article, 1 = Book Item (chapter), 2 = Book
        doc_title            -> The title of the article/book/book item
        journal_title        -> Journal/magazine title if doc_type == ARTICLE
        journal_short_title  -> Abbreviation of the journal, optional
        book_title           -> For book items: title of the containing book
        volume               -> For articles: volume number
        journal_issue        -> For articles: issue number
        journal_season       -> e.g. 'Spring', 'Summer', etc. (optional)
        journal_quarter      -> e.g. 1 to 4 (optional)
        book_publisher       -> Book's publisher, optional
        pub_place            -> The place of publication, optional
        edition              -> String describing the edition
        ISBN                 -> The book's ISBN
        pages                -> For a complete book, total pages; or for article/book item, range
        start_page           -> Start page for an article/chapter
        end_page             -> End page for an article/chapter
        series               -> The name of any series in which the item appears
        doc_year             -> The publication year
        language             -> The language code or name, optional

    :param people: A list of dictionaries describing contributors/authors, each with keys:
        doc_relationship -> integer: 0 = author, 1 = editor, 2 = translator, 3 = contributor
        first_name       -> person's first name/initials
        last_name        -> person's last name
    :param site_id:  (optional) a string used in rfr_id to identify your site/app,
                     e.g. 'mysite.com:myapp'
    :return: A string suitable for embedding in the 'title' attribute of a span
             for COinS-based tools (Zotero, etc.).

    For references on how these fields map, see:
        - http://ocoins.info/
        - http://www.zotero.org/support/dev/making_coins
    """

    # Quick validation
    if not (document and isinstance(document, dict) and people is not None):
        return ""

    doc_type = document.get('doc_type')
    if doc_type not in (DOCTYPE_ARTICLE, DOCTYPE_BOOK_ITEM, DOCTYPE_BOOK):
        # If doc_type is missing or invalid, we can't proceed
        return ""

    # The key-value pairs we'll assemble into the query
    q_list = []

    # Indicate the OpenURL version
    q_list.append(("ctx_ver", "Z39.88-2004"))

    # Distinguish article vs. book for 'rft_val_fmt'
    if doc_type == DOCTYPE_ARTICLE:
        q_list.append(("rft_val_fmt", "info:ofi/fmt:kev:mtx:journal"))
    else:
        q_list.append(("rft_val_fmt", "info:ofi/fmt:kev:mtx:book"))

    # Optionally specify a 'site ID'
    if site_id:
        q_list.append(("rfr_id", f"info:sid/{site_id}"))

    # Extract main doc title
    doc_title = document.get('doc_title')

    # If it's an article, store 'article' genre and relevant fields
    if doc_type == DOCTYPE_ARTICLE:
        q_list.append(("rft.genre", "article"))
        if doc_title:
            q_list.append(("rft.atitle", doc_title))
        if document.get('journal_title'):
            jtitle = document['journal_title']
            q_list.append(("rft.jtitle", jtitle))
            q_list.append(("rft.title",  jtitle))
        if document.get('journal_short_title'):
            q_list.append(("rft.stitle", document['journal_short_title']))
        # Volume, Issue
        if document.get('volume'):
            q_list.append(("rft.volume", str(document['volume'])))
        if document.get('journal_issue'):
            q_list.append(("rft.issue", document['journal_issue']))
        # Optional season or quarter
        if document.get('journal_season'):
            q_list.append(("rft.ssn", document['journal_season']))
        if document.get('journal_quarter'):
            q_list.append(("rft.quarter", document['journal_quarter']))

    elif doc_type == DOCTYPE_BOOK_ITEM:
        q_list.append(("rft.genre", "bookitem"))
        if doc_title:
            # 'atitle' is sometimes used for the chapter or item
            q_list.append(("rft.atitle", doc_title))
        if document.get('book_title'):
            btitle = document['book_title']
            q_list.append(("rft.btitle", btitle))
            q_list.append(("rft.title",  btitle))

    elif doc_type == DOCTYPE_BOOK:
        q_list.append(("rft.genre", "book"))
        if doc_title:
            q_list.append(("rft.btitle", doc_title))
            q_list.append(("rft.title",  doc_title))

    # For books or book items, we might have the publisher, place, edition, ISBN
    if doc_type in (DOCTYPE_BOOK, DOCTYPE_BOOK_ITEM):
        if document.get('book_publisher'):
            q_list.append(("rft.pub", document['book_publisher']))
        if document.get('pub_place'):
            q_list.append(("rft.place", document['pub_place']))
        if document.get('edition'):
            q_list.append(("rft.edition", document['edition']))
        if document.get('ISBN'):
            q_list.append(("rft.isbn", str(document['ISBN'])))

    # Pages
    if document.get('pages'):
        q_list.append(("rft.pages", document['pages']))
        # If it's a complete book, sometimes 'rft.tpages' is used
        if doc_type == DOCTYPE_BOOK:
            q_list.append(("rft.tpages", document['pages']))

    # Start/end pages for articles or book items
    if doc_type in (DOCTYPE_ARTICLE, DOCTYPE_BOOK_ITEM):
        if document.get('start_page'):
            q_list.append(("rft.spage", document['start_page']))
        if document.get('end_page'):
            q_list.append(("rft.epage", document['end_page']))

    # Series
    if document.get('series'):
        q_list.append(("rft.series", document['series']))
        # Some examples use rft.issn for the series
        q_list.append(("rft.issn",  document['series']))

    # Year/date
    if document.get('doc_year'):
        q_list.append(("rft.date", document['doc_year']))

    # Language
    if document.get('language'):
        q_list.append(("rft.language", document['language']))

    # People - treat doc_relationship=0 as an author, else as a contributor
    # 0=author, 1=editor, 2=translator, 3=contributor
    # There's no official standard for 'editor' or 'translator' in the COinS
    # standard, so often we just store them as contributor as well.
    for p in people:
        rel = p.get('doc_relationship', 3)  # default to 'contributor'
        fn  = p.get('first_name', "")
        ln  = p.get('last_name', "")
        # Convert names to "Lastname,+Firstname" format
        person_str = f"{ln},+{fn}"
        if rel == 0:
            # author
            q_list.append(("rft.au", person_str))
        else:
            # everything else => contributor
            q_list.append(("rft.contributor", person_str))

    # Build the final query string, with &amp; separating fields
    parts = []
    for key, val in q_list:
        if val:  # skip empty
            # must encode to UTF-8 before quote_plus
            encoded_val = quote_plus(val.encode("utf-8"))
            parts.append(f"{key}={encoded_val}")

    # Join with &amp; for embedding in an HTML attribute
    query_string = "&amp;".join(parts)
    return query_string
