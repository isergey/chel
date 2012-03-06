# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'Название организации', unique=True)
    weight = models.IntegerField(default=0, verbose_name=u'Вес организации')
    def __unicode__(self):
        return self.name


class OrganisationGroups(models.Model):
    organistion = models.ForeignKey(Organisation)
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return unicode(self.organistion) + u": " + unicode(self.group)
    class Meta:
        unique_together = ('group', 'organistion')

    def get_org_groups(cls, organistion):
        org_groups = OrganisationGroups.objects.filter(organistion=organistion)
        groups_ids = []
        for org_group in org_groups:
            groups_ids.append(org_group.group_id)

        if groups_ids:
            return Group.objects.filter(id__in=groups_ids)
        return []


class OrganisationUser(models.Model):
    organistion = models.ForeignKey(Organisation, verbose_name=u'Организация, к которой принадлежит пользователь')
    user = models.ForeignKey(User, unique=True, verbose_name=u'Пользователь')
    def __unicode__(self):
        return unicode(self.user) + u": " + unicode(self.organistion)

    class Meta:
        unique_together = ('organistion', 'user')


#    def inherit_org_groups(self):
