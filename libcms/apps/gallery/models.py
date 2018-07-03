# -*- encoding: utf-8 -*-
import os
import shutil
try:
    import Image
except ImportError:
    from PIL import Image
import time
from django.conf import settings
from django.db import models


def get_album_dir(slug):
    return settings.MEDIA_ROOT + 'gallery/' + slug + '/'


def image_file_name(instance, filename):
    if instance.id:
        gen_name = unicode(instance.id) + u'.jpg'
    else:
        gen_name = (u"%.9f" % time.time()).replace(u'.', u'') + u'.jpg'

    return (get_album_dir(instance.album.slug) + gen_name)


class Album(models.Model):
    slug = models.SlugField(
        verbose_name=u'Slug',
        max_length=64,
        db_index=True,
        unique=True
    )
    title = models.CharField(max_length=512, verbose_name=u'Название')
    description = models.TextField(verbose_name=u'Описание', blank=True)
    public = models.BooleanField(verbose_name=u'Опубликован', default=False, db_index=True)
    create_date = models.DateTimeField(verbose_name=u"Дата создания", auto_now_add=True, db_index=True)

    #    def save(self):
    #        if getattr(self, 'id', None):
    #            self.slug = Album.objects.get(id=self.id).slug
    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-create_date']
        permissions = (
            ("public_album", "Can public album"),
        )

    def get_dir(self):
        return get_album_dir(self.slug)

    def get_description(self):
        return self.description.replace(u'\n', u'<br/>')


class AlbumImage(models.Model):
    album = models.ForeignKey(Album)
    image = models.FileField(upload_to=image_file_name, verbose_name=u'Файл с изображением', max_length=512)
    comments = models.CharField(max_length=512, blank=True, verbose_name=u'Коментарии к изображению')
    create_date = models.DateTimeField(verbose_name=u"Дата создания", auto_now_add=True, db_index=True)

    def __unicode__(self):
        return self.comments

    def get_thumbinail_dir(self):
        return self.album.get_dir() + 'thumbinails/'

    def get_thumbinail_path(self):
        return self.get_thumbinail_dir() + self.get_image_file_name()

    def delete_thumbinail(self):
        os.remove(self.get_thumbinail_path())

    def get_image_file_name(self):
        return unicode(self.image).split('/')[-1]

    def delete_thumbinail(self):
        get_thumbinail_path = instance.get_thumbinail_path()
        if os.path.isfile(get_thumbinail_path):
            os.remove(get_thumbinail_path)


from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver


@receiver(pre_delete, sender=Album)
def album_pre_delete(instance, **kwargs):
    album_path = instance.get_dir()
    album_images = AlbumImage.objects.filter(album=instance)

    for album_image in album_images:
        album_image.delete()

    if os.path.isdir(album_path):
        shutil.rmtree(instance.get_dir())


@receiver(post_save, sender=AlbumImage)
def image_post_save(instance, **kwargs):
    handle_uploaded_file(instance)


@receiver(pre_delete, sender=AlbumImage)
def image_pre_delete(instance, **kwargs):
    if os.path.isfile(unicode(instance.image)):
        os.remove(unicode(instance.image))

    get_thumbinail_path = instance.get_thumbinail_path()
    if os.path.isfile(get_thumbinail_path):
        os.remove(get_thumbinail_path)


def handle_uploaded_file(instance):
    thumbinail_path = instance.get_thumbinail_path()
    thumbinail_dir = instance.get_thumbinail_dir()
    image_file_path = unicode(instance.image)
    if not os.path.exists(thumbinail_dir):
        os.makedirs(thumbinail_dir)
    final_hight = 768
    try:
        im = Image.open(image_file_path)
        im = im.convert('RGB')
        image_ratio = float(im.size[0]) / im.size[1]
        final_width = int((image_ratio * final_hight))
        im.thumbnail((final_width, final_hight), Image.ANTIALIAS)
        im.save(image_file_path, "JPEG", quality=95)
    except IOError as e:
        return None

    image_width = im.size[0]
    image_hight = im.size[1]
    image_ratio = float(image_width) / image_hight

    box = [0, 0, 0, 0]
    if image_ratio <= 1:
        new_hight = int(image_width / 1.333)
        vert_offset = int((image_hight - new_hight) / 2)
        box[0] = 0
        box[1] = vert_offset
        box[2] = image_width
        box[3] = vert_offset + new_hight
    else:
        new_width = image_hight * 1.333
        if new_width > image_width:
            new_width = image_width
            new_hight = int(new_width / 1.333)
            vert_offset = int((image_hight - new_hight) / 2)
            box[0] = 0
            box[1] = vert_offset
            box[2] = new_width
            box[3] = vert_offset + new_hight
        else:
            gor_offset = int((image_width - new_width) / 2)
            box[0] = gor_offset
            box[1] = 0
            box[2] = int(gor_offset + new_width)
            box[3] = image_hight

    im = im.crop(tuple(box))

    final_hight = 240
    try:
        image_ratio = float(im.size[0]) / im.size[1]
        final_width = int((image_ratio * final_hight))
        im.thumbnail((final_width, final_hight), Image.ANTIALIAS)
        im.save(thumbinail_path, "JPEG", quality=95)
    except IOError as e:
        return None
    return image_file_path
