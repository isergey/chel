# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from guardian.decorators import permission_required_or_403

from common.pagination import get_page
from django.contrib.auth.models import User, Group

from forms import UserForm






#@permission_required_or_403('accounts.can_deliver_pizzas')
def index(request):
    return render(request, 'administration/index.html')



def users_list(request):
    users_page = get_page(request,  User.objects.all().exclude(id=-1))
    return render(request, 'administration/user_list.html', {
        'users_page': users_page
    })

def edit_user(request, id):
    user = get_object_or_404(User, id=id)
    form = UserForm(instance=user)
    return render(request, 'administration/edit_user.html', {
        'user': user,
        'form': form
    })



def groups_list(request):
    groups_page = get_page(request,  Group.objects.all())
    return render(request, 'administration/groups_list.html', {
        'groups_page': groups_page
    })