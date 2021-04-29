from django.db import models


class Group(models.Model):
    code = models.SlugField(
        verbose_name='Код группы',
        primary_key=True
    )

    title = models.CharField(
        verbose_name='Название',
        max_length=512
    )

    hidden = models.BooleanField(
        verbose_name='Скрыта',
        default=False
    )

    is_active = models.BooleanField(
        verbose_name='Активна',
        default=True
    )

    order = models.PositiveIntegerField(
        verbose_name='Порядок вывода',
        default=0,
        db_index=True
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['order']


class Subject(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    code = models.SlugField(
        verbose_name='Код',
        primary_key=True
    )

    title = models.CharField(
        verbose_name='Название',
        max_length=512
    )

    hidden = models.BooleanField(
        verbose_name='Скрыта',
        default=False
    )

    is_active = models.BooleanField(
        verbose_name='Активна',
        default=True
    )

    order = models.PositiveIntegerField(
        verbose_name='Порядок вывода',
        default=0,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['order']


class Subscriber(models.Model):
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE
    )