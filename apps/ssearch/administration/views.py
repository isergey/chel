# coding: utf-8
from lxml import etree
from django.core.files.storage import default_storage
from forms import UploadForm
from ssearch.models import Upload
from django.shortcuts import render, redirect, HttpResponse
from common.pymarc2 import reader, record, marcxml

#Our initial page
def initial(request):
    return render(request, 'ssearch/administration/upload.html', {
        'form': UploadForm(),
        })


#Our file upload handler that the form will post to
def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

    return redirect('ssearch:administration:initial')


def pocess(request):
    uploaded_file = Upload.objects.filter(processed=False)[:1]

    if not uploaded_file:
        return HttpResponse(u'No files')
    else:
        uploaded_file = uploaded_file[0]


    source = None
    try:
        source = default_storage.open(uploaded_file.file)
    except IOError:
        uploaded_file.delete()
        return HttpResponse(u'Fail')

    for mrecord in reader.Reader(record.UnimarcRecord, source):
        print etree.tostring(marcxml.record_to_rustam_xml(mrecord), encoding='UTF-8')

    #    attrs = {'field1': 'value1', 'field2': 'value2'}
    #    filter_attrs = {'filter_field': 'filtervalue'}
    #    rows = MyModel.objects.filter(**filter_attrs).update(**attrs)
    #    if not rows:
    #        attrs.update(filter_attrs)
    #        obj = MyModel.objects.create(**attrs)

    return HttpResponse(u'ok')


def convert():
    pass


def indexing():
    pass

