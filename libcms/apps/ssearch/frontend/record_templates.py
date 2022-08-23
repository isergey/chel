# coding=utf-8
from collections import OrderedDict
from functools import cached_property
from typing import List

from junimarc.marc_query import MarcQuery, FieldQuery


def _get_df_index(field):
    index = OrderedDict()
    index['i1'] = field.get('i1', ' ')
    index['i2'] = field.get('i2', ' ')
    for subfield in field.get('sf', []):
        id = subfield.get('id', '')
        exist_subfields = index.get(id)
        if exist_subfields is None:
            exist_subfields = []
            index[id] = exist_subfields
        inner = subfield.get('inner')
        if inner is not None:
            exist_subfields.append(_get_fields_index(inner))
        else:
            exist_subfields.append(subfield.get('d', ''))

    return index


def _get_fields_index(fields_dict):
    index = OrderedDict()
    for field in fields_dict.get('cf', []):
        tag = field.get('id', '')
        exist_fields = index.get(tag)
        if exist_fields is None:
            exist_fields = []
            index[tag] = exist_fields
        exist_fields.append(field.get('d', ''))

    for field in fields_dict.get('df', []):
        tag = field.get('id', '')
        exist_fields = index.get(tag)
        if exist_fields is None:
            exist_fields = []
            index[tag] = exist_fields
        exist_fields.append(_get_df_index(field))
    return index


def _get_first_value(values, default=''):
    if values and len(values):
        return values[0]
    return default


def _get_first_subfield_data(field_index, id, default=''):
    return _get_first_value(field_index.get(id), default)


def _get_inner_fields_index(inner_subfields=None):
    index = OrderedDict()
    inner_subfields = inner_subfields or []
    for inner_subfield in inner_subfields:
        for tag, fields in list(inner_subfield.items()):
            index[tag] = fields
    return index


def _get_fields(fields_index, tags):
    lookup_tags = []
    for key in list(fields_index.keys()):
        if key in tags:
            lookup_tags.append(key)
    fields = []
    for tag in lookup_tags:
        ffields = fields_index.get(tag, [])
        for field in ffields:
            fields.append(field)
    return fields


def _append_if_not_endswith_to(parts, item, additionals=None):
    additionals = additionals or []
    last_item = None
    if len(parts):
        last_item = parts[-1]
    if last_item:
        if additionals:
            for additional in additionals:
                if last_item.endswith(additional):
                    return
        if last_item.endswith(item):
            return
    parts.append(item)


def append_symbol(c: str, items: List[str]):
    if not items:
        return
    last_item = items[-1].strip()
    if last_item[-1] != c:
        items.append(c)


def get_title(rq: MarcQuery, fq: FieldQuery):
    title = []
    for sfa in fq.get_subfield('a').list():
        title_part = sfa.get_data()
        if not title_part:
            continue
        if title:
            append_symbol(';', title)

        title.append(' ' + title_part)

    title_part = fq.get_subfield('b').get_data()
    if title_part:
        title.append(' [' + title_part + ']')

    title_part = fq.get_subfield('h').get_data()
    if title_part:
        append_symbol('.', title)
        title.append(' ' + title_part)

    title_part = fq.get_subfield('i').get_data()
    if title_part:
        append_symbol('.', title)
        title.append(' ' + title_part)

    title_part = fq.get_subfield('f').get_data()
    if title_part:
        title.append(' / ' + title_part)

    title_part = fq.get_subfield('g').get_data()
    if title_part:
        append_symbol(';', title)
        title.append(' ' + title_part)

    title_part = fq.get_subfield('v').get_data()
    if title_part:
        if rq.get_field('200').get_subfield('a').get_data() != title_part:
            append_symbol('.', title)
            title.append(' - ' + title_part)
    return ''.join(title)


def get_person_name(fq: FieldQuery):
    result = []
    sa = fq.get_subfield('a').get_data()
    sb = fq.get_subfield('b').get_data()
    sg = fq.get_subfield('g').get_data()

    if sg:
        result.append(sa)
        result.append(', ')
        result.append(sg)
    elif sb:
        result.append(sa)
        result.append(' ')
        result.append(sb)
    else:
        result.append(sa)
    return ''.join(result)


