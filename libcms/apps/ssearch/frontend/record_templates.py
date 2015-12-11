# coding=utf-8
from collections import OrderedDict


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
        for tag, fields in inner_subfield.items():
            index[tag] = fields
    return index


def _get_fields(fields_index, tags):
    lookup_tags = []
    for key in fields_index.keys():
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


class RusmarcTemplate(object):
    def __init__(self, record_dict, references=None):
        self.record_dict = record_dict
        self.fields_index = _get_fields_index(record_dict)
        self.references = references or {}
        self.cache = {}

    def get_title(self, fields_index=None):
        if fields_index is None:
            fields_index = self.fields_index
        title_parts = []
        f200 = fields_index.get('200', [{}])[0]
        sfa = _get_first_subfield_data(f200, 'a').strip()
        title_parts.append(sfa)

        f200_items = f200.items()
        for i, (sf_id, sf_values) in enumerate(f200_items):
            if sf_id == 'e':
                data = _get_first_value(sf_values).strip()
                if data:
                    _append_if_not_endswith_to(title_parts, ':')
                    title_parts.append(' ' + data)
            elif sf_id == 'h':
                data = _get_first_value(sf_values).strip()
                if data:
                    _append_if_not_endswith_to(title_parts, '.', [u'…'])
                    title_parts.append(' ' + data)
            elif sf_id == 'i':
                data = _get_first_value(sf_values).strip()
                if data:
                    _append_if_not_endswith_to(title_parts, ',')
                    title_parts.append(' ' + data)
            elif sf_id == 'v':
                data = _get_first_value(sf_values).strip()
                if data:
                    _append_if_not_endswith_to(title_parts, '.')
                    title_parts.append(' ' + data)
        return u''.join(title_parts)

    def annotations(self):
        items = []
        fields = _get_fields(self.fields_index, ['330'])
        for field in fields:
            subfields = field.get('a', [])
            for subfield in subfields:
                items.append(subfield)
        return items

    def get_source(self):

        f461_link = self._get_link_from_inner(_get_inner_fields_index(self.fields_index.get('461', [{}])[0].get('1')))
        f463_link = self._get_link_from_inner(_get_inner_fields_index(self.fields_index.get('463', [{}])[0].get('1')))

        sources_parts = []

        link_title = f461_link.get('title', '')
        if link_title:
            sources_parts.append(link_title)

        link_title = f463_link.get('title', '')
        if link_title:
            sources_parts.append(link_title)

        title = u' — '.join(sources_parts)
        link = f463_link.get('id', '')

        if not link:
            link = f461_link.get('id', '')

        if not title:
            return []

        return [{
            'title': title,
            'link_id': link
        }]

    def get_content(self):
        return self._get_inner_links('464')

    def at_same_storage(self):
        return self._get_inner_links('451')

    def at_another_storage(self):
        return self._get_inner_links('452')

    def translate_link(self):
        return self._get_inner_links('453')

    def translate_original_link(self):
        return self._get_inner_links('454')

    def copy_original(self):
        return self._get_inner_links('455')

    def reproduction(self):
        return self._get_inner_links('456')

    def subject_heading(self):
        items = []
        fields = self.fields_index.get('606', [])
        for field in fields:
            parts = []
            sfa = field.get('a', [''])[0]
            if not sfa:
                continue
            parts.append(sfa)
            sfds_x = field.get('x', [])
            for sf_x in sfds_x:
                parts.append(sf_x)
            items.append(u' — '.join(parts))
        return items

    def subject_keywords(self):
        items = []
        fields = self.fields_index.get('610', [])
        for field in fields:
            for sfa in field.get('a', []):
                items.append(sfa)
        return items

    def holders(self):
        items = []
        fields = _get_fields(self.fields_index, ['850', '899'])
        for field in fields:
            subfields = field.get('a', [])
            for subfield in subfields:
                items.append({
                    'title': self.references.get('holders', {}).get(subfield, subfield),
                    'value': subfield
                })
        return items

    def shelving(self):
        items = []
        fields = self.fields_index.get('852', [])
        for field in fields:
            subfields = field.get('a', [])
            for subfield in subfields:
                items.append({
                    'title': self.references.get('holders', {}).get(subfield, subfield),
                    'value': subfield
                })
        return items

    def _get_inner_links(self, tag):
        links = []
        fields = self.fields_index.get(tag, [])
        for field in fields:
            link = self._get_link_from_inner(_get_inner_fields_index(field.get('1')))
            if link.get('title'):
                links.append(link)
        return links

    def _get_link_from_inner(self, fields_index):
        link = {}
        if fields_index:
            link['title'] = self.get_title(fields_index)
            link['id'] = fields_index.get('001', [''])[0]
        return link
