# -*- coding: utf-8 -*-
import commonldap

import ldap
user_attr_map = {
    'ldap_ident':'cn=*', #идентификатор пользователя в ldap
    'cn':'cn',
    'name':'sn',
    'uid':'uid',
    'phone': 'telephoneNumber',
    'email':'mail',
    'password':'userPassword',
    'member_of': 'memberOf',
    'description': 'description',
    'ldap_object_class':'objectClass',
}
user_get_fields = [
    user_attr_map['cn'],
    user_attr_map['name'],
    user_attr_map['uid'],
    user_attr_map['phone'],
    user_attr_map['email'],
    user_attr_map['password'],
    user_attr_map['member_of'],
    user_attr_map['description'],
    user_attr_map['cn'],
    user_attr_map['ldap_object_class'],
]

class LdapUser(object):
    """
    Класс для отображения LDAP пользователя
    """
    #карта отображения атрибутов пользоватлея на LDAP объект


    def __init__(self, username = '', password = '', member_of = [], name = '', email = '', phone = '', description =''):
        self.dn = '' # LDAP object dn
        self.cn = username
        self.uid = username
        self.name = name #ФИО человека :)
        self.password = password
        self.description = description
        self._member_of = []

        if isinstance(member_of, list):
            self._member_of = member_of
        else: self._member_of.append(str(member_of))

        self.email = email
        self.phone = phone
        self._ldap_object_classes = []

    def __str__(self):
        lines = [
            'cn: ' + self.cn.encode('utf-8'),
            'uid: ' + self.uid.encode('utf-8'),
            'name: ' + self.name.encode('utf-8'),
            'password: ' + self.password.encode('utf-8'),
            'member_of: ' + str(self._member_of),
            'email: ' + self.email.encode('utf-8'),
            'phone: ' + self.phone.encode('utf-8'),
        ]

        return '\n'.join(lines)

    @property
    def member_of(self):
        return self._member_of
    
    @member_of.setter
    def member_of(self, value): self._member_of.append(value)
    
    @property
    def ldap_object_classes(self):
        return self._ldap_object_classes
    
    @ldap_object_classes.setter
    def ldap_object_classes(self, value): pass

    def set_username(self, username):
        self.cn = username
        self.uid = username
    
    def add_ldap_object_class(self,class_name):
        self.ldap_object_classes.append(class_name)
    
    """
    Возвращает объект пользователя как словарь, пригодный для вставки
    в LDAP базу
    """
    def to_ldap_map(self):
        ldap_map = {}
        ldap_map[user_attr_map['ldap_object_class']] = ['RUSLANperson', 'pilotPerson', 'person', 'top']
        ldap_map[user_attr_map['cn']] = self.cn.encode('UTF-8')
        ldap_map[user_attr_map['name']] = self.name.encode('UTF-8')
        ldap_map[user_attr_map['uid']] = self.uid.encode('UTF-8')
        ldap_map[user_attr_map['password']] = self.password.encode('UTF-8')
        
        if self.member_of :
            ldap_map[user_attr_map['member_of']] = self.member_of
        if self.email :
            ldap_map[user_attr_map['email']] = self.email.encode('UTF-8')
        if self.phone :
            ldap_map[user_attr_map['phone']] = self.phone.encode('UTF-8')
        if self.description :
            ldap_map[user_attr_map['description']] = self.description.encode('UTF-8')
        return ldap_map
            
    """
    Создает объект пользователя из словаря LDAP объекта
    """
    def from_ldap_map(self, ldap_map):
        self.dn = ldap.dn.explode_dn(ldap_map[0],ldap.DN_FORMAT_LDAPV3)
        self.string_dn = ldap_map[0]
        ldap_map = ldap_map[1] #в нулевом элементе содержится dn
        temp = commonldap.get_ldap_attribute_first(ldap_map, user_attr_map['uid'])
        if temp : 
            self.cn = temp
            self.uid = temp #!!! пока совпадает с cn'ом

        temp = commonldap.get_ldap_attribute_first(ldap_map, user_attr_map['name'])
        if temp: 
            self.name = temp.decode('UTF-8') #ФИО человека :)
        
        temp = commonldap.get_ldap_attribute_first(ldap_map, user_attr_map['password'])
        if temp: 
            self.password = temp.decode('utf-8')
        
        temp = commonldap.get_ldap_attribute(ldap_map, user_attr_map['member_of'])
        if temp: 
            self._member_of = temp

        temp = commonldap.get_ldap_attribute_first(ldap_map, user_attr_map['email'])
        if temp: 
            self.email = temp.decode('utf-8')
        
        temp = commonldap.get_ldap_attribute_first(ldap_map, user_attr_map['phone'])
        if temp: 
            self.phone = temp.decode('utf-8')

        temp = commonldap.get_ldap_attribute_first(ldap_map, user_attr_map['description'])
        if temp:
            self.description = temp.decode('utf-8')

        temp = commonldap.get_ldap_attribute(ldap_map, user_attr_map['ldap_object_class'])
        if temp:
            self.ldap_object_classes = temp

        return self

        
        

        
