# encode: utf-8
import json
from .. import record


def make_data_subfield(subfield_dict):
    return record.DataSubfield(
        code=subfield_dict['id'],
        data=subfield_dict['d']
    )


def make_control_field(field_dict):
    return record.ControlField(
        tag=field_dict['tag'],
        data=field_dict['d']
    )


def make_extended_subfield(subfield_dict):
    fields = []

    for field_dict in subfield_dict.get('cf', []):
        fields.append(make_control_field(field_dict))

    for field_dict in subfield_dict.get('df', []):
        fields.append(make_data_field(field_dict))

    return record.ExtendedSubfield(
        code=subfield_dict['id'],
        fields=fields
    )


def make_data_field(field_dict):
    subfields = []

    for subfield_dict in field_dict.get('sf', []):
        subfields.append(make_data_subfield(subfield_dict))

    for subfield_dict in field_dict.get('esf', []):
        subfields.append(make_extended_subfield(subfield_dict))

    return record.DataField(
        tag=field_dict['tag'],
        ind1=field_dict.get('i1', u' '),
        ind2=field_dict.get('i2', u' '),
        subfields=subfields
    )


def record_from_json(json_record):
    if type(json_record) == dict:
        record_dict = json_record
    else:
        record_dict = json.loads(json_record)
    fields = []

    for field_dict in record_dict.get('cf', []):
        fields.append(make_control_field(field_dict))

    for field_dict in record_dict.get('df', []):
        fields.append(make_data_field(field_dict))

    return record.Record(
        leader=record_dict.get('l'),
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
