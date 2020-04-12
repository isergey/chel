#encoding: utf-8
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
import forum.models


def init_app(sender, **kwargs):
    print('Init forum module')
post_migrate.connect(init_app, sender=forum.models)



def init_groups(sender, **kwargs):
    group, created = Group.objects.get_or_create(name='forum_moderators')
    if group:
        print('\tGroup "forum_moderators" was created')
post_migrate.connect(init_groups, sender=forum.models)