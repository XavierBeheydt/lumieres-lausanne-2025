# models/ac_model.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class ACModel(models.Model):
    access_owner = models.ForeignKey(
        User,
        verbose_name=_("Propriétaire"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    access_public = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_("Public"),
        help_text=_("L'élément sera visible par tout le monde.")
    )
    access_groups = models.ManyToManyField(
        "fiches.UserGroup",  # Lazy import of UserGroup
        verbose_name=_("Groupes d'accès"),
        blank=True
    )

    class Meta:
        abstract = True

    def user_access(self, user, any_login=False):
        """
        Check if the user has access to the object.

        If `any_login` is True, any authenticated user is granted access
        if no `access_groups` are defined.
        """
        # Object is not yet saved => access granted
        if not self.id:
            return True

        # Handle access_private if present in a subclass
        if hasattr(self, 'access_private') and self.access_private:
            return self.access_owner == user

        # If user is not authenticated, only public objects are visible
        if not user.is_authenticated:
            return self.access_public

        # If object is public, user has access
        if self.access_public:
            return True

        # If owner, user has access
        if self.access_owner == user:
            return True

        # Lazy import of UserGroup to avoid circular imports
        from fiches.models.core.user_group import UserGroup

        # Direct membership in `access_groups`
        if UserGroup.objects.filter(users=user, id__in=self.access_groups.values_list('id', flat=True)).exists():
            return True

        # Indirect membership via Django groups
        if self.access_groups.filter(groups__in=user.groups.all()).exists():
            return True

        # If `any_login` is True and no access_groups are defined
        if any_login and not self.access_groups.exists():
            return True

        # No access granted
        return False
