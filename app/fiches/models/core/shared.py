from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """
    Abstract base model for shared functionality.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

def get_usergroups_for_user(user):
    """
    Utility function to retrieve user groups for a given user.
    """
    from fiches.models.core.user_group import UserGroup  # Lazy import to avoid circular imports
    from django.db.models import Q

    q1 = Q(users=user)
    q2 = Q(groups__in=user.groups.all())
    return UserGroup.objects.filter(q1 | q2).distinct()
