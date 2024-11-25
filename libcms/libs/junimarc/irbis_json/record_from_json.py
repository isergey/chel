import json
from typing import List, Tuple
from .. import record


def record_from_json(json_record: dict):
    fields = []
    for tag, flds in json_record.items():
        for subfields in flds:
            sbflds = []
            for code, data in subfields.items():
                print(code, data)
                sbflds.append(record.DataSubfield(code, data))
            fields.append(record.DataField(tag, subfields=sbflds))
    rec = record.Record(fields=fields)
    return rec

def records_from_json_list(json_list: Tuple[List, str]):
    json_records = json_list
    if isinstance(json_list, str):
        json_records = json.loads(json_list)

    records = []
    for json_record in json_records:
        records.append(record_from_json(json_record))

    return records