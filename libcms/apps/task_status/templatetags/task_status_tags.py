# -*- coding: utf-8 -*-
from django import template

register = template.Library()
from .. import utils


@register.simple_tag
def get_task_status(name):
    print('get_task_status', name)
    return utils.get_task_status(name)
