# encoding: utf-8
from django import forms

class CoolForm(forms.Form):
    #error_css_class = 'class-error'
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
    #        for field in self.fields:
    #            self.fields[field].widget.attrs['class'] = 'some-class other-class'
    def as_div(self):
        "Returns this form rendered as HTML <div>s."
        return self._html_output(
            normal_row = '<div%(html_class_attr)s>%(label)s %(field)s %(errors)s %(help_text)s </div>',
            error_row = '<div class="error">%s</div>',
            row_ender = '</div>',
            help_text_html = '<span class="help-block">%s</span>',
            errors_on_separate_row = False)


class CoolModelForm(forms.ModelForm):
    #error_css_class = 'class-error'
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
    #        for field in self.fields:
    #            self.fields[field].widget.attrs['class'] = 'some-class other-class'
    def as_div(self):
        "Returns this form rendered as HTML <div>s."
        return self._html_output(
            normal_row = '<div class="control-group">%(label)s %(field)s %(errors)s %(help_text)s </div>',
            error_row = '<div class="error">%s</div>',
            row_ender = '</div>',
            help_text_html = '<span class="help-block">%s</span>',
            errors_on_separate_row = False)