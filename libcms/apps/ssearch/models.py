# coding=utf-8
import zipfile
import json
import binascii
from collections import Counter
from datetime import datetime, timedelta
import hashlib
from io import BytesIO
from django.db import models
from django.contrib.auth.models import User
from harvester.models import RecordContent
from junimarc.json.junimarc import record_from_json

# from common.pagination import get_page2

# RECORDS_DB_CONNECTION = 'harvester'


class ViewDocLog(models.Model):
    record_id = models.CharField(max_length=32, db_index=True)
    collection_id = models.CharField(max_length=64, db_index=True, null=True)
    user = models.ForeignKey(User, null=True, db_index=True, on_delete=models.CASCADE)
    view_date_time = models.DateTimeField(auto_now_add=True, db_index=True)

    @staticmethod
    def get_view_count(collection_id):
        return ViewDocLog.objects.filter(collection_id=collection_id.lower().strip()).count()


class ZippedTextField(models.TextField):
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.postgresql_psycopg2' \
                or connection.settings_dict['ENGINE'] == 'django.db.backends.postgresql':
            return 'bytea'
        else:
            return 'BLOB'

    def to_python(self, value):
        fp = BytesIO(value)
        zfp = zipfile.ZipFile(fp, "r")
        value = zfp.open("record.json").read()
        value = value.decode('utf-8')

        return value

    def get_db_prep_save(self, value, connection):
        if isinstance(value, str):
            zvalue = BytesIO()
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
#     def __str__(self):
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
#     def __str__(self):
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

# class RecordContent(models.Model):
#     record_id = models.CharField(max_length=32, db_column='original_id_hash')
#     source_id = models.CharField(max_length=32)
#     content = models.BinaryField()
#     create_date_time = models.DateTimeField()
#
#     class Meta:
#         db_table = 'records'
#
#     def unpack_content(self):
#         fp = BytesIO(self.content)
#         zfp = zipfile.ZipFile(fp, "r")
#         value = zfp.open("record.json").read()
#         return value.decode('utf-8')


def get_records(record_ids):
    """
    :param record_ids: record_id идентификаторы записей
    :return: списко записей
    """
    records_objects = list(RecordContent.objects.filter(record_id__in=record_ids))
    records = []
    for record in records_objects:
        rdict = json.loads(record.content)
        jrecord = record_from_json(rdict)
        records.append({
            'id': record.record_id,
            'dict': rdict,
            'tree': record_to_ruslan_xml(jrecord),
            'jrecord': jrecord
        })
        # record.tree = record_to_ruslan_xml(json.loads(record.content))
    records_dict = {}
    for record in records:
        records_dict[record['id']] = record
    nrecords = []
    for record_id in record_ids:
        record = records_dict.get(record_id, None)
        if record:
            nrecords.append(record)
    return nrecords


# def get_records(ids, db_config='records'):
#     cleaned_ids = []
#     for id in ids:
#         cleaned_ids.append(id.strip())
#     records = list(RecordContent.objects.using(RECORDS_DB_CONNECTION).filter(record_id__in=cleaned_ids))
#     records_dict = {}
#     for record in records:
#         records_dict[record.record_id] = record
#     result_records = []
#     for id in cleaned_ids:
#         record = records_dict.get(id, None)
#         if not record: continue
#         result_records.append(record)
#     return result_records

from junimarc import ruslan_xml

