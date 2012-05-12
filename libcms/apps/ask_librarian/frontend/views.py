# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import translation
from django.utils.translation import to_locale, get_language

from ..models import Question
from forms import QuestionForm

def index(request):
    return render(request, 'ask_librarian/frontend/index.html')

def ask(request):

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            print question.category
    else:
        form = QuestionForm()

    return render(request, 'ask_librarian/frontend/ask.html', {
        'form': form
    })