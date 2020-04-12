# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from guardian.shortcuts import get_groups_with_perms, assign, remove_perm, get_perms_for_model

def check_perm_for_model(perm_name, model):
    perms =  get_perms_for_model(model)
    for perm in perms:
        if perm.codename == perm_name:
            return True
    return False


def assign_perm_for_groups_id(perm_name, object, groups_ids):
    groups = Group.objects.filter(pk__in=groups_ids)
    for group in groups:
        assign(perm_name, group, object)


def remove_perm_for_groups_id(perm_name, object, groups_ids):
    groups = Group.objects.filter(pk__in=groups_ids)
    for group in groups:
        remove_perm(perm_name, group, object)


def get_group_ids_for_object_perm(perm_name, object):
    groups_dict = get_groups_with_perms(object, attach_perms=True)
    groups_ids = []
    for (group, perms) in  groups_dict.items():
        if perm_name in perms: groups_ids.append(str(group.id))
    return groups_ids


def edit_group_perms_for_object(perm_name, object, old_perm_groups_ids, new_perm_groups_ids):
    remove_perm_groups_ids = []

    for id in old_perm_groups_ids:
        if id not in new_perm_groups_ids:
            remove_perm_groups_ids.append(id)

    if remove_perm_groups_ids:
        remove_perm_for_groups_id(perm_name, object, remove_perm_groups_ids)

    assign_perm_groups_ids = []

    for i in new_perm_groups_ids:
        if i not in old_perm_groups_ids:
            assign_perm_groups_ids.append(i)

    assign_perm_for_groups_id(perm_name, object, assign_perm_groups_ids)

