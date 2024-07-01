# -*- coding: utf-8 -*-
import json
from junimarc.json.junimarc import record_from_json
from django.core.paginator import Paginator
from django.db.transaction import atomic
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
# from journal.models import log_action
from . import forms
from . import models
from . import harvesting
from . import indexing as indexing_utils
from . import tasks

@login_required
@atomic
def index(request):
    sources = models.Source.objects.all()
    return render(request, 'harvester/index.html', {
        'sources': sources,
    })


@login_required
@atomic
def sources(request):
    sources = models.Source.objects.all()
    return render(request, 'harvester/sources.html', {
        'sources': sources,
    })


@login_required
@atomic
def source(request, id):
    source = get_object_or_404(models.Source, id=id)
    source_records_files = models.SourceRecordsFile.objects.filter(source=source)
    harvesting_rules = models.HarvestingRule.objects.filter(source=source)
    indexing_rules = models.IndexingRule.objects.filter(source=source)

    is_exist_active_harvesting_rules = models.HarvestingRule.objects.filter(active=True).exists()
    is_exist_active_indexing_rules = models.IndexingRule.objects.filter(active=True).exists()

    return render(request, 'harvester/source.html', {
        'source': source,
        'source_records_files': source_records_files,
        'is_exist_active_harvesting_rules': is_exist_active_harvesting_rules,
        'is_exist_active_indexing_rules': is_exist_active_indexing_rules,
        'harvesting_rules': harvesting_rules,
        'indexing_rules': indexing_rules,
    })


@login_required
@atomic
def add_source(request):
    if request.method == 'POST':
        form = forms.SourceForm(request.POST)
        if form.is_valid():
            source = form.save(commit=False)
            source.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='create',
            #     user=request.user,
            #     content_type=models.Source,
            #     content_id=source.id,
            # )
            return redirect('harvester:source', id=source.id)
    else:
        form = forms.SourceForm()
    return render(request, 'harvester/source_form.html', {
        'form': form,
    })


@login_required
@atomic
def change_source(request, id):
    source = get_object_or_404(models.Source, id=id)
    if request.method == 'POST':
        form = forms.SourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='update',
            #     user=request.user,
            #     content_type=models.Source,
            #     content_id=source.id,
            # )
            return redirect('harvester:source', id=id)
    else:
        form = forms.SourceForm(instance=source)
    return render(request, 'harvester/source_form.html', {
        'form': form,
        'source': source
    })


@login_required
@atomic
def delete_source(request, id):
    source = get_object_or_404(models.Source, id=id)
    indexing_utils.reset_source_index(source.id)
    harvesting.delete_source_records(source.id)
    # log_action(
    #     request,
    #     app='harvester',
    #     action='delete',
    #     user=request.user,
    #     content_type=models.Source,
    #     content_id=source.id,
    # )
    source.delete()
    return redirect('harvester:index')


