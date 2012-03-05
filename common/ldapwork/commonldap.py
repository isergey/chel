# -*- coding: utf-8 -*-

def get_ldap_attribute_first(attr_map, key):
    """
    Функция получает на вход карту вида
    attr_map = {
        'key':['value1','valueN']
    }
    и возвращает первый элемент из списка key
    Если ключ или значение не найдено, возвращается None
    """
    if attr_map.has_key(key):
        if len(attr_map[key]) > 0 : return attr_map[key][0]
        else: return None
    else: return None

def get_ldap_attribute( attr_map, key):
    """
    Функция получает на вход карту вида
    attr_map = {
        'key':['value1','valueN']
    }
    и возвращает элемент key
    Если ключ или значение не найдено, возвращается None
    """
    if attr_map.has_key(key):
        if len(attr_map[key]) > 0 : return attr_map[key]
        else: return None
    else: return None