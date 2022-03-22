from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from pydantic import BaseModel

from versioning.service import add_version
from .models import Content


class ContentVersion(BaseModel):
    title: str
    meta: str
    meta_description: str
    content: str


def save_content_version(content: Content, user: User):
    content_version = ContentVersion(
        title=content.title,
        meta=content.meta,
        meta_description=content.meta_description,
        content=content.content
    )
    content_type = ContentType.objects.get_for_model(content)

    add_version(
        content_type=content_type.app_labeled_name,
        content_id=str(content.id),
        content=content_version.json(ensure_ascii=False),
        user=user
    )