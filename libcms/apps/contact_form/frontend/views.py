from datetime import timedelta

from django.core.mail import EmailMessage
from django.db import transaction
from django.shortcuts import render, HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from . import forms
from .. import models
# from ..settings import MAX_REQUESTS_FROM_IP_PER_MINUTE, MAX_REQUESTS_PER_MINUTE

MAX_REQUESTS_FROM_IP_PER_MINUTE = 2
MAX_REQUESTS_PER_MINUTE = 2

@csrf_exempt
@transaction.atomic()
def index(request):
    if request.method == 'POST':
        form = forms.ContactRequestForm(request.POST)
        now = timezone.now()
        past = now - timedelta(minutes=1)
        if form.is_valid():
            # if not _g_recapcha(request.POST['g-recaptcha-response']):
            #     return HttpResponse(status=400)
            ip_address = get_client_ip(request)
            if ip_address and models.get_from_date_count_from_ip(past, ip_address) >= MAX_REQUESTS_FROM_IP_PER_MINUTE:
                return HttpResponse('Вы превысили лимит обращений. Повторите через несколько минут.')

            if models.get_from_date_count(past) >= MAX_REQUESTS_PER_MINUTE:
                return HttpResponse('Превышен лимит обращений. Повторите через несколько минут.')

            contact_request = form.save(commit=False)
            contact_request.ip_address = get_client_ip(request)
            contact_request.save()
            _send_email(contact_request)
            return HttpResponse(status=200)

        else:
            return HttpResponse(status=400)

    else:
        form = forms.ContactRequestForm()

    return render(request, 'contact_form/frontend/index.html', {
        'form': form,
    })


def done(request):
    return render(request, 'contact_form/frontend/done.html', {

    })


def _render_email_template(contact_request):
    context = dict({
        'contact_request': contact_request,
    })
    template = get_template('contact_form/email/contact_request.html')
    return template.render(context)


def _send_email(contact_request):
    to = [notification_email.email for notification_email in models.NotificationEmail.objects.all()]
    if not to:
        return
    message = EmailMessage(
        subject='Запрос из контактной формы',
        to=to,
        body=_render_email_template(contact_request)
    )
    message.content_subtype = "html"
    message.send()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
