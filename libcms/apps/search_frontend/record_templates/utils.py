from typing import List

from junimarc.marc_query import SubfieldQuery, MarcQuery, FieldQuery


def append_symbol(c: str, items: List[str]):
    """
    Добавляет точку в массив items, в случае, если последний триммированный элемент не заканчивается на "точку"
    """
    if not items:
        return

    last_item = (items[-1:] or [''])[0].strip()
    if last_item[-1:] != c:
        items.append(c)


def add_to_values(values: List[str], data: str):
    if data:
        if type(data) in [list, set]:
            values.extend(data)
        else:
            values.append(data)
    return values


def get_each_subfield_data(sfq: SubfieldQuery):
    values = []
    for sf in sfq.list():
        add_to_values(values, sf.get_gata())
    return values


def get_each_filed_query(rq: MarcQuery, tag_prefix: str):
    fqs: List[FieldQuery] = []
    for fq in rq.get_fields():
        if fq.get_tag().startswith(tag_prefix):
            fqs.append(fq)
    return fqs
