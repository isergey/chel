# -*- coding: utf-8 -*-
from django import template
from django.core.cache import cache
from arbicon.models import OrganisationUser

register = template.Library()

@register.filter
def get_user_org(user):
    org = cache.get(u"user_org_" + unicode(user.username), None)
    if org:
        if org == u"0":
            return u""
        else:
            return org

    try:
        org_user = OrganisationUser.objects.select_related().get(user=user)
    except OrganisationUser.DoesNotExist:
        cache.set(u"user_org_" + user.username, u'0')
        return u""

    cache.set(u"user_org_" + user.username, org_user.organistion.name)
    return org_user.organistion.name

