# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User, Group
from ldapwork.ldap_work import LdapWork, LdapConnection
from arbicon.models import Organisation, OrganisationGroups, OrganisationUser
username_postfix = u'.arbicon.ru'
group_prefix = u'arbicon.'

class LdapBackend:
    def authenticate(self, username=None, password=None, session=None):
        if len(password) == 0:
            return None


        result = self.get_or_create_user(username, password)
        return result

    @transaction.commit_on_success
    def get_or_create_user(self, username, password):
        """
            Функция принимает имя пользователя и пароль. Если на LDAP сервере существует
        подходящий пользователь - проверяется его наличие в локальной базе, если в 
        базе его не оказалось, то пользователь создается в локальной базе(синхронизация 
        с LDAP пользователем) и возвращается как User, попутно присваивая ему группу 
        для доступа к функциям сайта.
            Если пользователя не существует в LDAP, но существует в локальной базе,
        проверяем его на принадлежность к супер админу, если супер админ, то логиними
        если не супер админ - удаляем.
        """




        ldap_connection = LdapConnection(settings.LDAP)
        ldap_work = LdapWork(ldap_connection)


        # Филтр запроса на получение объета пользователя
        # filter = '(&(uid=%s)(objectClass=RUSLANperson)(userPassword=%s))' % (username, password)
        # аттрибуты, которые будут извлечены для обработки
        # attrs = ['uid','sn','memberOf','userPassword','mail','telephoneNumber']

        # ldap_results = ldap_connection.search_s( settings.LDAP_BASE_DN, ldap.SCOPE_SUBTREE, filter, attrs )
        ldap_users = ldap_work.get_users_by_attr(username=username, password=password)

        # если пользователь не существет в LDAP
        # проверяем, существует ли он в локальной базе
        # если да, то удаляем его
        if not ldap_users:
            try:
                user = User.objects.get(username=(username + username_postfix))
                if user.is_superuser:
                    return user
                user.delete()
            except User.DoesNotExist:
                pass
            return None

        try:

            user = User.objects.get(username=(username + username_postfix))

        except User.DoesNotExist:

            ldap_user = ldap_users[0]

            user_name = ldap_user.name.split()
            first_name = u''
            last_name = u''

            if len(user_name) == 3:
                first_name = (user_name[1] + u' ' + user_name[2])[0:30]
                last_name = user_name[0][0:30]
            elif len(user_name) == 2:
                first_name = user_name[1][0:30]
                last_name = user_name[0][0:30]
            elif len(user_name) == 1:
                last_name = user_name[0][0:30]

            user = User(username=(ldap_user.uid + username_postfix), email=ldap_user.email, first_name=first_name, last_name=last_name)

            user.is_superuser = False
            user.set_password(password)
            user.save()

            orgs = []
            if len(ldap_user.dn) > 3:
                orgs = ldap_work.get_org_by_attr(o=ldap_user.dn[1],node='.')

            if orgs:
                org = orgs[0]
                try:
                    organistion = Organisation.objects.get(name=org.o[0:255])
                except Organisation.DoesNotExist:
                    organistion = Organisation(name=org.o[0:255])
                    organistion.save()
                groups = []
                for member in org.member_of:
                    try:
                        group = Group.objects.get(name=(group_prefix + member.lower()))
                    except Group.DoesNotExist:
                        group = Group(name=(group_prefix + member.lower()))
                        group.save()

                    groups.append(group)

                    try:
                        og = OrganisationGroups.objects.get(organistion=organistion, group=group)
                    except OrganisationGroups.DoesNotExist:
                        og = OrganisationGroups(organistion=organistion, group=group)
                        og.save()

                try:
                    organistion_user = OrganisationUser.objects.get(organistion=organistion , user=organistion)
                except OrganisationUser.DoesNotExist:
                    organistion_user = OrganisationUser(organistion=organistion, user=user)
                    organistion_user.save()
                    user.groups = groups
                    #user.save()

        return user


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _get_ldap_attribute_first(self, attr_map, key):
        """
        Функция получает на вход карту вида
        attr_map = {
            'key':['value1','valueN']
        }
        и возвращает первый элемент из списка key
        Если ключ или значение не найдено, возвращается None
        """
        if attr_map.has_key(key):
            if len(attr_map[key]) > 0: return attr_map[key][0]
            else: return None
        else: return None
