from django.db import models


class Record(models.Model):
    namespace = models.CharField(max_length=256, db_index=True)
    key = models.CharField(max_length=256, db_index=True)
    value = models.TextField(max_length=10 * 1024)

    class Meta:
        unique_together = [['namespace', 'key']]
        ordering = ['namespace', 'key']