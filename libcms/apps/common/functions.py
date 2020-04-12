# encoding: utf-8
import re
#Замена запрещенных символов xnl пробелами
RE_XML_ILLEGAL = '([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' +\
                 '|' +\
                 '([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' %\
                 (chr(0xd800),chr(0xdbff),chr(0xdc00),chr(0xdfff),
                  chr(0xd800),chr(0xdbff),chr(0xdc00),chr(0xdfff),
                  chr(0xd800),chr(0xdbff),chr(0xdc00),chr(0xdfff))

def replace_illegal(xml_string):
    return re.sub(RE_XML_ILLEGAL, " ", xml_string)
