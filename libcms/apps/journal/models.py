import json
import uuid

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Record(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sc = models.UUIDField(db_index=True)
    ip = models.GenericIPAddressField()
    user_id = models.CharField(
        max_length=64,
        blank=True
    )
    action = models.CharField(
        max_length=128,
        db_index=True,
        blank=True
    )

    json_attributes = models.TextField(
        max_length=10 * 1024,
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True, db_index=True)


def create_record(request, sc: str, action: str, attributes: dict = None):
    user_id = ''
    if request.user.is_authenticated:
        user_id = str(request.user.id)

    attributes_content = ''
    if attributes is not None:
        attributes_content = json.dumps(attributes, ensure_ascii=False)

    Record.objects.bulk_create([Record(
        sc=sc,
        ip=_get_client_ip(request),
        user_id=user_id,
        action=action,
        json_attributes=attributes_content
    )])


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
