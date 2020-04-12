# -*- coding: utf-8 -*-
from rfc3986 import is_valid_uri
from urllib.error import HTTPError
from urllib.request import urlretrieve
import requests
import hashlib
import time
import os

from django.db import transaction
from django.utils import timezone
from django.utils.html import smart_urlquote
from junimarc.iso2709.reader import Reader
from junimarc.json.junimarc import record_to_json
from junimarc.record import ControlField

from . import tasks
from . import models
from . import settings


def _get_record_id(jrecord, source, dump):
    cleaned_dump = dump
    if isinstance(cleaned_dump, str):
        cleaned_dump = cleaned_dump.encode('utf-8')
    fields_001 = jrecord.get_fields('001')
    record_id = ''
    hash = hashlib.md5(cleaned_dump).hexdigest()
    for field_001 in fields_001:
        if not isinstance(field_001, ControlField):
            continue
        data = field_001.get_data()
        if data:
            record_id = data
            break

    if record_id:
        return hashlib.md5((record_id + source).encode('utf-8')).hexdigest(), record_id, hash

    return hash, record_id, hash


def _create_records(record_containers):
    for record_container in record_containers:
        models.Record.objects.bulk_create([record_container['record']])
        models.RecordContent.objects.bulk_create([record_container['content']])


def _update_records(record_containers):
    for record_container in record_containers:
        record_container['record'].save()
        record_content = record_container['content']
        models.RecordContent.objects.filter(record_id=record_content.record_id).update(content=record_content.content)


def _reset_records(records):
    ids = set()
    session_id = None
    for record in records:
        ids.add(record.id)
        if not session_id:
            session_id = record.session_id

    if session_id:
        models.Record.objects.filter(id__in=ids).update(session_id=session_id)


def _process_records(record_containers, reset=True):
    processed_record_containers_index = {}

    for record_container in record_containers:
        record = record_container['record']
        processed_record_containers_index[record.id] = record_container

    record_containers_for_create = []
    record_containers_for_update = []
    records_for_reset = []
    record_for_update_ids = set()

    records = models.Record.objects.filter(id__in=list(processed_record_containers_index.keys()))

    for record in records:
        record_container = processed_record_containers_index.get(record.id)
        if record_container is not None:
            record_for_update_ids.add(record.id)
            precessed_record = record_container['record']

            if reset:
                record.session_id = precessed_record.session_id

            need_update = False

            if record.hash != precessed_record.hash or record.deleted != precessed_record.deleted:
                need_update = True

            if need_update:
                record.hash = precessed_record.hash
                record.update_date = precessed_record.update_date
                record.deleted = precessed_record.deleted
                record_containers_for_update.append({
                    'record': record,
                    'content': record_container['content']
                })
            elif reset:
                records_for_reset.append(record)

    for processed_record_id in list(processed_record_containers_index.keys()):
        if processed_record_id not in record_for_update_ids:
            record_containers_for_create.append(processed_record_containers_index[processed_record_id])

    _create_records(record_containers_for_create)
    _update_records(record_containers_for_update)
    _reset_records(records_for_reset)
    return len(record_containers_for_create), len(record_containers_for_update)


def _get_percent(current, total):
    if total == 0:
        return 0
    return round(current * 100 / total)


def _get_file_path(file_uri: str):
    file_path = file_uri
    is_tmp = False
    error = ''
    if not is_valid_uri(file_path):
        error = 'URI not valid ' + file_path
        return None, is_tmp, error

    if file_uri.startswith('http://') or file_uri.startswith('https://'):
        file_path = os.path.join(settings.TMP_DIR, '%f' % (time.time(),))
        try:
            response = requests.head(file_uri)
            response.raise_for_status()
        except requests.HTTPError as e:
            error = str(e)
            return None, is_tmp, error

        try:
            urlretrieve(smart_urlquote(file_uri), file_path)
        except HTTPError as e:
            error = str(e)
            file_path = None
        is_tmp = True
    return file_path, is_tmp, error


def _get_full_text(uri: str):
    cleaned_uri = uri
    uri_hash = hashlib.md5(cleaned_uri.encode('utf-8')).hexdigest()
    content = ''
    print('uri', uri)
    try:
        full_text_cache = models.FullTextCache.objects.get(uri_hash=uri_hash)
        print('cached', uri)
        return full_text_cache.content
    except models.FullTextCache.DoesNotExist:
        pass

    file_path, is_tmp, error = _get_file_path(uri)

    if not file_path:
        models.FullTextCache(
            uri_hash=uri_hash,
            uri=cleaned_uri[0:2048],
            content=content,
            error=bool(error),
            message=error
        ).save()
        return content

    result_file_path = file_path + '.txt'

    command = ' '.join([
        'java',
        '-jar',
        settings.PDFBOX_PATH,
        'ExtractText',
        "%s" % (file_path,),
        "%s" % (result_file_path,),
    ])
    os.system(command)

    if os.path.exists(result_file_path):
        with open(result_file_path, 'r', encoding='utf-8', errors='replace') as text_file:
            content = text_file.read()

    models.FullTextCache(uri_hash=uri_hash, content=content).save()
    print('save', uri_hash)
    if os.path.exists(result_file_path):
        os.unlink(result_file_path)

    if is_tmp:
        os.path.isfile(file_path)
        os.unlink(file_path)

    return content


