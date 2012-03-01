# -*- coding: utf-8 -*-
from django import forms
from forum.models import Article, Topic, Forum

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        exclude = [
            'forum',
            'created',
            'public',
            'closed',
            'deleted'
        ]

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = [
            'topic',
            'author',
            'created',
            'updated',
            'public',
            'closed',
            'deleted'
        ]


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