@login_required
@atomic
def source_file(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    source_records_file = get_object_or_404(models.SourceRecordsFile, source=source, id=id)
    return render(request, 'harvester/source_file.html', {
        'source': source,
        'source_records_file': source_records_file,
    })


@login_required
@atomic
def add_source_file(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    if request.method == 'POST':
        form = forms.SourceFileForm(request.POST)
        if form.is_valid():
            source_file = form.save(commit=False)
            source_file.source = source
            source_file.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='create',
            #     user=request.user,
            #     content_type=models.SourceRecordsFile,
            #     content_id=source_file.id,
            # )
            return redirect('harvester:source', id=source.id)
    else:
        form = forms.SourceFileForm()
    return render(request, 'harvester/source_file_form.html', {
        'source': source,
        'form': form,
    })


@login_required
@atomic
def change_source_file(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    source_file = get_object_or_404(models.SourceRecordsFile, source=source, id=id)
    if request.method == 'POST':
        form = forms.SourceFileForm(request.POST, instance=source_file)
        if form.is_valid():
            source_file = form.save(commit=False)
            source_file.source = source
            source_file.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='update',
            #     user=request.user,
            #     content_type=models.SourceRecordsFile,
            #     content_id=source_file.id,
            # )
            return redirect('harvester:source_file', source_id=source.id, id=id)
    else:
        form = forms.SourceFileForm(instance=source_file)
    return render(request, 'harvester/source_file_form.html', {
        'source': source,
        'form': form,
        'source_file': source_file,
    })


@login_required
@atomic
def delete_source_file(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    source_file = get_object_or_404(models.SourceRecordsFile, source=source, id=id)

    # log_action(
    #     request,
    #     app='harvester',
    #     action='delete',
    #     user=request.user,
    #     content_type=models.SourceRecordsFile,
    #     content_id=source_file.id,
    # )
    source_file.delete()
    return redirect('harvester:source', id=source.id)


@login_required
@atomic
def add_harvesting_rule(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    if request.method == 'POST':
        form = forms.HarvestingRuleForm(request.POST)
        if form.is_valid():
            harvesting_rule = form.save(commit=False)
            harvesting_rule.source = source
            harvesting_rule.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='create',
            #     user=request.user,
            #     content_type=models.HarvestingRule,
            #     content_id=harvesting_rule.id,
            # )
            return redirect('harvester:source', id=source.id)
    else:
        form = forms.HarvestingRuleForm()
    return render(request, 'harvester/harvesting_rule_form.html', {
        'form': form,
        'source': source,
    })


@login_required
@atomic
def change_harvesting_rule(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    harvesting_rule = get_object_or_404(models.HarvestingRule, id=id)
    if request.method == 'POST':
        form = forms.HarvestingRuleForm(request.POST, instance=harvesting_rule)
        if form.is_valid():
            harvesting_rule = form.save(commit=False)
            harvesting_rule.source = source
            harvesting_rule.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='update',
            #     user=request.user,
            #     content_type=models.HarvestingRule,
            #     content_id=harvesting_rule.id,
            # )
            return redirect('harvester:source', id=source.id)
    else:
        form = forms.HarvestingRuleForm(instance=harvesting_rule)
    return render(request, 'harvester/harvesting_rule_form.html', {
        'form': form,
        'source': source,
        'harvesting_rule': harvesting_rule,
    })


@login_required
@atomic
def delete_harvesting_rule(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    harvesting_rule = get_object_or_404(models.HarvestingRule, id=id)

    # log_action(
    #     request,
    #     app='harvester',
    #     action='delete',
    #     user=request.user,
    #     content_type=models.HarvestingRule,
    #     content_id=harvesting_rule.id,
    # )
    harvesting_rule.delete()
    return redirect('harvester:source', id=source.id)


@login_required
@atomic
def run_harvesting_rule(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    harvesting_rule = get_object_or_404(models.HarvestingRule, id=id)
    harvesting.collect_harvesting_rule(harvesting_rule.id)
    return redirect('harvester:source', id=source.id)


@login_required
@atomic
def harvesting_journal(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    harvesting_status_list = models.HarvestingStatus.objects.filter(harvesting_rule__source_id=source_id).order_by(
        '-create_date')
    paginator = Paginator(harvesting_status_list, 25)  # Show 25 contacts per page

    page = request.GET.get('page')
    harvesting_statuses = paginator.get_page(page)
    return render(request, 'harvester/harvesting_journal.html', {
        'harvesting_statuses': harvesting_statuses,
        'source': source,
    })


@login_required
@atomic
def clean_harvesting_journal(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    models.HarvestingStatus.objects.filter(harvesting_rule__source_id=source_id).delete()
    return redirect('harvester:harvesting_journal', source_id=source.id)


@login_required
@atomic
def add_indexing_rule(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    if request.method == 'POST':
        form = forms.IndexingRuleForm(request.POST)
        if form.is_valid():
            indexing_rule = form.save(commit=False)
            indexing_rule.source = source
            indexing_rule.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='create',
            #     user=request.user,
            #     content_type=models.IndexingStatus,
            #     content_id=indexing_rule.id,
            # )
            return redirect('harvester:source', id=source.id)
    else:
        form = forms.IndexingRuleForm()
    return render(request, 'harvester/indexing_rule_form.html', {
        'form': form,
        'source': source,
    })


@login_required
@atomic
def change_indexing_rule(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    indexing_rule = get_object_or_404(models.IndexingRule, id=id)
    if request.method == 'POST':
        form = forms.IndexingRuleForm(request.POST, instance=indexing_rule)
        if form.is_valid():
            indexing_rule = form.save(commit=False)
            indexing_rule.source = source
            indexing_rule.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='update',
            #     user=request.user,
            #     content_type=models.IndexingStatus,
            #     content_id=indexing_rule.id,
            # )
            return redirect('harvester:source', id=source.id)
    else:
        form = forms.IndexingRuleForm(instance=indexing_rule)
    return render(request, 'harvester/indexing_rule_form.html', {
        'form': form,
        'source': source,
        'indexing_rule': indexing_rule,
    })


@login_required
@atomic
def delete_indexing_rule(request, source_id, id):
    source = get_object_or_404(models.Source, id=source_id)
    indexing_rule = get_object_or_404(models.IndexingRule, id=id)

    # log_action(
    #     request,
    #     app='harvester',
    #     action='delete',
    #     user=request.user,
    #     content_type=models.IndexingStatus,
    #     content_id=indexing_rule.id,
    # )
    indexing_rule.delete()
    return redirect('harvester:source', id=source.id)


@login_required
@atomic
def indexing_journal(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    indexing_status_list = models.IndexingStatus.objects.filter(source_id=source_id).order_by('-create_date')
    paginator = Paginator(indexing_status_list, 25)  # Show 25 contacts per page

    page = request.GET.get('page')
    indexing_statuses = paginator.get_page(page)
    return render(request, 'harvester/indexing_journal.html', {
        'indexing_statuses': indexing_statuses,
        'source': source,
    })


@login_required
@atomic
def clean_indexing_journal(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    models.IndexingStatus.objects.filter(source_id=source_id).delete()
    return redirect('harvester:indexing_journal', source_id=source.id)


@login_required
@atomic
def records(request, source_id=None):
    source = None
    q = Q()
    if source_id is not None:
        source = get_object_or_404(models.Source, id=source_id)
        q &= Q(source=source)
    records_list = models.Record.objects.filter(q).order_by('-update_date')
    paginator = Paginator(records_list, 25)  # Show 25 contacts per page

    page = request.GET.get('page')
    records = paginator.get_page(page)

    total_records = models.Record.objects.filter(q).count()
    records_for_delete = models.Record.objects.filter(q & Q(deleted=True)).count()
    return render(request, 'harvester/records.html', {
        'records': records,
        'source': source,
        'total_records': total_records,
        'records_for_delete': records_for_delete,
    })


@login_required
@atomic
def record(request, source_id=None):
    id = request.GET.get('id')
    source_code = request.GET.get('source')
    original_id = request.GET.get('ln')
    record_source = None
    if source_id is not None:
        record_source = get_object_or_404(models.Source, id=source_id)
    if id:
        record = get_object_or_404(models.Record, id=id)
    elif source_code and original_id:
        source = get_object_or_404(models.Source, code=source_code)
        record = get_object_or_404(models.Record, source=source, original_id=original_id)
    else:
        return HttpResponse(
            'Укажите id или код источника source и идентификатор 001 поля записи oid',
            code=400
        )
    record_content = get_object_or_404(models.RecordContent, record=record)

    view = request.GET.get('view', 'html')
    if view == 'json':
        return HttpResponse(record_content.content, content_type='application/json')
    jrecord = record_from_json(record_content.content)
    index_document = indexing_utils.get_index_document(record)
    if type(index_document) != dict:
        index_document = index_document.to_dict()

    index_document_json = json.dumps(index_document, ensure_ascii=False, indent=2)
    record_content_json = json.dumps(json.loads(record_content.content), ensure_ascii=False, indent=2)
    return render(request, 'harvester/record.html', {
        'record': record,
        'record_content': record_content,
        'jrecord': jrecord,
        'index_document_json': index_document_json,
        'record_content_json': record_content_json,
        'source': record_source,
    })


@login_required
@atomic
def delete_source_records(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    harvesting.delete_source_records(source.id)
    return redirect('harvester:source', id=source.id)


@login_required
@atomic
def clean_source_records(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    harvesting.clean_source_records(source.id)
    return redirect('harvester:source', id=source.id)


@login_required
@atomic
def collect_source(request, source_id):
    source = get_object_or_404(models.Source, id=source_id)
    harvesting.collect_source(source.id)
    #tasks.collect_source(source.id)
    return redirect('harvester:source', id=source.id)


@login_required
# @atomic
def collect_by_harvesting_rule(request, id):
    harvesting_rule = get_object_or_404(models.HarvestingRule, id=id)
    return redirect('harvester:source', id=source.id)


@login_required
@atomic
def index_transformation_rules(request):
    index_transformation_rules = models.IndexTransformationRule.objects.all()
    return render(request, 'harvester/index_transformation_rules.html', {
        'index_transformation_rules': index_transformation_rules
    })


@login_required
@atomic
def add_index_transformation_rule(request):
    save_and_edit = request.POST.get('sae')
    if request.method == 'POST':
        form = forms.IndexTransformationRuleForm(request.POST)
        if form.is_valid():
            transformation_rule = form.save(commit=False)
            transformation_rule.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='create',
            #     user=request.user,
            #     content_type=models.IndexTransformationRule,
            #     content_id=transformation_rule.id,
            # )
            if save_and_edit is None:
                return redirect('harvester:index_transformation_rules')
            else:
                return redirect('harvester:change_index_transformation_rule', id=transformation_rule.id)
    else:
        form = forms.IndexTransformationRuleForm()
    return render(request, 'harvester/index_transformation_rule_form.html', {
        'form': form
    })


@login_required
@atomic
def change_index_transformation_rule(request, id):
    transformation_rule = get_object_or_404(models.IndexTransformationRule, id=id)
    save_and_edit = request.POST.get('sae')
    if request.method == 'POST':
        form = forms.IndexTransformationRuleForm(request.POST, instance=transformation_rule)
        if form.is_valid():
            form.save()
            # log_action(
            #     request,
            #     app='harvester',
            #     action='update',
            #     user=request.user,
            #     content_type=models.IndexTransformationRule,
            #     content_id=transformation_rule.id,
            # )
            if save_and_edit is None:
                return redirect('harvester:index_transformation_rules')
    else:
        form = forms.IndexTransformationRuleForm(instance=transformation_rule)
    return render(request, 'harvester/index_transformation_rule_form.html', {
        'form': form,
        'transformation_rule': transformation_rule,
    })


@login_required
@atomic
def delete_index_transformation_rule(request, id):
    transformation_rule = get_object_or_404(models.IndexTransformationRule, id=id)

    # log_action(
    #     request,
    #     app='harvester',
    #     action='delete',
    #     user=request.user,
    #     content_type=models.IndexTransformationRule,
    #     content_id=transformation_rule.id,
    # )
    transformation_rule.delete()
    return redirect('harvester:index_transformation_rules')


@login_required
#@atomic
def index_source(request, id):
    source = get_object_or_404(models.Source, id=id)
    transformation_rule = source.transformation_rule
    if not transformation_rule:
        return HttpResponse('У источника не указано правило трансформации', status=400)
    indexing_utils.index_source(source.id)
    #tasks.index_source(id)
    return redirect('harvester:source', id=id)


@login_required
@atomic
def reset_source_index(request, id):
    source = get_object_or_404(models.Source, id=id)
    indexing_utils.reset_source_index(id)
    return redirect('harvester:source', id=id)


@login_required
@atomic
def clean_source_index(request, id):
    source = get_object_or_404(models.Source, id=id)
    indexing_utils.clean_source_index(id)
    return redirect('harvester:source', id=id)