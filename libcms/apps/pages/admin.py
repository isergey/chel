from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from . import models

admin.site.register(models.Page, MPTTModelAdmin)