def record_to_ruslan_xml(map_record, syntax='1.2.840.10003.5.28', namespace=False):
    return ruslan_xml.record_to_xml(map_record, syntax, namespace)
    """
    default syntax rusmarc
    """
    string_leader = map_record['l']

    root = etree.Element('record')
    root.set('syntax', syntax)
    leader = etree.SubElement(root, 'leader')

    length = etree.SubElement(leader, 'length')
    length.text = string_leader[0:5]

    status = etree.SubElement(leader, 'status')
    status.text = string_leader[5]

    type = etree.SubElement(leader, 'status')
    type.text = string_leader[6]

    leader07 = etree.SubElement(leader, 'leader07')
    leader07.text = string_leader[7]

    leader08 = etree.SubElement(leader, 'leader08')
    leader08.text = string_leader[8]

    leader09 = etree.SubElement(leader, 'leader09')
    leader09.text = string_leader[9]

    indicator_count = etree.SubElement(leader, 'indicatorCount')
    indicator_count.text = string_leader[10]

    indicator_length = etree.SubElement(leader, 'identifierLength')
    indicator_length.text = string_leader[11]

    data_base_address = etree.SubElement(leader, 'dataBaseAddress')
    data_base_address.text = string_leader[12:17]

    leader17 = etree.SubElement(leader, 'leader17')
    leader17.text = string_leader[17]

    leader18 = etree.SubElement(leader, 'leader18')
    leader18.text = string_leader[18]

    leader19 = etree.SubElement(leader, 'leader19')
    leader19.text = string_leader[19]

    entry_map = etree.SubElement(leader, 'entryMap')
    entry_map.text = string_leader[20:23]

    if 'cf' in map_record:
        for cfield in map_record['cf']:
            control_field = etree.SubElement(root, 'field')
            control_field.set('id', cfield['id'])
            control_field.text = cfield['d']

    if 'df' in map_record:
        for field in map_record['df']:
            data_field = etree.SubElement(root, 'field')
            data_field.set('id', field['id'])

            ind1 = etree.SubElement(data_field, 'indicator')
            ind1.set('id', '1')
            ind1.text = field['i1']

            ind2 = etree.SubElement(data_field, 'indicator')
            ind2.set('id', '2')
            ind2.text = field['i2']

            for subfield in field['sf']:
                if 'inner' in subfield:
                    linked_subfield = etree.SubElement(data_field, 'subfield')
                    linked_subfield.set('id', subfield['id'])

                    if 'cf' in subfield['inner']:
                        for cfield in subfield['inner']['cf']:
                            linked_control_field = etree.SubElement(linked_subfield, 'field')
                            linked_control_field.set('id', cfield['id'])
                            linked_control_field.text = cfield['d']
                    else:
                        for lfield in subfield['inner']['df']:
                            linked_data_field = etree.SubElement(linked_subfield, 'field')
                            linked_data_field.set('id', lfield['id'])

                            linked_ind1 = etree.SubElement(linked_data_field, 'indicator')
                            linked_ind1.set('id', '1')
                            linked_ind1.text = lfield['i1']

                            linked_ind2 = etree.SubElement(linked_data_field, 'indicator')
                            linked_ind2.set('id', '2')
                            linked_ind2.text = lfield['i2']

                            for lsubfield in lfield['sf']:
                                linkeddata_subfield = etree.SubElement(linked_data_field, 'subfield')
                                linkeddata_subfield.set('id', lsubfield['id'])
                                linkeddata_subfield.text = lsubfield['d']

                else:
                    data_subfield = etree.SubElement(data_field, 'subfield')
                    data_subfield.set('id', subfield['id'])
                    data_subfield.text = subfield['d']
    return root


from collections import defaultdict


def fill_records(detail_log_dict_list):
    record_ids_index = defaultdict(list)
    for detail_log_dict in detail_log_dict_list:
        record_ids_index[detail_log_dict['detail_log'].record_id].append(detail_log_dict)

    for record_content in get_records(list(record_ids_index.keys())):
        for detail_log_dict in record_ids_index.get(record_content.record_id, []):
            detail_log_dict['record_content'] = record_content


REPEAT_LOG_TIMEOUT_MINUTES = 10
LOG_TIMEOUT_MINUTES = 60
LOG_TIMEOUT_LIMIT_RECORDS = 1400


class SearchLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    params = models.TextField(verbose_name='Параметры поиска', max_length=2048, blank=True)
    total = models.BigIntegerField(verbose_name='Найдено записей', default=0)
    in_results = models.BooleanField(verbose_name='Уточнение результатов', default=False)
    session_id = models.CharField(verbose_name='Идентификатор сесии', max_length=64, db_index=True)
    date_time = models.DateTimeField(auto_now_add=True, db_index=True)
    params_crc32 = models.IntegerField(db_index=True, verbose_name='CRC32 json-строки параметров запроса', default=0)

    def get_params(self):
        return json.loads(self.params)

DETAIL_ACTIONS_REFERENCE = {
    'VIEW_DETAIL': {
        'code': 0,
        'title': 'просмотр записи',
    },
    'LOAD_FULL_TEXT': {
        'code': 1,
        'title': 'загрузка полного текста',
    },
    'VIEW_FULL_TEXT': {
        'code': 2,
        'title': 'просмотр полного текста',
    },
    'LOAD_VIDEO': {
        'code': 3,
        'title': 'загрузка видео',
    },
    'VIEW_VIDEO': {
        'code': 4,
        'title': 'просмотр видео',
    },
    'LOAD_AUDIO': {
        'code': 5,
        'title': 'загрузка аудио',
    },
    'VIEW_AUDIO': {
        'code': 6,
        'title': 'прослушивание аудио',
    },
    'LOAD_CONTENT_LIST': {
        'code': 7,
        'title': 'загрузка содержания',
    },
    'LOAD_DOCUMENT': {
        'code': 8,
        'title': 'загрузка электронного документа',
    },
    'SOCIAL_SHARE': {
        'code': 9,
        'title': 'отправка в соц. сети',
    },
}

DETAIL_ACTIONS = {}

DETAIL_ACTIONS_CHOICES = []
DETAIL_ACTIONS_TITLES = {}


def init_detail_actions():
    for action_key, value in list(DETAIL_ACTIONS_REFERENCE.items()):
        DETAIL_ACTIONS[action_key] = value.get('code', 0)

    for action_key, value in list(DETAIL_ACTIONS_REFERENCE.items()):
        code = value.get('code', None)
        if code is None:
            continue
        title = value.get('title', code)
        DETAIL_ACTIONS_TITLES[code] = value.get('title', code)
        DETAIL_ACTIONS_CHOICES.append([code, title])


init_detail_actions()


class DetailLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, blank=True)
    record_id = models.CharField(max_length=64, db_index=True)
    action = models.IntegerField(verbose_name='Действие', default=DETAIL_ACTIONS['VIEW_DETAIL'], db_index=True)
    session_id = models.CharField(verbose_name='Идентификатор сесии', max_length=64, db_index=True)
    attrs = models.TextField(
        verbose_name='JSON атрибуты',
        blank=True,
        max_length=10 * 1024
    )
    date_time = models.DateTimeField(auto_now_add=True, db_index=True)


    def set_attrs(self, attrs):
        self.attrs = json.dumps(attrs, ensure_ascii=False)

    def get_attrs(self):
        if not self.attrs:
            return {}
        return json.loads(self.attrs)

    def __str__(self):
        return '{record_id} {action}'.format(record_id=self.record_id, action=self.action)


def log_search_request(params, user=None, total=0, in_results=False, session_id=''):
    # if not params:
    #     return
    # is_empty = True
    #
    # for param in params:
    #     value = param.get('value', '').strip()
    #     if value and value != '*':
    #         is_empty = False
    #
    # if is_empty:
    #     return

    json_params = json.dumps(params, ensure_ascii=False).lower()

    params_crc32 = binascii.crc32(json_params.encode('utf-8')) / 10

    now = datetime.now()

    q = models.Q(
        params_crc32=params_crc32,
    )

    id_q = models.Q()

    if session_id:
        id_q |= models.Q(session_id=session_id)

    if user is not None:
        id_q |= models.Q(user=user)

    if id_q:
        q &= models.Q(date_time__gte=now - timedelta(minutes=REPEAT_LOG_TIMEOUT_MINUTES))
        q &= id_q

    if user or session_id:
        if SearchLog.objects.filter(q).exists():
            return

    search_log = SearchLog(
        user=user,
        params=json_params,
        total=int(total),
        in_results=in_results,
        session_id=session_id,
        params_crc32=params_crc32
    )

    SearchLog.objects.bulk_create([search_log])


