# -*- coding: utf-8 -*-
from django import forms
from forum.models import Article, Topic

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        exclude = [
            'forum',
            'created',
            'public',
        ]

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = [
            'topic',
            'author',
            'created',
            'updated',
            'public'
        ]

