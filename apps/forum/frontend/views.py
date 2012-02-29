# -*- coding: utf-8 -*-
import postmarkup
import simplejson
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, Http404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from forum.models import Forum, Topic, Article
from forms import ArticleForm, TopicForm, ForumForm

postmarkup_render = postmarkup.create()

def index(request):
    forums = Forum.objects.all()
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('forum:frontend:forums')
    else:
        form = ForumForm()

    return render(request, 'forum/frontend/forums.html', {
        'forums': forums,
        'form': form
    })

@login_required
def topics(request, slug):
    forum = get_object_or_404(Forum, slug=slug)
    topics = Topic.objects.filter(forum=forum)
    if request.method == 'POST':
        topic_form = TopicForm(request.POST, prefix='topic')
        article_form = ArticleForm(request.POST, prefix='article')
        if topic_form.is_valid() and article_form.is_valid():
            topic = topic_form.save(commit=False)
            topic.forum = forum
            topic.save()
            article = article_form.save(commit=False)
            article.author = request.user
            article.topic = topic
            article.save()
            return redirect('forum:frontend:articles', slug=forum.slug, id=topic.id)
    else:
        topic_form = TopicForm(prefix='topic')
        article_form = ArticleForm(prefix='article')
    return render(request, 'forum/frontend/topics.html', {
        'forum': forum,
        'topics': topics,
        'topic_form': topic_form,
        'article_form': article_form,
        })



@login_required
def articles(request, slug, id, aid=None, eid=None):
    topic = get_object_or_404(Topic, id=id)
    articles_qs = Article.objects.select_related('author').filter(topic=topic)

    # пагинация сообщений в топике форума
    paginator = Paginator(articles_qs, 20)
    page_num = request.GET.get('page', '1')
    if page_num == 'last':
        page_num = paginator.num_pages
    try:
        page = paginator.page(int(page_num))
    except (InvalidPage, ValueError):
        raise Http404()

    # отрисовка сообщений в bbcode в html
    articles = page.object_list
    for article in articles:
        article.text = postmarkup_render(article.text)

    # если пользователь нажал на цитирование
    if aid:
        quote_article = get_object_or_404(Article, id=aid)
    else:
        quote_article = None

    # если пользователь редактирует свое сообщение
    if eid:
        edit_article = get_object_or_404(Article, id=eid)
        if request.user != edit_article.author and not request.user.has_perms(['forum.change_article']):
            return  HttpResponseForbidden()
    else:
        edit_article = None

    if request.method == 'POST':
        if edit_article:
            form = ArticleForm(request.POST, instance=edit_article)
        else:
            form = ArticleForm(request.POST)

        if form.is_valid():
            if edit_article:
                form.save()
                return redirect('forum:frontend:articles', slug=topic.forum.slug, id=topic.id)

            article = form.save(commit=False)
            article.author = request.user
            article.topic = topic
            if quote_article:
                article.text = u"[quote][b]%s[/b]:\n%s[/quote] %s" % (
                quote_article.author.username, quote_article.text, article.text)

            article.save()

            return redirect('forum:frontend:articles', slug=topic.forum.slug, id=topic.id)
    else:
        if edit_article:
            form = ArticleForm(instance=edit_article)
        else:
            form = ArticleForm()

    if quote_article:
        quote_article.text = postmarkup_render(quote_article.text)
    if edit_article:
        edit_article.text = postmarkup_render(edit_article.text)

    return render(request, 'forum/frontend/articles.html', {
        'topic': topic,
        'articles': articles,
        'quote_article': quote_article,
        'edit_article': edit_article,
        'form': form

    })

@login_required
def article_delete(request, id):
    if not request.user.has_perms(['forum.delete_article']):
        return HttpResponseForbidden()

    article = get_object_or_404(Article, id=id)
    topic =  article.topic
    article.delete()

    if request.is_ajax():
        return HttpResponse(u'{"status":"ok"}')
    else:
        return redirect('forum:frontend:articles', slug=topic.forum.slug, id=topic.id)

@login_required
def article_hide(request, id):
    if not request.user.has_perms(['forum.publish_article']):
        return HttpResponseForbidden()

    article = get_object_or_404(Article, id=id)
    article.public = False
    article.save()

    if request.is_ajax():
        return HttpResponse(u'{"status":"ok"}')
    else:
        return redirect('forum:frontend:articles', slug=article.topic.forum.slug, id=article.topic.id)


@login_required
def article_show(request, id):
    if not request.user.has_perms(['forum.publish_article']):
        return HttpResponseForbidden()

    article = get_object_or_404(Article, id=id)
    article.public = True
    article.save()

    if request.is_ajax():
        return HttpResponse(u'{"status":"ok"}')
    else:
        return redirect('forum:frontend:articles', slug=article.topic.forum.slug, id=article.topic.id)


def article_preview(request):
    if request.method == 'POST':
        text = request.POST.get('text', u' ')
        result = {'text':postmarkup_render(text)}
        return HttpResponse(simplejson.dumps(result, ensure_ascii=False))

    return HttpResponse(u'{}')