from .models import Record


def get_value(namespace: str, key: str, dflt=None) -> str:
    record = Record.objects.filter(namespace=namespace, key=key).first()
    if record is None:
        return dflt
    return record.value


def set_value(namespace: str, key: str, value: str):
    record = Record.objects.filter(namespace=namespace, key=key).first()
    if record is None:
        Record.objects.bulk_create([Record(namespace=namespace, key=key, value=value)])
    else:
        record.value = value
        record.save()
