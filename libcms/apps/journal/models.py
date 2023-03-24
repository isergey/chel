import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

from crawlerdetect.detector import is_crawler

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

    def set_attributes(self, attributes: dict):
        if not attributes:
            return
        self.json_attributes = json.dumps(attributes, ensure_ascii=False)

    def get_attributes(self) -> dict:
        return json.loads(self.json_attributes) if self.json_attributes else {}

    def __str__(self):
        lines = [
            'action: ' + self.action,
            'user_id: ' + (self.user_id or '---'),
            'sc: ' + str(self.sc),
            'ip: ' + self.ip,
            'created: ' + str(self.created),
            'json_attributes: ' + (self.json_attributes or '---')
        ]
        return '\n'.join(lines)


def create_record(request, sc: str, action: str, attributes: dict = None):
    if is_crawler(request):
        return

    user_id = ''
    if request.user.is_authenticated:
        user_id = str(request.user.id)

    record = Record(
        sc=sc,
        ip=_get_client_ip(request),
        user_id=user_id,
        action=action,
    )

    record.set_attributes(attributes)

    Record.objects.bulk_create([record])


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@dataclass
class FilterParams:
    form_date: datetime = None
    to_date: datetime = None


def load_records(filter_params: FilterParams = FilterParams()) -> Iterator[Record]:
    next_id = None
    while True:
        if not next_id:
            q = Q()
        else:
            q = Q(id__gt=next_id)

        if filter_params.form_date:
            q &=Q(create__gte=filter_params.form_date)
        if filter_params.to_date:
            q &= Q(create__lte=filter_params.to_date)

        records = list(Record.objects.filter(q).order_by('created')[:2])

        if not records:
            break

        next_id = records[-1].id

        for record in records:
            yield record