def _collect_file(harvesting_rule, records_file, now, session_id):
    source = harvesting_rule.source
    batch_size = 20
    processed = 0
    created = 0
    updated = 0
    deleted = 0

    extended_subfield_code = ''
    if records_file.schema == models.SCHEMAS['RUSMARC']:
        extended_subfield_code = '1'
    print(('extended_subfield_code', extended_subfield_code))
    print(('Start collecting source', source, 'file', records_file.file_uri))

    file_path, is_tmp, error = _get_file_path(records_file.file_uri)
    reader = Reader(file_path, extended_subfield_code=extended_subfield_code)
    total_records = 0
    # print('Calculate total records...')
    # total_records = reader.get_total_records()
    # print(('Total records', total_records))

    record_containers = []

    for rec in reader.read():
        errors = rec.get_errors()
        if errors:
            print(errors)
        processed += 1
        record_json = record_to_json(rec, dump=True)
        record_id,  original_id, record_hash = _get_record_id(rec, source.code, record_json)
        record_containers.append({
            'record': models.Record(
                id=record_id,
                original_id=original_id,
                hash=record_hash,
                source=source,
                schema='junimarc',
                session_id=session_id,
                create_date=now,
                update_date=now,
            ),
            'content': models.RecordContent(record_id=record_id, content=record_json)
        })

        if len(record_containers) >= batch_size:
            created_amount, updated_amount = _process_records(record_containers, reset=harvesting_rule.reset)
            created += created_amount
            updated += updated_amount
            record_containers = []

        if processed % 100 == 0:
            print(('processed', processed, _get_percent(processed, total_records), '%'))

    if is_tmp:
        if os.path.isfile(file_path):
            os.remove(file_path)

    if record_containers:
        _process_records(record_containers, reset=harvesting_rule.reset)

    if harvesting_rule.reset:
        deleted = models.Record.objects.filter(
            deleted=False,
            source=source
        ).exclude(
            session_id=session_id
        ).update(
            deleted=True,
            update_date=now
        )

    return {
        'processed': processed,
        'created': created,
        'updated': updated,
        'deleted': deleted,
        'total_records': total_records,
    }


def _collect_harvesting_rule(harvesting_rule):
    source = harvesting_rule.source
    now = timezone.now()
    session_id = int(time.time())

    created = 0
    updated = 0
    deleted = 0
    processed = 0
    total_records = 0
    error = False
    message = ''
    try:
        for source_file in models.SourceRecordsFile.objects.filter(source=source):
            stats = _collect_file(harvesting_rule, source_file, session_id=session_id, now=now)
            created += stats['created']
            updated += stats['updated']
            deleted += stats['deleted']
            processed += stats['processed']
            total_records += stats['total_records']
    except Exception as e:
        error = True
        message = str(e)

    models.HarvestingStatus(
        harvesting_rule=harvesting_rule,
        create_date=now,
        created=created,
        updated=updated,
        deleted=deleted,
        processed=processed,
        total_records=total_records,
        session_id=session_id,
        error=error,
        message=message
    ).save()
    print(('processed', processed, _get_percent(processed, total_records), '%'))
    print(('session id', session_id))
    print(('total records', total_records))
    print(('processed', processed))
    print(('created', created))
    print(('updated', updated))
    print(('for delete', deleted))


# @transaction.atomic()
def collect_harvesting_rule(id):
    now = timezone.now()
    harvesting_rule = models.HarvestingRule.objects.get(id=id)
    if not harvesting_rule.active:
        return
    _collect_harvesting_rule(harvesting_rule)
    harvesting_rule.last_harvested = now
    harvesting_rule.save()
    source = harvesting_rule.source
    source.last_harvesting_date = now
    source.save()


# @transaction.atomic()
def collect_source(id):
    now = timezone.now()
    source = models.Source.objects.get(id=id)
    for harvesting_rule in models.HarvestingRule.objects.filter(active=True, source=source):
        _collect_harvesting_rule(harvesting_rule)
        if harvesting_rule.index_after_harvesting:
            tasks.index_source(source.id)
    source.last_harvesting_date = now
    source.save()


# @transaction.atomic()
def collect():
    now = timezone.now()
    for source in models.Source.objects.filter(active=True):
        print('Collect ', source.code)
        for harvesting_rule in models.HarvestingRule.objects.filter(active=True, source=source):
            _collect_harvesting_rule(harvesting_rule)
        source.last_harvesting_date = now
        source.save()


# @transaction.atomic()
def delete_source_records(id):
    source = models.Source.objects.get(id=id)
    record_contents = models.RecordContent.objects.filter(record__source=source)
    record_contents._raw_delete(record_contents.db)
    records = models.Record.objects.filter(source=source)
    records._raw_delete(records.db)
    source.last_harvesting_date = None
    source.save()


# @transaction.atomic()
def clean_source_records(id):
    source = models.Source.objects.get(id=id)
    record_contents = models.RecordContent.objects.filter(record__source=source, record__deleted=True)
    record_contents._raw_delete(record_contents.db)

    records = models.Record.objects.filter(source=source, deleted=True)
    records._raw_delete(records.db)
