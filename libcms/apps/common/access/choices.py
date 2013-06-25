# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group

def get_groups_choices():
    choices = []
    groups = Group.objects.all()

    for group in groups:
        choices.append((group.id, group.name.lower()))

    return choices