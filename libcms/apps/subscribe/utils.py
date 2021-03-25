from . import models


def is_have_subscribe(user, code):
    try:
        subscribe = models.Subscribe.objects.get(code=code)
    except models.Subscribe.DoesNotExist:
        return False

    subscriber = models.Subscriber.objects.filter(user=user).first()
    if subscriber is None:
        return False

    return subscriber.subscribe.filter(id=subscribe.id).exists()


def subscribe(user, group_name, code, title, lucen_query=''):
    try:
        group = models.Group.objects.get(name=group_name)
    except models.Group.DoesNotExist:
        group = models.Group(name=group_name, hidden=True)
        group.save()

    try:
        subscribe = models.Subscribe.objects.get(code=code)
    except models.Subscribe.DoesNotExist:
        subscribe = models.Subscribe(
            group=group,
            code=code,
            name=title,
            lucene_query=lucen_query
        )
        subscribe.save()

    subscriber = models.Subscriber.objects.filter(user=user).first()
    if subscriber is None:
        subscriber = models.Subscriber(user=user)
        subscriber.save()

    if not subscriber.subscribe.filter(id=subscribe.id).exists():
        subscriber.subscribe.add(subscribe)


def unsubscribe(user, code):
    try:
        subscribe = models.Subscribe.objects.get(code=code)
    except models.Subscribe.DoesNotExist:
        return

    try:
        subscriber = models.Subscriber.objects.get(user=user)
    except models.Subscriber.DoesNotExist:
        return
    subscriber.subscribe.remove(subscribe)