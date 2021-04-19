from typing import List, Optional
from django.conf import settings
from django.template.loader import render_to_string

from subscribe.models import Subscribe, Letter
# from .models import News

SUBSCRIPTION_CODE = 'news'

SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')

#
# def create_subscription_letter(news_list: List[News]) -> Optional[Letter]:
#     if not len(news_list):
#         return
#
#     subscribe = Subscribe.objects.filter(code=SUBSCRIPTION_CODE).first()
#
#     if subscribe is None:
#         subscribe = Subscribe(
#             code=SUBSCRIPTION_CODE,
#             name='Новости'
#         )
#         subscribe.save()
#
#     content = render_to_string('news/email/subscription.html', {
#         'news_list': news_list,
#         'subscribe': subscribe,
#         'SITE_DOMAIN': SITE_DOMAIN
#     })
#
#     letter = Letter(
#         subscribe=subscribe,
#         subject='Новости',
#         content_format='html',
#         content=content
#     )
#
#     letter.save()
#     return letter