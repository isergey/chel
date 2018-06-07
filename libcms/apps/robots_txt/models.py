from django.db import models


class RobotsTxt(models.Model):
    content = models.TextField(max_length=10 * 1024, blank=True)
    update_date = models.DateTimeField(auto_now=True)