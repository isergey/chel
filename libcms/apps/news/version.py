from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from pydantic import BaseModel

from versioning.service import add_version
from .models import NewsContent


class NewsContentVersion(BaseModel):
    title: str
    teaser: str
    content: str


def save_content_version(content: NewsContent, user: User):
    content_version = NewsContentVersion(
        title=content.title,
        meta=content.teaser,
        content=content.content
    )
    content_type = ContentType.objects.get_for_model(content)

    add_version(
        content_type=content_type.app_labeled_name,
        content_id=str(content.id),
        content=content_version.json(ensure_ascii=False),
        user=user
    )