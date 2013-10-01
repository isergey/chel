# -*- encoding: utf-8 -*-
from django.conf import settings
from django.template import Library
from ..frontend import titles
register = Library()



content_type_titles = {
    'a': u'библиографическое издание',
    'b': u'каталог',
    'c': u'указатель',
    'd': u'реферат',
    'e': u'словарь',
    'f': u'энциклопедия',
    'g': u'справочное издание',
    'h': u'описание проекта',
    'i': u'статистические данные',
    'j': u'учебник',
    'k': u'патент',
    'l': u'стандарт',
    'm': u'диссертация',
    'n': u'законы',
    'o': u'словарь',
    'p': u'технический отчет',
    'q': u'экзаменационный лист',
    'r': u'литературный обзор/рецензия',
    's': u'договоры',
    't': u'карикатуры или комиксы',
    'u': u'неизвестно',
    'w': u'религиозные тексты',
    'z': u'другое',
}

@register.filter
def content_type_title(code):
    return content_type_titles.get(code.lower(), code)
#

@register.filter
def attr_title(value, attr):
    return titles.get_attr_value_title(attr, value, 'ru')


language_titles = {
    'rus':u"Русский",
    'eng':u"Английский",
    'tat':u"Татарский",
    'tar':u"Татарский",
    'aze':u"Азербайджанский",
    'amh':u"Амхарский",
    'ara':u"Арабский",
    'afr':u"Африкаанс",
    'baq':u"Баскский",
    'bak':u"Башкирский",
    'bel':u"Белорусский",
    'bal':u"Белуджский",
    'bul':u"Болгарский",
    'bua':u"Бурятский",
    'hun':u"Венгерский",
    'vie':u"Вьетнамский",
    'dut':u"Голландский",
    'gre':u"Греческий",
    'geo':u"Грузинский",
    'dan':u"Датский",
    'dra':u"Дравидийские",
    'grc':u"Древнегреческий",
    'egy':u"Египетский",
    'heb':u"Иврит",
    'ind':u"Индонезийский",
    'ira':u"Иранские",
    'ice':u"Исландский",
    'spa':u"Испанский",
    'ita':u"Итальянский",
    'kaz':u"Казахский",
    'cat':u"Каталанский",
    'kir':u"Киргизский",
    'chi':u"Китайский",
    'kor':u"Корейский",
    'cpe':u"Креольские",
    'cam':u"Кхмерский",
    'khm':u"Кхмерский",
    'lat':u"Латинский",
    'lav':u"Латышский",
    'lit':u"Литовский",
    'mac':u"Македонский",
    'chm':u"Марийский",
    'mon':u"Монгольский",
    'mul':u"Многоязычный",
    'ger':u"Немецкий",
    'nor':u"Норвежский",
    'per':u"Персидский",
    'pol':u"Польский",
    'por':u"Португальский",
    'rum':u"Румынский",
    'sla':u"Славянский",
    'slo':u"Словацкий",
    'tib':u"Тибетский",
    'tur':u"Турецкий",
    'tus':u'Tускарора',
    'uzb':u"Узбекский",
    'ukr':u"Украинский",
    'fin':u"Финский",
    'fiu':u"Финно-угорские",
    'fre':u"Французский",
    'hin':u"Хинди",
    'che':u"Чеченский",
    'cze':u"Чешский",
    'chv':u"Чувашский",
    'swe':u"Шведский",
    'est':u"Эстонский",
    'epo':u"Эсперанто",
    'esp':u"Эсперанто",
    'eth':u"Эфиопский",
    'gez':u"Эфиопский",
    'jpn':u"Японский",
    'jap':u"Японский",

}

@register.filter
def language_title(code):
    return language_titles.get(code, code)
