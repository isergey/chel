from django.contrib.auth.models import User
from django.db.transaction import atomic
from django.utils import timezone
from huey.contrib.djhuey import db_task

from . import services


@db_task()
def send_letters():
    services.send_letters()
    services.send_to_email()
    services.clear_statuses()
