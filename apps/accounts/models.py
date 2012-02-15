# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models


class Permissions(User):
    """
    Класс для создания прав достпа
    """
    class Meta:
        proxy = True
        permissions = (
            ("view_users", "Can view users list"),
            ("view_groups", "Can view groups list"),
        )

