from django import forms
from ssearch.models import Upload

class UploadForm(forms.models.ModelForm):
    class Meta:
        model = Upload
        exclude = ('timestamp','processed', 'success')
