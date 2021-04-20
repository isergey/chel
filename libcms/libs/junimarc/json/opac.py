# encode: utf-8
import json
from .. import record


def make_data_subfield(code, subfield_dict):
    return record.DataSubfield(
        code=code,
        data=subfield_dict.get('data', '')
    )


def make_control_field(tag, field_dict):
    return record.ControlField(
        tag=tag,
        data=field_dict.get('data', '')
    )


def make_extended_subfield(code, subfield_dict):
    fields = []

    for field_dict in subfield_dict.get('cf', []):
        fields.append(make_control_field(field_dict))

    for field_dict in subfield_dict.get('df', []):
        fields.append(make_data_field(field_dict))

    return record.ExtendedSubfield(
        code=code,
        fields=fields
    )


def make_data_field(tag, field_dict):
    subfields = []

    for subfield_dict in field_dict.get('subfields', []):
        code = subfield_dict.get('code', '')
        if not code:
            continue

        if code != '1':
            subfields.append(make_data_subfield(code, subfield_dict))
        else:
            subfields.append(make_extended_subfield(code, subfield_dict))

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
            fields.append(make_control_field(tag, field_dict))
        else:
            fields.append(make_data_field(tag, field_dict))

    return record.Record(
        leader=record_dict.get('leader', ''),
        fields=fields
    )


def extended_subfield_to_json(subfield):
    cf = []
    df = []

    for field in subfield.get_fields():
        if isinstance(field, record.DataField):
            df.append(data_field_to_json(field))
        else:
            cf.append(control_field_to_json(field))
    return {
        'id': subfield.get_code(),
        'cf': cf,
        'df': df,
    }


def data_subfield_to_json(subfield):
    return {
        'id': subfield.get_code(),
        'd': subfield.get_data(),
    }


def data_field_to_json(field):
    sf = []
    esf = []

    for subfield in field.get_subfields():
        if isinstance(subfield, record.DataSubfield):
            sf.append(data_subfield_to_json(subfield))
        else:
            esf.append(extended_subfield_to_json(subfield))

    return {
        'tag': field.get_tag(),
        'i1': field.get_ind1(),
        'i2': field.get_ind2(),
        'sf': sf,
        'esf': esf,
    }


def control_field_to_json(field):
    return {
        'tag': field.get_tag(),
        'd': field.get_data(),
    }


def field_to_json(field):
    if isinstance(field, record.DataField):
        return data_field_to_json()
    return


def record_to_json(jrecord, dump=False):
    cf = []
    df = []

    for field in jrecord.get_fields():
        if isinstance(field, record.DataField):
            df.append(data_field_to_json(field))
        else:
            cf.append(control_field_to_json(field))

    record_json = {
        'l': jrecord.get_leader(),
        'cf': cf,
        'df': df,
    }

    if dump:
        return json.dumps(record_json, ensure_ascii=False)
    return record_json
