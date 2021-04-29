# encode: utf-8
import json
from .. import record


def make_data_subfield(code, data: str):
    return record.DataSubfield(
        code=code,
        data=data
    )


def make_control_field(tag, data=''):
    return record.ControlField(
        tag=tag,
        data=data
    )


def make_extended_subfield(code, field_dict: dict):
    fields = []
    tag = field_dict.get('tag', '')

    if tag.startswith('00'):
        fields.append(make_control_field(tag, field_dict.get('data', '')))
    else:
        fields.append(make_data_field(tag, field_dict))

    return record.ExtendedSubfield(
        code=code,
        fields=fields
    )


def make_data_field(tag: str, field_dict):
    subfields = []

    for subfield_dict in field_dict.get('subfields', []):
        code = subfield_dict.get('code', '')
        if not code:
            continue

        data = subfield_dict.get('data')

        if type(data) == dict:
            make_extended_subfield(code, data)
        else:
            subfields.append(make_data_subfield(code, data))

    ind1 = field_dict.get('ind1', ' ')
    if ind1 == '#':
        ind1 = ' '

    ind2 = field_dict.get('ind2', ' ')
    if ind2 == '#':
        ind2 = ' '

    return record.DataField(
        tag=tag,
        ind1=ind1,
        ind2=ind2,
        subfields=subfields
    )


def record_from_json(json_record):
    if type(json_record) == dict:
        record_dict = json_record
    else:
        record_dict = json.loads(json_record)

    fields = []

    for field_dict in record_dict.get('fields', []):
        tag = field_dict.get('tag', '')
        if not tag:
            continue
        if tag.startswith('00'):
            fields.append(make_control_field(tag, field_dict.get('data', '')))
        else:
            fields.append(make_data_field(tag, field_dict))

    return record.Record(
        leader=record_dict.get('leader', ''),
        fields=fields
    )


def extended_subfield_to_json(subfield):
    data = []

    for field in subfield.get_fields():
        if isinstance(field, record.DataField):
            data.append(data_field_to_json(field))
        else:
            data.append(control_field_to_json(field))
    return {
        'code': subfield.get_code(),
        'data': data,
    }


def data_subfield_to_json(subfield):
    return {
        'code': subfield.get_code(),
        'data': subfield.get_data(),
    }


def data_field_to_json(field):
    subfields = []

    for subfield in field.get_subfields():
        if isinstance(subfield, record.DataSubfield):
            subfields.append(data_subfield_to_json(subfield))
        else:
            subfields.append(extended_subfield_to_json(subfield))

    return {
        'tag': field.get_tag(),
        'ind1': field.get_ind1(),
        'ind2': field.get_ind2(),
        'subfields': subfields,
    }


def control_field_to_json(field):
    return {
        'tag': field.get_tag(),
        'data': field.get_data(),
    }


def field_to_json(field):
    if isinstance(field, record.DataField):
        return data_field_to_json(field)
    return


def record_to_json(jrecord, dump=False):
    fields = []

    for field in jrecord.get_fields():
        if isinstance(field, record.DataField):
            fields.append(data_field_to_json(field))
        else:
            fields.append(control_field_to_json(field))

    record_json = {
        'leader': jrecord.get_leader(),
        'fields': fields,
    }

    if dump:
        return json.dumps(record_json, ensure_ascii=False)
    return record_json
