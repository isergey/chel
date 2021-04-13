# coding=utf-8
import json
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


class ExternalUser(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='Связь с пользователем',
        blank=True, null=True,
        on_delete=models.CASCADE
    )

    external_username = models.CharField(
        verbose_name='Имя пользователя во внешней системе',
        max_length=255,
        db_index=True
    )

    auth_source = models.CharField(
        verbose_name='Идентфикатор источника аутенификации',
        max_length=32,
        db_index=True
    )

    attributes = models.TextField(
        verbose_name='Атрибуты пользователя в формате JSON',
        max_length=10 * 1024
    )

    update = models.DateTimeField(auto_now=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ['external_username', 'auth_source']

    def get_attributes(self):
        return json.loads(self.attributes)

    def set_attributes(self, attributes=None):
        self.attributes = json.dumps(attributes or {}, ensure_ascii=False)

    def clean(self):
        try:
            json.loads(self.attributes)
        except ValueError:
            raise ValidationError('Значение "Атрибуты пользователя" должно быть JSON строкой')


@receiver(post_delete, sender=ExternalUser)
def on_external_user_delete(sender, **kwargs):
    User.objects.filter(id=kwargs['instance'].user_id).delete()


def get_external_users(user, auth_source=None):
    q = models.Q(user=user)
    if auth_source:
        q = q & models.Q(auth_source=auth_source)
    return ExternalUser.objects.filter(q)


def find_external_user(external_username, auth_source) -> User:
    """
    Найти пользователя из внешней системы
    :param external_username:
    :param auth_source:
    :return: User или None
    """
    cleaned_external_username = external_username.strip().lower()
    cleaned_auth_source = auth_source.strip().lower()
    external_user = ExternalUser.objects.select_related('user').filter(
        external_username=cleaned_external_username,
        auth_source=cleaned_auth_source
    ).first()

    if external_user is not None:
        return external_user.user

    return None


@transaction.atomic()
def create_or_update_external_user(
        external_username,
        auth_source,
        attributes={},
        first_name='',
        last_name='',
        email='',
        is_active=None,
        is_staff=None,
        is_superuser=None,
        groups=['users']) -> ExternalUser:
    """
    Создание или обновление пользователя из внешней системы аутентификации
    :param external_username: Имя пользователя во внешней системе
    :param auth_source: Идентификатор внешней системы
    :param attributes: Хеш атрибутов внешнего пользователя
    :param first_name:
    :param last_name:
    :param email:
    :param is_active:
    :param is_staff:
    :param is_superuser:
    :param groups: названия групп, в которые нужно добавить пользователя
    :return:
    """
    cleaned_external_username = external_username.strip().lower()
    cleaned_auth_source = auth_source.strip().lower()

    try:
        external_user = ExternalUser.objects.get(
            external_username=cleaned_external_username,
            auth_source=cleaned_auth_source
        )
        if external_user.get_attributes() != attributes:
            external_user.set_attributes(attributes)
            external_user.save()

        user_is_updated = False
        user = external_user.user

        if first_name and user.first_name != first_name:
            user.first_name = first_name
            user_is_updated = True

        if last_name and user.last_name != last_name:
            user.last_name = last_name
            user_is_updated = True

        if email and user.email != email:
            user.email = True
            user_is_updated = True

        if is_staff is not None and user.is_staff != is_staff:
            user.is_staff = is_staff
            user_is_updated = True

        if is_superuser is not None and user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            user_is_updated = True

        if is_active is not None and user.is_active != is_active:
            user.is_active = is_active
            user_is_updated = True

        if user_is_updated:
            user.save()

        if groups:
            exist_groups = Group.objects.filter(name__in=groups)
            user.groups.add(*exist_groups)

        return external_user
    except ExternalUser.DoesNotExist:
        external_user = ExternalUser(
            external_username=cleaned_external_username,
            auth_source=cleaned_auth_source
        )
        external_user.set_attributes(attributes)
        external_user.save()

        user = User(
            username='%s@sso' % (external_user.id,),
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_staff=bool(is_staff),
            is_superuser=bool(is_superuser),
            is_active=bool(is_active)
        )
        user.set_unusable_password()
        user.save()

        if groups:
            exist_groups = Group.objects.filter(name__in=groups)
            user.groups.add(*exist_groups)

        external_user.user = user
        external_user.save()

        return external_user
