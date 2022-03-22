from typing import Optional

from django.db.models import Model
from django.contrib.auth.models import User
from django.core.serializers import serialize

from .models import Version


def add_version(content_type: str, content_id: str, content: str, user: Optional[User]):
    exists_version = Version.objects.filter(content_type=content_type, content_id=content_id).order_by('-created').first()
    if exists_version is not None and exists_version.content == content:
        return
    Version(
        content_type=content_type,
        content_id=content_id,
        user=user,
        content=content
    ).save()



