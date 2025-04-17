from django.apps import apps

# Lazy loading of ContributionDoc and ContributionMan to prevent circular imports
def get_contribution_doc_model():
    return apps.get_model('fiches', 'ContributionDoc')

def get_contribution_man_model():
    return apps.get_model('fiches', 'ContributionMan')

# Direct imports for models that are not causing circular import issues
from .keyword import PrimaryKeyword, SecondaryKeyword

__all__ = ['get_contribution_doc_model', 'get_contribution_man_model', 'PrimaryKeyword', 'SecondaryKeyword']
