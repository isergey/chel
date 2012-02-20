# coding: utf-8
from forms import UploadForm
from ssearch.models import Upload
from django.shortcuts import render, redirect


#Our initial page
def initial(request):
    return render(request, 'ssearch/administration/upload.html', {
        'form':  UploadForm(),
    })


#Our file upload handler that the form will post to
def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

    return redirect('ssearch:administration:initial')


def pocess():
    pass

def convert():
    pass

def indexing():
    pass

