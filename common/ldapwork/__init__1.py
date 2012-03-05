# -*- coding: utf-8 -*-
"""
from common.functions import ForLdap 
class LdapOrganisation(object):
    #карта отображения атрибутов пользоватлея на LDAP объект
    attr_map = {'o': 'o',
                'country': 'c',
                'code': 'code',
                'display_name': 'displayName',
                'district': 'district',
                'edd_service': 'eddService',
                'http_service': 'httpService',
                'ill_service': 'illService',
                'location': 'l',
                'phone': 'telephoneNumber',
                'email': 'mail',
                'email_access': 'mailAccess', #сервера доступа к почте
                'plans': 'plans', #расписание работы
                'postal_address': 'postalAddress',
                'osi_latitude': 'osiLatitude', #географические координаты
                'osi_longitude': 'osiLongitude',
                'member_of': 'memberOf',
                'ldap_object_class': 'objectClass',
                }
    def __init__(self, title = None, country = None, code = None, district = None, 
                 edd_service = None, http_service = None, ill_service = None, 
                 location = None, phone = None, email = None, email_access = None, plans = None,
                 postal_address = None, osi_latitude = None, osi_longitude = None):
        
        self.title = title     
        self.country = country
        self.code = code
        self.district = district
        self.edd_service = edd_service
        self.http_service = http_service
        self.ill_service = ill_service
        self.location = location
        self.phone = phone
        self.email = email
        self.email_access = email_access
        self.plans = plans
        self.postal_address = postal_address
        self.osi_latitude = osi_latitude
        self.osi_longitude = osi_longitude
        self._member_of = []
        self._ldap_object_classes = []
    
    @property
    def member_of(self):
        return self._member_of
    
    @member_of.setter
    def member_of(self, value): pass
    
    @property
    def ldap_object_classes(self):
        return self._ldap_object_classes
    
    @ldap_object_classes.setter
    def ldap_object_classes(self, value): pass
        
    def add_ldap_object_class(self, class_name):
        self._ldap_object_classes.append(class_name)
    
    def add_member_of(self, member_of):
        self._member_of.append(member_of)
    
    def to_ldap_map(self):
        
        ldap_map = {}
        
        if self.title:
            ldap_map[user_get_fields['o']] = self.title
            ldap_map[user_get_fields['display_name']] = self.title
        
        if self.country:
            ldap_map[user_get_fields['country']] = self.country
        
        if self.code:
            ldap_map[user_get_fields['code']] = self.code
        
        if self.district:
            ldap_map[user_get_fields['district']] = self.district
        
        if self.edd_service:
            ldap_map[user_get_fields['edd_service']] = self.edd_service
        
        if self.http_service:
            ldap_map[user_get_fields['http_service']] = self.http_service
        
        if self.ill_service:
            ldap_map[user_get_fields['ill_service']] = self.ill_service
        
        if self.location:
            ldap_map[user_get_fields['location']] = self.location
            
        if self.phone:
            ldap_map[user_get_fields['phone']] = self.phone
            
        if self.email:
            ldap_map[user_get_fields['email']] = self.email
        
        if self.email_access:
            ldap_map[user_get_fields['email_access']] = self.email_access
        
        if self.plans:
            ldap_map[user_get_fields['plans']] = self.plans
        
        if self.postal_address:
            ldap_map[user_get_fields['postal_address']] = self.postal_address
        
        if self.osi_latitude:
            ldap_map[user_get_fields['osi_latitude']] = self.osi_latitude
        
        if self.osi_longitude:
            ldap_map[user_get_fields['osi_longitude']] = self.osi_longitude
        
        if self.member_of:
            ldap_map[user_get_fields['member_of']] = self.member_of
        
        if self.ldap_object_classes:
            ldap_map[user_get_fields['ldap_object_class']] = self.ldap_object_classes
                   
        return ldap_map
    
    def from_ldap_map(self, ldap_map):
        
        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['o'])
        if temp : 
            self.title = temp

        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['country'])
        if temp: 
            self.country = temp #ФИО человека :)
        
        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['code'])
        if temp: 
            self.code = temp
        
        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['district'])
        if temp: 
            self.district = temp

        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['edd_service'])
        if temp: 
            self.edd_service = temp
        
        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['ill_service'])
        if temp: 
            self.ill_service = temp       

        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['location'])
        if temp: 
            self.location = temp  

        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['phone'])
        if temp: 
            self.phone = temp  

        temp = ForLdap.get_ldap_attribute_first(ldap_map, user_get_fields['email'])
        if temp: 
            self.email = temp  
            
        temp = ForLdap.get_ldap_attribute(ldap_map, user_get_fields['email_access'])
        if temp:
            self.email_access = temp

        temp = ForLdap.get_ldap_attribute(ldap_map, user_get_fields['plans'])
        if temp:
            self.plans = temp
            
        temp = ForLdap.get_ldap_attribute(ldap_map, user_get_fields['postal_address'])
        if temp:
            self.postal_address = temp
            
        temp = ForLdap.get_ldap_attribute(ldap_map, user_get_fields['osi_latitude'])
        if temp:
            self.osi_latitude = temp
            
        temp = ForLdap.get_ldap_attribute(ldap_map, user_get_fields['osi_longitude'])
        if temp:
            self.osi_longitude = temp
            
        temp = ForLdap.get_ldap_attribute(ldap_map, user_get_fields['member_of'])
        if temp:
            self._member_of = temp
            
        temp = ForLdap.get_ldap_attribute(ldap_map, user_get_fields['ldap_object_class'])
        if temp:
            self.ldap_object_classes = temp
"""