class RusmarcTemplate(object):
    def __init__(self, rq: MarcQuery, references=None):
        self.rq = rq
        self.references = references or {}
        self.cache = {}

    @cached_property
    def get_title(self):
        return self.__get_title()

    def __get_title(self, field=None):
        title = []
        title200 = get_title(self.rq, self.rq.get_field('200'))
        title461 = get_title(self.rq, self.rq.get_field('461').get_field('200'))
        title463 = get_title(self.rq, self.rq.get_field('463').get_field('200'))

        if title461 and title463:
            title.append(title200)
            title.append(' // ')
            title.append(title461)
            append_symbol('.', title)
            title.append(' — ')
            title.append(title463)
        elif title461:
            title.append(title461)
            append_symbol('.', title)
            title.append(' — ')
            title.append(title200)
        elif title463:
            title.append(title461)
            append_symbol('.', title)
            title.append(' — ')
            title.append(title200)
        else:
            title.append(title200)
        return ''.join(title)

    @cached_property
    def get_author(self):
        parts = []
        for fq in self.rq.get_field('700').list():
            data = get_person_name(fq)
            if data:
                parts.append(data)

        if not parts:
            data = self.rq.get_field('710').get_subfield('a').get_data()
            if data:
                parts.append(data)

        if not parts:
            data = self.rq.get_field('720').get_subfield('a').get_data()
            if data:
                parts.append(data)

        if not parts:
            data = self.rq.get_field('730').get_subfield('a').get_data()
            if data:
                parts.append(data)

        if not parts:
            data = self.rq.get_field('740').get_subfield('a').get_data()
            if data:
                parts.append(data)
        return ''.join(parts)

    @cached_property
    def get_publication_date(self):
        return self.rq.get_field('210').get_subfield('d').get_data()

    @cached_property
    def annotations(self):
        values = []
        data = self.rq.get_field('330').get_subfield('a').get_data()
        if data:
            values.append(data)
        return values

    @cached_property
    def get_source(self):
        f461q = self.rq.get_field('461')
        title = get_title(f461q, f461q.get_field('200'))
        link = f461q.get_field('001').get_data()

        if not title:
            return []
        return [{
            'title': title,
            'link_id': link
        }]

    @cached_property
    def get_content(self):
        return self._get_inner_links('464')

    @cached_property
    def at_same_storage(self):
        return self._get_inner_links('451')

    @cached_property
    def at_another_storage(self):
        return self._get_inner_links('452')

    @cached_property
    def translate_link(self):
        return self._get_inner_links('453')

    @cached_property
    def translate_original_link(self):
        return self._get_inner_links('454')

    @cached_property
    def copy_original(self):
        return self._get_inner_links('455')

    @cached_property
    def reproduction(self):
        return self._get_inner_links('456')

    @cached_property
    def subject_heading(self):
        items = []
        fields = self.rq.get_field('606').list()
        for field in fields:
            parts = []
            sfa = field.get_subfield('a').get_data()
            if not sfa:
                continue
            parts.append(sfa)
            sfds_x = field.get_subfield('x').list()
            for sf_x in sfds_x:
                parts.append(sf_x.get_data())
            items.append(' — '.join(parts))
        return items

    @cached_property
    def subject_keywords(self):
        items = []
        fields = self.rq.get_field('610').list()
        for field in fields:
            for sfaq in field.get_subfield('a').list():
                sfa = sfaq.get_data()
                if not sfa in items:
                    items.append(sfa)
        return items

    @cached_property
    def holders(self):
        items = []
        fields = self.rq.get_field('850').list() + self.rq.get_field('899').list()
        for field in fields:
            subfields = field.get_subfield('a').list()
            for subfield in subfields:
                sfd = subfield.get_data()
                items.append({
                    'title': self.references.get('holders', {}).get(sfd, sfd),
                    'value': sfd
                })
        return items

    @cached_property
    def shelving(self):
        items = []
        fields = self.rq.get_field('852').list()
        for field in fields:
            subfields = field.get_subfield('a').list()
            for subfield in subfields:
                sfd = subfield.get_data()
                items.append({
                    'title': self.references.get('holders', {}).get(sfd, sfd),
                    'value': sfd
                })
        return items

    def _get_inner_links(self, tag):
        links = []
        fields = self.rq.get_field(tag).list()
        for field in fields:
            link = self._get_link_from_inner(field)
            if link.get('title'):
                links.append(link)
        return links

    def _get_link_from_inner(self, field):
        return {
            'title': self.__get_title(field),
            'id': field.get_field('001').get_data(),
        }

    def get_collections(self):
        cols = []
        f907q = self.rq.get_field('908')
        data = f907q.get_subfield('b').get_data()
        if data:
            cols.append(data)
        else:
            return ' / '.join(cols)

        data = f907q.get_subfield('a').get_data()
        if data:
            cols.append(data)
        else:
            return ' / '.join(cols)

        data = f907q.get_subfield('c').get_data()
        if data:
            cols.append(data)
        else:
            return ' / '.join(cols)

        data = f907q.get_subfield('d').get_data()
        if data:
            cols.append(data)
        else:
            return ' / '.join(cols)

        data = f907q.get_subfield('e').get_data()
        if data:
            cols.append(data)
        else:
            return ' / '.join(cols)

        data = f907q.get_subfield('f').get_data()
        if data:
            cols.append(data)

        return ' / '.join(cols)


def get_full_text_links(marq_query):
    ft_links = []
    for fq in marq_query.get_field('856').list():
        ft_links.append({
            'url': fq.get_subfield('u').get_data(),
            'title': fq.get_subfield('2').get_data() or 'полный текст',
        })
    return ft_links
