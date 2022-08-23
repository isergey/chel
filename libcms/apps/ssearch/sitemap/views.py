from django.shortcuts import render

from harvester import models

LIMIT = 1000


def index(request):
    total_records = models.Record.objects.all().count()
    total_offsets = int(total_records / LIMIT)
    offsets = []
    for offset in range(total_offsets):
        offsets.append(offset)

    return render(request, 'ssearch/sitemap/index.html', {
        'offsets': offsets
    }, content_type='application/xml')


def records(request, offset):
    offset = int(offset) * LIMIT
    record_models = list(models.Record.objects.values('id', 'update_date').all().order_by('-create_date')[
                    offset:offset + LIMIT])
    return render(request, 'ssearch/sitemap/records.html', {
        'records': record_models,
    }, content_type='application/xml')
