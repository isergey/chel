import datetime
from django.db import models

class Upload(models.Model):
    """Uploaded files."""
    file = models.FileField(upload_to='uploads',)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-timestamp',]

    def __unicode__(self):
        return u"%s" % (self.file)

    @property
    def size(self):
        return filesizeformat(self.file.size)


