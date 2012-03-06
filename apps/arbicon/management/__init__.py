#encoding: utf-8

from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import Group
from django.db.models.signals import post_syncdb
import arbicon.models
from arbicon.auth.ldapwork.ldap_work import LdapConnection, LdapWork
from arbicon.models import Organisation, OrganisationGroups
group_prefix = u'arbicon.'

@transaction.commit_on_success
def init_app(sender, **kwargs):
    """
    Синхронизация организаций с LDAP базой арбикон
    """
    print 'Init arbicon module'
    ldap_connection = LdapConnection(settings.LDAP)
    ldap_work = LdapWork(ldap_connection)
    print '\t Import organisations from ldap...'
    for org in  ldap_work.get_org_by_attr(node='.'):
        try:
            organistion = Organisation.objects.get(name=org.o[0:255])
        except Organisation.DoesNotExist:
            organistion = Organisation(name=org.o[0:255])
            organistion.save()

        for member in org.member_of:
            try:
                group = Group.objects.get(name=(group_prefix + member.lower()))
            except Group.DoesNotExist:
                group = Group(name=(group_prefix + member.lower()))
                group.save()
            try:
                og = OrganisationGroups.objects.get(organistion=organistion, group=group)
            except OrganisationGroups.DoesNotExist:
                og = OrganisationGroups(organistion=organistion, group=group)
                og.save()
    print '\t Import organisations from ldap complete.'

post_syncdb.connect(init_app, sender=arbicon.models)


#
#def init_groups(sender, **kwargs):
#    arbicon_members, created = Group.objects.get_or_create(name='arbicon_members')
#    if arbicon_members:
#        print '\tGroup "arbicon_members" was created'
#
#post_syncdb.connect(init_groups, sender=arbicon.models)