def log_detail(record_id, user=None, action=0, session_id=''):
    if not record_id:
        return

    now = datetime.now()

    q = models.Q(
        record_id=record_id,
        action=action
    )

    id_q = models.Q()

    if session_id:
        id_q |= models.Q(session_id=session_id)

    if user is not None:
        id_q |= models.Q(user=user)

    if id_q:
        q &= models.Q(date_time__gte=now - timedelta(minutes=REPEAT_LOG_TIMEOUT_MINUTES))
        q &= id_q

    if user or session_id:
        if DetailLog.objects.filter(q).exists():
            return

    # if DetailLog.objects.filter(
    #         date_time__gte=now - timedelta(minutes=LOG_TIMEOUT_MINUTES),
    # ).count() > LOG_TIMEOUT_LIMIT_RECORDS:
    #     return

    detail_log = DetailLog(
        record_id=record_id,
        user=user,
        action=action,
        session_id=session_id
    )

    DetailLog.objects.bulk_create([detail_log])


def get_statistics_for_detail(record_id):
    detail_log_records = DetailLog.objects.filter(record_id=record_id)
    report = {}

    for detail_log_record in detail_log_records.iterator():
        action_count = report.get(detail_log_record.action, 0)
        report[detail_log_record.action] = action_count + 1

    report_lines = []
    for action, count in list(report.items()):
        report_lines.append({
            'id': action,
            'value': count,
            'title': DETAIL_ACTIONS_TITLES.get(action, action)
        })
    report_lines.sort(key=lambda x: x['value'])
    return report_lines


def _get_begin_day_datetime(date):
    return datetime(
        year=date.year,
        month=date.month,
        day=date.day,
        hour=0,
        minute=0,
        second=0
    )


def _get_end_day_datetime(date):
    return datetime(
        year=date.year,
        month=date.month,
        day=date.day,
        hour=23,
        minute=59,
        second=59
    )


def _filter_record_ids(record_ids):
    # source = None
    # try:
    #     source = Source.objects.get(code='sic')
    # except Source.DoesNotExist:
    #     pass
    qs = RecordContent.objects.filter(id__in=record_ids).values('id')
    # if source is not None:
    #     qs = qs.exclude(source=source)
    records = qs
    return [record['id'] for record in records]


def get_rating_records(start_date, end_date):
    q = models.Q()
    now = datetime.now()

    if not start_date:
        start_date = now.date()
    q &= models.Q(date_time__gte=_get_begin_day_datetime(start_date))

    if not end_date:
        end_date = now.date()
    q &= models.Q(date_time__lte=_get_end_day_datetime(end_date))

    counter = Counter()
    per_page = 1000
    page_number = 1
    qs = DetailLog.objects.filter(q)
    page = get_page2(page_number, qs, per_page)

    while True:
        records_ids = []
        for item in page.object_list:
            records_ids.append(item.record_id)
        filtered_ids = _filter_record_ids(set(records_ids))
        for record_id in records_ids:
            if record_id in filtered_ids:
                counter[record_id] += 1

        if not page.has_next():
            break
        page_number += 1
        page = get_page2(page_number, qs, per_page)

    most_commons = counter.most_common()[:20]
    record_ids = [x[0] for x in most_commons]
    records = get_records(record_ids)
    records_index = {}

    for record in records:
        records_index[record.record_id] = record

    records_list = []
    for most_common in most_commons:
        records_list.append({
            'record': records_index[most_common[0]],
            'rating': most_common[1]
        })
    # for record in records:
    #     mq = marc_query.MarcQuery(json_schema.record_from_json(record.content))
    #     print mq.get_field('200').get_subfield('a').get_data()
    return {
        'start_date': start_date,
        'end_date': end_date,
        'records_list': records_list
    }
