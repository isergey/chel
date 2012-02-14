# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

class CommonInfo(User):
    class Meta:
        proxy = True
        permissions = (("can_deliver_pizzas", "Can deliver pizzas"),)