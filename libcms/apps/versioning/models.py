from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Version(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    content_type = models.CharField(max_length=128, db_index=True)
    content_id = models.CharField(max_length=128, db_index=True)
    content = models.TextField(max_length=100 * 1000)
    created = models.DateTimeField(auto_now_add=True, db_index=True)


