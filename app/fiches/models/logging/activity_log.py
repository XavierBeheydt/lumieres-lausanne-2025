# models/activity_log.py

from django.db import models, connection, transaction
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.apps import apps

class ObjectActivities(models.Manager):
    """
    Add a Manager method to filter the activities related to a specific object.
    """
    def activities(self, **kwargs):
        qs = super().get_queryset()
        if 'object' in kwargs:
            obj = kwargs['object']
            try:
                qs = qs.filter(model_name=obj.__class__.__name__, object_id=obj.id)
            except:
                qs = qs.none()
        return qs


class ActivityLog(models.Model):
    object_id  = models.IntegerField()
    model_name = models.CharField(verbose_name=_("Type d'objet"), max_length=256)
    user       = models.ForeignKey(User, verbose_name=_("Utilisateur"), on_delete=models.CASCADE)
    date       = models.DateTimeField(auto_now_add=True)
    p_orphan   = models.BooleanField(default=False, blank=True, editable=False)

    objects    = ObjectActivities()

    @property
    def object_info(self):
        try:
            model = apps.get_model('fiches', self.model_name)
            obj = model.objects.get(pk=self.object_id)
            model_name = model._meta.verbose_name
            # If old code changed model_name for Person objects to Biography’s verbose name,
            # reintroduce that logic here if Biography still exists:
            # from fiches.models.biography import Biography
            # if self.model_name == 'Person':
            #     model_name = Biography._meta.verbose_name

            return {'model_name': model_name, 'object_name': str(obj), 'object': obj }
        except:
            return None

    def get_object(self):
        try:
            model = apps.get_model('fiches', self.model_name)
            return model.objects.get(pk=self.object_id)
        except:
            return None

    @staticmethod
    def sanitize():
        """
        Find any orphan entries (related to non-existing/deleted objects)
        and set p_orphan = True where objects no longer exist.
        """
        cursor = connection.cursor()
        model_names = [m['model_name'] for m in ActivityLog.objects.values('model_name').distinct()]

        for model_name in model_names:
            model = apps.get_model('fiches', model_name)
            object_table = model._meta.db_table
            activity_table = ActivityLog._meta.db_table
            query = f"""
                UPDATE `{activity_table}`
                LEFT JOIN `{object_table}` ON (`{object_table}`.`id` = `{activity_table}`.`object_id`)
                SET `{activity_table}`.`p_orphan` = 1
                WHERE `{activity_table}`.`model_name` = '{model_name}'
                AND `{object_table}`.`id` IS NULL;
            """
            cursor.execute(query)
            # Using commit() since commit_unless_managed() is removed in newer Djangos
            transaction.commit()

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        return f"{name} - {self.date.isoformat()}"

    class Meta:
        verbose_name = _("Activité")
