# utils_coins.py
from django.utils.safestring import mark_safe
from .coins import OpenURL, DOCTYPE_ARTICLE, DOCTYPE_BOOK_ITEM, DOCTYPE_BOOK

def get_doc_coins(biblio_obj):
    """
    Build a COinS <span> snippet so that Zotero or other tools can detect metadata.
    """
    # Suppose your Biblio document_type.code is an int:
    dt_code = biblio_obj.document_type.code  # e.g. 1 => "journal", 2 => "book" ...
    if dt_code == 1:
        doc_type = DOCTYPE_ARTICLE
    elif dt_code == 2:
        doc_type = DOCTYPE_BOOK
    elif dt_code == 3:
        doc_type = DOCTYPE_BOOK_ITEM
    else:
        # fallback if code is something else
        doc_type = DOCTYPE_BOOK

    document_dict = {
        'doc_type': doc_type,
        'doc_title': biblio_obj.title,
        'journal_title': biblio_obj.journal_title,
        'book_title': biblio_obj.book_title,
        # ... fill in the rest
    }

    people = []
    for contrib in biblio_obj.contributiondoc_set.all():
        doc_rel = 0  # 0 => author, adjust as needed
        # If you have logic for editor, translator, etc. do so here
        first_name = ''
        last_name = ''
        if contrib.person:
            last_name = contrib.person.name or ''
        people.append({
            'doc_relationship': doc_rel,
            'first_name': first_name,
            'last_name': last_name,
        })

    openurl_str = OpenURL(document_dict, people, site_id='mysite.com:myapp')
    if not openurl_str:
        return ""

    return mark_safe(f'<span class="Z3988" title="{openurl_str}"></span>')
