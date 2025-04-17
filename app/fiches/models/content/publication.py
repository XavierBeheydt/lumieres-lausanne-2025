# fiches/models/content/publication.py

from django.db import models

class Publication(models.Model):
    # This model stores publications
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        db_table = 'fiches_publication'

    def __str__(self):
        return self.title
