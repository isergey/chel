import datetime as dt
import json
import re
from collections import OrderedDict

FIELD_TYPES = {
    'text': 'text',
    'string': 'string',
    'datetime': 'datetime',
    'integer': 'integer',
    'boolean': 'boolean',
    'number': 'number',
}

SOLR_TYPE_SUFFIXES = {
    'text': 't',
    'string': 's',
    'datetime': 'dt',
    'integer': 'l',
    'boolean': 'b',
    'number': 'l',
}

DT_FORMATS = ['%Y%m%d%H%M%S', '%Y%m%d', '%Y']
INT_RE = re.compile('\d+')
NUMBER_RE = re.compile('\d+\.\d+')


def _datetime_values_to_solr_values(values, formats=None):
    dt_values = []
    frmts = formats or DT_FORMATS
    for value in values:
        value_type = type(value)
        if value_type is str:
            for format in frmts:
                try:
                    dt_values.append(dt.datetime.strptime(value, format))
                    break
                except ValueError:
                    pass
        else:
            dt_values.append(value)
    solr_values = []
    for dt_value in dt_values:
        dt_value_type = type(dt_value)
        if dt_value_type is dt.datetime:
            solr_values.append(dt_value.isoformat() + 'Z')
        elif dt_value_type is dt.date:
            solr_values.append(dt_value.isoformat() + 'T00:00:00Z')

    return solr_values


def _interger_values_to_solr_values(values):
    solr_values = []
    for value in values:
        try:
            solr_values.append(str(int(value)))
        except ValueError:
            pass

        res = INT_RE.findall(value)
        if res:
            solr_values.append(str(int(res[0])))
        pass
    return solr_values


def _number_values_to_solr_values(values):
    solr_values = []
    for value in values:
        try:
            solr_values.append(str(float(value)))
        except ValueError:
            pass

        res = NUMBER_RE.findall(value)
        if res:
            solr_values.append(str(float(res[0])))
        pass
    return solr_values


def _boolean_values_to_solr_values(values):
    solr_values = []
    for value in values:
        value_type = type(value)
        if value_type is str:
            value_start = value.lower()[0:1]
            if value_start in ['1', 't']:
                solr_values.append(True)
            elif value_start in ['0', 'f']:
                solr_values.append(False)
        else:
            solr_values.append(value == True)

    return solr_values


class Field(object):
    def __init__(self, name, value):
        self.__name = name
        self.__value = set()
        self.__type = FIELD_TYPES['text']
        self.__lang = ''
        self.__sortable = False
        self.__date_formats = DT_FORMATS
        self.set_value(value)

    def set_value(self, value):
        self.__value = set()
        self.add_value(value)

    def add_value(self, value):
        if not value:
            return
        value_type = type(value)
        if value_type is list or value_type is tuple or value_type is set:
            for item in value:
                item_type = type(item)
                if item_type is list or item_type is tuple or item_type is set:
                    self.__value.update(item)
                else:
                    self.__value.add(item)
        else:
            self.__value.add(value)

    def sortable(self):
        self.__sortable = True
        return self

    def as_text(self, lang=''):
        self.__type = FIELD_TYPES['text']
        self.__lang = lang
        return self

    def as_string(self):
        self.__type = FIELD_TYPES['string']
        return self

    def as_datetime(self, formats=None):
        self.__type = FIELD_TYPES['datetime']
        self.__date_formats = formats
        return self

    def as_integer(self):
        self.__type = FIELD_TYPES['integer']
        return self

    def as_boolean(self):
        self.__type = FIELD_TYPES['boolean']
        return self

    def as_number(self):
        self.__type = FIELD_TYPES['number']
        return self

    def get_solr_name(self):
        name = [self.__name, '_', SOLR_TYPE_SUFFIXES[self.__type], self.__lang.lower()]
        if self.__sortable:
            name.append('s')
        return ''.join(name)

    def get_solr_value(self):
        solr_value = []
        if self.__type in [FIELD_TYPES['text'], FIELD_TYPES['string']]:
            solr_value = list(self.__value)
        else:
            if self.__type == FIELD_TYPES['datetime']:
                solr_value = _datetime_values_to_solr_values(self.__value, self.__date_formats)
            elif self.__type == FIELD_TYPES['integer']:
                solr_value = _interger_values_to_solr_values(self.__value)

            elif self.__type == FIELD_TYPES['number']:
                solr_value = _number_values_to_solr_values(self.__value)
            elif self.__type == FIELD_TYPES['boolean']:
                solr_value = _boolean_values_to_solr_values(self.__value)

        if self.__sortable and solr_value:
            if self.__type in [FIELD_TYPES['text'], FIELD_TYPES['string']]:
                solr_value = [''.join(''.join(solr_value).split(' ')).lower().strip()[0:255]]
            else:
                solr_value = [solr_value[0]]

        return solr_value


class IndexDocument(object):
    def __init__(self, id):
        self.__id = id
        self.__fields = []

    def set_field(self, name, value):
        self.__fields[name] = value

    def add_field(self, name, value):
        field = Field(name, value)
        self.__fields.append(field)
        return field

    def to_dict(self):
        converted_fields = OrderedDict()
        for field in self.__fields:
            name = field.get_solr_name()
            values = field.get_solr_value()
            if not values:
                continue
            exist_values = converted_fields.get(name)

            if exist_values is None:
                exist_values = []
                converted_fields[name] = exist_values
            exist_values.extend(values)

        for k, v in converted_fields.items():
            converted_fields[k] = list(set(v))

        converted_fields['id'] = self.__id

        return converted_fields

    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
