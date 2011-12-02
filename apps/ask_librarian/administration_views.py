# encoding: utf-8
import datetime
from django.shortcuts import render, Http404, HttpResponse,redirect, get_object_or_404
from forms import QuestionForm
from models import Question, Category, AnswerManager, ManagerNonActivePeriod


def index(request):
    return render(request, 'administration/module.html')

def questions(request):
    return render(request, 'administration/questions.html')

def managers(request):
    return render(request, 'administration/managers.html')