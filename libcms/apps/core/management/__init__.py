#encoding: utf-8
from django.contrib.auth.models import Group
from django.db.models.signals import post_syncdb
import core.models


def init_app(sender, **kwargs):
    print 'Init core module'
post_syncdb.connect(init_app, sender=core.models)



def init_groups(sender, **kwargs):
    group, created = Group.objects.get_or_create(name='users')
    if group:
        print '\tGroup "users" was created'

    group, created = Group.objects.get_or_create(name='anonymouses')
    if group:
        print '\tGroup "anonymouses" was created'
post_syncdb.connect(init_groups, sender=core.models)