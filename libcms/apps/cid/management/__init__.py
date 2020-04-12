from django.db.models.signals import post_migrate
import cid.models

from ..models import types, Type

def create_types(sender, **kwargs):
    for type_item in types:
        Type.objects.get_or_create(variant=type_item[0])

post_migrate.connect(create_types, sender=cid.models)