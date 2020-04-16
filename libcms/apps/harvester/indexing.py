from junimarc.json.junimarc import record_from_json
from junimarc.marc_query import MarcQuery
from solr.indexing import IndexDocument
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from . import settings
from . import models
from . import solr_api

from . import harvesting


# dt.datetime.now() + dt.timedelta(seconds=c.CronTab('1,3,4 * * * *').previous())


def _record_to_index_document(source, transformation_code, record, record_content):
    content = record_content.content
    jrecord = record_from_json(content)
    rq = MarcQuery(jrecord)
    index_document = IndexDocument(record.id)
    urls = {}
    get_full_text = harvesting._get_full_text
    context = {
        'skip': False,
        'index_document': index_document,
    }
    exec(transformation_code, locals(), locals())
    return context


def _get_transformation(source):
    transformation_rule = source.transformation_rule
    if not transformation_rule:
        raise ValueError('Source %s have not transformation_rule rule' % (source.code,))

    transformation_code = compile(transformation_rule.content.strip(), 'Indexing rule', 'exec')

    source_tree = []
    source_parts = source.code.split('.')

    for i, source_part in enumerate(source_parts):
        if i == 0:
            source_tree.append(('system_source', '.'.join(source_parts[0:1])))
        else:
            source_tree.append(('system_source_lvl_' + str(i), '.'.join(source_parts[0:i + 1])))

    return {
        'transformation_code': transformation_code,
        'source_tree': source_tree,
    }


def _index_doc_post_processing(index_document, record_content, transformation):
    source_tree = transformation['source_tree']
    for source_tree_item in source_tree:
        index_document.add_field(source_tree_item[0], source_tree_item[1]).as_string()
    index_document.add_field('system_create_date', record_content.record.create_date).as_datetime().sortable()
    return index_document


def _clean_source_index(source):
    solr_client = solr_api.get_solr_client()
    batch_size = 50
    id_list = []
    deleted = 0
    for record in models.Record.objects.filter(source=source, deleted=True).iterator():
        id_list.append(record.id)
        deleted += 1
        if len(id_list) >= batch_size:
            solr_client.delete_by_id_list(settings.SOLR_COLLECTION, id_list)

    if id_list:
        solr_client.delete_by_id_list(settings.SOLR_COLLECTION, id_list)
    solr_client.commit(settings.SOLR_COLLECTION)
    return deleted


def _get_last_indexing_date(source):
    last_index_date = None
    indexing_statuses = models.IndexingStatus.objects.filter(source=source).order_by('-create_date')[:1]
    if indexing_statuses:
        last_index_date = indexing_statuses[0].create_date
    return last_index_date


# @transaction.atomic()
def index_source(id):
    print('index source', id)
    now = timezone.now()
    source = models.Source.objects.get(id=id)
    print('Deleting records with deleted flag from index')
    deleted = 0
    #deleted = _clean_source_index(source)
    #print('deleted from index', deleted)
    batch_size = 50
    solr_client = solr_api.get_solr_client()
    transformation_rule = source.transformation_rule

    if transformation_rule is None:
        return

    transformation = _get_transformation(source)
    transformation_code = transformation['transformation_code']

    index_documents = []
    updated_docs_count = 0
    try:
        q = Q(source=source)
        last_indexing_date = source.last_indexing_date
        if last_indexing_date:
            q &= Q(update_date__gte=last_indexing_date)
        i = 0
        # for record_content in models.RecordContent.objects.filter(q).exclude(
        #         record__deleted=True).iterator():
        print('Last index date', source.last_indexing_date)
        print('Records for indexing:', models.Record.objects.filter(q).exclude(deleted=True).count())
        for record in models.Record.objects.filter(q).exclude(deleted=True).iterator():
            print(i)
            if i % 100 == 0:
                print(i)
            i += 1
            try:
                record_content = models.RecordContent.objects.get(record=record)
            except models.RecordContent.DoesNotExist:
                continue

            # if record_content.record.deleted:
            #     continue
            context = _record_to_index_document(
                source,
                transformation_code,
                record,
                record_content
            )
            index_document = context['index_document']

            if context['skip']:
                continue

            index_document = _index_doc_post_processing(index_document, record_content, transformation)
            index_documents.append(index_document.to_dict())
            updated_docs_count += 1

            if len(index_documents) > batch_size:
                solr_client.update(
                    collection=settings.SOLR_COLLECTION,
                    docs=index_documents,
                )
                index_documents = []

        if index_documents:
            solr_client.update(
                collection=settings.SOLR_COLLECTION,
                docs=index_documents,
            )
        print('commit solr')
        solr_client.commit(settings.SOLR_COLLECTION)
        print('commit solr success')
        models.IndexingStatus(
            source=source,
            indexed=updated_docs_count,
            deleted=deleted,
            create_date=now,
        ).save()
        source.last_indexing_date = now
        source.save()
    except Exception as e:
        models.IndexingStatus(
            source=source,
            indexed=updated_docs_count,
            deleted=deleted,
            create_date=now,
            error=True,
            message=str(e)
        ).save()
        # raise e


# @transaction.atomic()
def reset_source_index(id):
    source = models.Source.objects.get(id=id)
    transformation = _get_transformation(source)
    source_index_field, source_index_value = transformation['source_tree'][0]
    solr_client = solr_api.get_solr_client()
    solr_client.delete_by_query(settings.SOLR_COLLECTION, ':'.join([source_index_field + '_s', source_index_value]))
    solr_client.commit(settings.SOLR_COLLECTION)
    source.last_indexing_date = None
    source.save()


# @transaction.atomic()
def clean_source_index(id):
    source = models.Source.objects.get(id=id)
    _clean_source_index(source)


# @transaction.atomic()
def get_index_document(record):
    source = record.source
    if not source.transformation_rule:
        return {'error': 'no transformation_rule rule'}

    transformation = _get_transformation(source)
    transformation_code = transformation['transformation_code']

    try:
        record_content = models.RecordContent.objects.get(record=record)
    except models.RecordContent.DoesNotExist:
        return {'error': 'record not found'}

    context = _record_to_index_document(
        source,
        transformation_code,
        record,
        record_content
    )

    index_document = context['index_document']

    index_document = _index_doc_post_processing(index_document, record_content, transformation)

    return index_document


def index():
    for source in models.Source.objects.filter(active=True):
        index_source(source.id)
