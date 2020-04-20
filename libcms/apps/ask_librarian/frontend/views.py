# -*- coding: utf-8 -*-
from django.db import transaction, models
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from common.pagination import get_page

from ..models import Question, Category, Recomendation, StatusJournal
from .forms import QuestionForm, RecomendationForm, DateFilterForm


def index(request):
    id = request.GET.get('id', None)
    q = request.GET.get('q', '')
    if id:
        try:
            id = int(id)
        except ValueError:
            raise Http404()
        return redirect('ask_librarian:frontend:detail', id=id)

    category = request.GET.get('category', None)
    if category:
        try:
            category = int(category)
        except ValueError:
            raise Http404()
    categories = []
    category_m = None
    if category:
        try:
            category_m = Category.objects.get(id=category)
        except Category.DoesNotExist:
            raise Http404('Категория не найдена')

        if category_m:
            categories.append(category_m)
            descendants = category_m.get_descendants()
            for descendant in descendants:
                categories.append(descendant)
    else:
        categories = list(Category.objects.all())

    q_criteria = models.Q(status=1)

    if q:
        terms = q.split()
        question_terms_q = None
        answer_terms_q = None
        for term in terms:
            if len(term) < 1:
                continue
            if not question_terms_q:
                question_terms_q = models.Q(question__icontains=term)
                answer_terms_q = models.Q(answer__icontains=term)
            else:
                question_terms_q &= models.Q(question__icontains=term)
                answer_terms_q &= models.Q(answer__icontains=term)

        if question_terms_q:
            q_criteria &= models.Q(question_terms_q | answer_terms_q)
    if id:
        q_criteria &= models.Q(id=id)

    if category and categories:
        q_criteria &= models.Q(category__in=categories)

    if category and categories:
        q_criteria &= models.Q(category__in=categories)

    if request.method == 'POST':
        date_filter_form = DateFilterForm(request.POST)
        if date_filter_form.is_valid():
            date = date_filter_form.cleaned_data['date']
            q_criteria &= models.Q(
                create_date__year=date.year,
                create_date__month=date.month,
                create_date__day=date.day
            )
    else:
        date_filter_form = DateFilterForm()

    questions_page = get_page(request, Question.objects.filter(q_criteria).order_by('-create_date'), 10)
    questions_page.object_list = list(questions_page.object_list)
    cd = {}

    for category_item in categories:
        cd[category_item.id] = category_item

    for question in questions_page.object_list:
        if question.category_id in cd:
            question.category = cd[question.category_id]

    return render(request, 'ask_librarian/frontend/questions_list.html', {
        'questions_page': questions_page,
        'category': category_m,
        'categories': categories,
        'date_filter_form': date_filter_form
    })


@transaction.atomic
def detail(request, id):
    question = get_object_or_404(Question, id=id)
    if request.method == 'POST':
        recomendation_form = RecomendationForm(request.POST, prefix='recomendation_form')
        if recomendation_form.is_valid():
            recomendation = recomendation_form.save(commit=False)
            if request.user.is_authenticated:
                recomendation.user = request.user
            recomendation.question = question
            recomendation.save()
            return render(request, 'ask_librarian/frontend/recomended_thanks.html', {
                'question': question,
            })
    else:
        recomendation_form = RecomendationForm(prefix='recomendation_form')
    recomendations = Recomendation.objects.filter(question=question, public=True).order_by('-create_date')
    return render(request, 'ask_librarian/frontend/detail.html', {
        'question': question,
        'recomendation_form': recomendation_form,
        'recomendations': recomendations
    })


def printed_detail(request, id):
    question = get_object_or_404(Question, id=id)
    return render(request, 'ask_librarian/frontend/printed_detail.html', {
        'question': question,
    })


@transaction.atomic
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            if request.user.is_authenticated:
                question.user = request.user
            question.save()
            StatusJournal.objects.bulk_create(
                [StatusJournal(question=question, user=question.user, status=question.status)]
            )

            return render(request, 'ask_librarian/frontend/thanks.html', {
                'question': question,
            })
    else:
        if request.user.is_authenticated:
            form = QuestionForm(
                initial={
                    'fio': request.user.last_name + ' ' + request.user.first_name,
                    'email': request.user.email,
                }
            )
        else:
            form = QuestionForm()

    return render(request, 'ask_librarian/frontend/ask.html', {
        'form': form
    })


@login_required
def my_questions(request):
    questions_page = get_page(request, Question.objects.filter(user=request.user).order_by('-create_date'), 10)
    return render(request, 'ask_librarian/frontend/my_questions.html', {
        'questions_page': questions_page
    })
