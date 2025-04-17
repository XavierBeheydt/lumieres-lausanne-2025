# fiches/models/keyword.py

from django.db import models

class PrimaryKeyword(models.Model):
    word = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = "Primary Keyword"
        verbose_name_plural = "Primary Keywords"


class SecondaryKeyword(models.Model):
    word = models.CharField(max_length=100, unique=True)
    primary_keyword = models.ForeignKey(
        PrimaryKeyword,
        on_delete=models.CASCADE,
        db_column='parent_id',
        related_name='secondary_keywords',
        verbose_name='Primary Keyword'
    )

    def __str__(self):
        return f"{self.word} ({self.primary_keyword})"

    class Meta:
        verbose_name = "Secondary Keyword"
        verbose_name_plural = "Secondary Keywords"
        managed = False
        db_table = "fiches_secondarykeyword"
