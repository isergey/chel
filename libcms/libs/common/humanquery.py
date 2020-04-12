# -*- coding: utf-8 -*-
import re

operator_title = {
    'AND': 'И',
    'NOT': 'И НЕ',
    'ANDNOT': 'ИЛИ',
}

attr_title = {
    '1':{
        'name': 'Точка доступа',
        '4': 'Заглавие',
        '1003': 'Автор',
        '21': 'Тематика'
    },
    '2':{
        'name': 'Отношение',
        '1': 'мньше',
        '2': 'меньше или равно',
        '3': 'равно',
        '4': 'больше или равно',
        '5': 'больше',
        '6': 'не равно',
        '100': 'фонетическое совпадение',
        '101': 'Stem',
        '102': 'релевантно',
        '103': 'AlwaysMatches',
    },
    '3':{
        'name': 'Позиция',
        '1': 'првое в поле',
        '2': 'первое в подполе',
        '3': 'любая',
    },
    '4':{
        'name': 'Структура',
        '1': 'фраза',
        '2': 'слово',
        '3': 'ключ',
        '4': 'год',
        '5': 'дата (нормализованная)',
        '6': 'список слов',
        '100': 'Date (un-normalized)',
        '101': 'Name (normalized)',
        '102': 'Name (un-normalized)',
        '103': 'структура',
        '104': 'Urx',
        '105': 'текст в свободной форме',
        '106': 'Document-text',
        '107': 'Local-number',
        '108': 'String',
        '109': 'Numeric string',
    },
    '5':{
        'name': 'Усечение',
        '1': 'справа',
        '2': 'слева',
        '3': 'справа и слева',
        '100': 'не обрезать',
        '101': 'Process # in search term',
        '102': 'RegExpr-1',
        '103': 'RegExpr-2',
    },
    '6':{
        'name': 'Completeness',
        '1': 'Incomplete subfield',
        '2': 'Complete subfield',
        '3': 'Complete field',
    }
}
attr_systems = {
    '1.2.840.10003.3.1': 'Bib-1'
}

class HumanQuery(object):
    def __init__(self, arm_query):
        if isinstance(arm_query, str) == False:
            raise TypeError('arm_query must be unicode')
        self.arm_query = arm_query

    def convert(self):
        opps_regx = re.compile(r"(\w+)\(", re.UNICODE)
        aributes_regx = re.compile(r"(\d+),(\d+):([\d.]+)", re.UNICODE)
        #terms_regx = re.compile(ur"[\(,]?([\w\s\[\]s,~!@#$%\^&\*=-_/\\{}`\?]+)(\[[\d,:.]+\])", re.UNICODE)
        terms_regx = re.compile(r"[\(,]?([^\[()]+)(\[[\d,:.]+\])", re.UNICODE)
        operators = re.findall(opps_regx, self.arm_query)
        terms = re.findall(terms_regx, self.arm_query)
        terms_list = [] # список поисковых термов
        terms_aributes = [] # список атрибутов, соответвующих термам
        if len(terms) != (len(operators)+1):
            raise ValueError('in arm_query number of terms and their operators do not match')
        if len(terms):
            for (term, attr_string) in terms:
                terms_list.append(term)
                aributes = re.findall(aributes_regx, attr_string)
                terms_aributes.append(aributes)
        else:
            raise ValueError('arm_query no have search term')

        if len(terms_aributes) == len(terms):
            terms_aributes.append(aributes)
        else:
            raise ValueError('in arm_query number of terms and their attributes do not match')        

        request_map = []
        index = 0
        op_index = len(operators)
        for term in terms_list:
            op_index -=1
            if terms_aributes[index]:
                (attribute, point, system) = terms_aributes[index][0]
            else:
                continue
            params = {'main':'', 'additional':''}
            if attribute in attr_title and point in attr_title[attribute]:
                params['main'] = "%s: %s " % (attr_title[attribute][point], term)
            else:
                params['main'] = "%s: %s " % (attribute+'='+point, term)
            additional = []
            for (attribute, point, system) in terms_aributes[index][1:]:
                if attribute in attr_title and point in attr_title[attribute]:
                    additional.append("%s — %s" % (attr_title[attribute]['name'], attr_title[attribute][point]))
                else:
                    additional.append("%s=%s" % ('Unknown atribute '+attribute, point))
            params['additional'] = '; '.join(additional)
            request_map.append(params)
            if op_index > -1:
                    request_map.append(operators[op_index])
            #print attribute, point, system
            index += 1
        buil_strings = []
        for item in request_map:
            if isinstance(item, dict):
                buil_strings.append(item['main'])#, u'Доп. условия: ', item['additional']
            else:
                buil_strings.append(operator_title[item])

        #print join(buil_strings)
        return '\n'.join(buil_strings)
