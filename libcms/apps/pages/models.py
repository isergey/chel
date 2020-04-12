# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import get_language
from mptt.models import MPTTModel, TreeForeignKey


class Page(MPTTModel):
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская страница',
        on_delete=models.CASCADE
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=255,
        db_index=True,
        help_text='Внимание! Последующее редактирование поля slug невозможно!'
    )
    url_path = models.CharField(
        max_length=1500,
        db_index=True,
    )

    public = models.BooleanField(
        verbose_name='Опубликована?',
        default=False, db_index=True,
        help_text='Публиковать страницу могут только пользователи с правами публикации страниц'
    )

    show_children = models.BooleanField(
        verbose_name='Показывать меню подстраниц',
        default=False,
    )

    show_neighbors = models.BooleanField(
        verbose_name='Показывать меню соедних страниц',
        default=False,
    )


    create_date = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-create_date']
        permissions = (
            # ("view_page", "Can view page"),
            ("public_page", "Can public page"),
        )

    def __str__(self):
        return self.slug

    def get_cur_lang_content(self):
        cur_language = get_language()
        try:
            content = Content.objects.get(page=self, lang=cur_language[:2])
        except Content.DoesNotExist:
            content = None
        return content

    def get_ancestors_titles(self):
        """
        return translated ancestors
        """
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        ancestors.reverse()
        # ancestors = list(self.get_ancestors())
        lang = get_language()[:2]
        ad = {}
        for ancestor in ancestors:
            ad[ancestor.id] = ancestor
        contents = Content.objects.filter(page__in=ancestors, lang=lang).values('page_id', 'title')
        for content in contents:
            ad[content['page_id']].title = content['title']
        return ancestors

    def save(self, *args, **kwargs):
        old = None
        if self.id:
            old = Page.objects.get(id=self.id)

        if old and self.slug != old.slug:
            self.slug = old.slug
        else:
            url_pathes = []
            if self.parent:
                for node in self.parent.get_ancestors():
                    url_pathes.append(node.slug)
                url_pathes.append(self.parent.slug)
                url_pathes.append(self.slug)
            else:
                url_pathes.append(self.slug)

            self.url_path = '/'.join(url_pathes)

        return super(Page, self).save(*args, **kwargs)

    def up(self):
        previous = self.get_previous_sibling()
        if previous:
            self.move_to(previous, position='left')

    def down(self):
        next = self.get_next_sibling()
        if next:
            self.move_to(next, position='right')


class Content(models.Model):
    page = models.ForeignKey(Page, verbose_name='Родительская страница', on_delete=models.CASCADE)
    lang = models.CharField(verbose_name="Язык", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name='Заглавие', max_length=512)
    meta = models.CharField(verbose_name="Meta keywords", max_length=512, blank=True,
                            help_text='Укажите ключевые слова для страницы')
    meta_description = models.CharField(verbose_name="Meta description", max_length=512, blank=True,
                            help_text='Краткое описаие страницы')
    content = models.TextField(verbose_name='Контент')

    class Meta:
        unique_together = (('page', 'lang'),)

    def __str__(self):
        return self.title

    def return_in_lang(self):
        pass


class ViewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)
