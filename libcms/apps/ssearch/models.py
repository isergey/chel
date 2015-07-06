import zipfile
from cStringIO import StringIO
from django.db import models
from django.contrib.auth.models import User


class ViewDocLog(models.Model):
    record_id = models.CharField(max_length=32, db_index=True)
    collection_id = models.CharField(max_length=64, db_index=True, null=True)
    user = models.ForeignKey(User, null=True, db_index=True)
    view_date_time = models.DateTimeField(auto_now_add=True, db_index=True)

    @staticmethod
    def get_view_count(collection_id):
        return ViewDocLog.objects.filter(collection_id=collection_id.lower().strip()).count()


class ZippedTextField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.postgresql_psycopg2' or connection.settings_dict[
            'ENGINE'] == 'django.db.backends.postgresql':
            return 'bytea'
        else:
            return 'BLOB'

    def to_python(self, value):
        fp = StringIO(value)
        zfp = zipfile.ZipFile(fp, "r")
        value = zfp.open("record.json").read()
        value = value.decode('utf-8')

        return value

    def get_db_prep_save(self, value, connection):
        if isinstance(value, unicode):
            zvalue = StringIO()
            myzip = zipfile.ZipFile(zvalue, 'w')
            myzip.writestr('record', value.encode('UTF-8'), 8)
            myzip.close()
            value = zvalue.getvalue()
        if value is None:
            return None
        else:
            return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value


#
# class Record(models.Model):
#     source_id = models.IntegerField(null=True, blank=True)
#     gen_id = models.CharField(max_length=32, unique=True)
#     record_id = models.CharField(max_length=32, db_index=True)
#     scheme = models.CharField(max_length=16, default='rusmarc', verbose_name=u"Scheme")
#     content = ZippedTextField(verbose_name=u'Xml content')
#     add_date = models.DateTimeField(auto_now_add=True, db_index=True)
#     update_date = models.DateTimeField(auto_now_add=True, db_index=True)
#     deleted= models.BooleanField()
#     hash = models.TextField(max_length=24)
#     def __unicode__(self):
#         return self.record_id
#     class Meta:
#         db_table = 'spstu'
#
# class AuthRecord(models.Model):
#     source_id = models.IntegerField(null=True, blank=True)
#     gen_id = models.CharField(max_length=32, unique=True)
#     record_id = models.CharField(max_length=32, db_index=True)
#     scheme = models.CharField(max_length=16, default='rusmarc', verbose_name=u"Scheme")
#     content = ZippedTextField(verbose_name=u'Xml content')
#     add_date = models.DateTimeField(auto_now_add=True, db_index=True)
#     update_date = models.DateTimeField(auto_now_add=True, db_index=True)
#     deleted= models.BooleanField()
#     hash = models.TextField(max_length=24)
#     def __unicode__(self):
#         return self.record_id
#     class Meta:
#         db_table = 'authorities'
#
#
#
# class IndexStatus(models.Model):
#     catalog = models.CharField(max_length=32, unique=True)
#     last_index_date = models.DateTimeField()
#     indexed = models.IntegerField(default=0)
#     deleted = models.IntegerField(default=0)
#
#
#
# from __future__ import unicode_literals
#
# from django.db import models
#
# class Collection(models.Model):
#     id = models.IntegerField(primary_key=True)
#     code = models.CharField(max_length=32L)
#     provider_code = models.ForeignKey('Provider', db_column='provider_code')
#     name = models.CharField(max_length=256L)
#     description = models.CharField(max_length=1024L, blank=True)
#     create_date = models.DateTimeField()
#     class Meta:
#         db_table = 'collection'
#
# class Provider(models.Model):
#     id = models.IntegerField(primary_key=True)
#     code = models.CharField(max_length=32L)
#     name = models.CharField(max_length=256L)
#     description = models.CharField(max_length=1024L, blank=True)
#     create_date = models.DateTimeField()
#     class Meta:
#         db_table = 'provider'
#
# class Record(models.Model):
#     id = models.IntegerField(primary_key=True)
#     original_id_md5 = models.CharField(max_length=32L)
#     provider_code = models.CharField(max_length=32L)
#     collection_code = models.CharField(max_length=32L)
#     scheme = models.CharField(max_length=64L)
#     deleted = models.IntegerField()
#     hash = models.CharField(max_length=32L)
#     create_date = models.DateTimeField()
#     update_date = models.DateTimeField()
#     refresh_id = models.BigIntegerField()
#     class Meta:
#         db_table = 'record'

class RecordContent(models.Model):
    record_id = models.CharField(max_length=32L, db_column='original_id_hash')
    source_id = models.CharField(max_length=32L)
    content = ZippedTextField()
    create_date_time = models.DateTimeField()

    class Meta:
        db_table = 'records'
