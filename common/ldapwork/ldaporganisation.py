# -*- coding: utf-8 -*-
import ldap
from commonldap import get_ldap_attribute_first, get_ldap_attribute

org_attr_map = {
                'ldap_ident':'o=*',
                'o': 'o',
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
                'weight': 'serialUnits',
                'ldap_object_class': 'objectClass',
}
org_get_fields = [
    org_attr_map['o'],
    org_attr_map['country'],
    org_attr_map['code'],
    org_attr_map['display_name'],
    org_attr_map['district'],
    org_attr_map['edd_service'],
    org_attr_map['http_service'],
    org_attr_map['ill_service'],
    org_attr_map['location'],
    org_attr_map['phone'],
    org_attr_map['email'],
    org_attr_map['email_access'],
    org_attr_map['plans'],
    org_attr_map['postal_address'],
    org_attr_map['osi_latitude'],
    org_attr_map['osi_longitude'],
    org_attr_map['member_of'],
    org_attr_map['weight'],
    org_attr_map['ldap_object_class'],
]
class LdapOrganisation(object):
    """
    Класс для отображения LDAP организации
    """
    #карта отображения атрибутов пользоватлея на LDAP объект

    def __init__(self, o = None, display_name=None, country = None, code = None, district = None,
                 edd_service = None, http_service = None, ill_service = None,
                 location = None, phone = None, email = None, email_access = None, plans = None,
                 postal_address = None, osi_latitude = None, osi_longitude = None, weight=0):
        
        self.string_dn = '' #строковое представление db
        self.dn = [] #элемент dn как список
        self.o = o
        self.display_name = display_name
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
        self.weight = weight
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

        if self.o:
            ldap_map[org_attr_map['o']] = self.o

        if self.display_name:
            ldap_map[org_attr_map['display_name']] = self.display_name
        
        if self.country:
            ldap_map[org_attr_map['country']] = self.country
        
        if self.code:
            ldap_map[org_attr_map['code']] = self.code
        
        if self.district:
            ldap_map[org_attr_map['district']] = self.district
        
        if self.edd_service:
            ldap_map[org_attr_map['edd_service']] = self.edd_service
        
        if self.http_service:
            ldap_map[org_attr_map['http_service']] = self.http_service
        else:
            self.http_service = ''
        
        if self.ill_service:
            ldap_map[org_attr_map['ill_service']] = self.ill_service
        
        if self.location:
            ldap_map[org_attr_map['location']] = self.location
            
        if self.phone:
            ldap_map[org_attr_map['phone']] = self.phone
            
        if self.email:
            ldap_map[org_attr_map['email']] = self.email
        
        if self.email_access:
            ldap_map[org_attr_map['email_access']] = self.email_access
        
        if self.plans:
            ldap_map[org_attr_map['plans']] = self.plans
        
        if self.postal_address:
            ldap_map[org_attr_map['postal_address']] = self.postal_address
        
        if self.osi_latitude:
            ldap_map[org_attr_map['osi_latitude']] = self.osi_latitude
        
        if self.osi_longitude:
            ldap_map[org_attr_map['osi_longitude']] = self.osi_longitude
        
        if self.member_of:
            ldap_map[org_attr_map['member_of']] = self.member_of

        if self.weight:
            ldap_map[org_attr_map['weight']] = self.weight

        if self.ldap_object_classes:
            ldap_map[org_attr_map['ldap_object_class']] = self.ldap_object_classes
                   
        return ldap_map


    
    def from_ldap_map(self, ldap_map):
        self.string_dn = ldap_map[0]
        self.dn = ldap.dn.explode_dn(ldap_map[0],ldap.DN_FORMAT_LDAPV3)
        ldap_map = ldap_map[1] #в нулевом элементе содержится dn
        temp = get_ldap_attribute_first(ldap_map, org_attr_map['o'])
        if temp :
            self.o = temp

        temp = get_ldap_attribute_first(ldap_map, org_attr_map['display_name'])
        if temp:
            self.display_name = temp 

        temp = get_ldap_attribute_first(ldap_map, org_attr_map['country'])
        if temp: 
            self.country = temp #ФИО человека :)
        
        temp = get_ldap_attribute_first(ldap_map, org_attr_map['code'])
        if temp: 
            self.code = temp
        
        temp = get_ldap_attribute_first(ldap_map, org_attr_map['district'])
        if temp: 
            self.district = temp

        temp = get_ldap_attribute_first(ldap_map, org_attr_map['http_service'])
        if temp:
            self.http_service = temp
        else:
            self.http_service = ''
        
        temp = get_ldap_attribute_first(ldap_map, org_attr_map['edd_service'])
        if temp: 
            self.edd_service = temp
        
        temp = get_ldap_attribute_first(ldap_map, org_attr_map['ill_service'])
        if temp: 
            self.ill_service = temp       

        temp = get_ldap_attribute_first(ldap_map, org_attr_map['location'])
        if temp: 
            self.location = temp  

        temp = get_ldap_attribute_first(ldap_map, org_attr_map['phone'])
        if temp: 
            self.phone = temp  

        temp = get_ldap_attribute_first(ldap_map, org_attr_map['email'])
        if temp: 
            self.email = temp  
            
        temp = get_ldap_attribute(ldap_map, org_attr_map['email_access'])
        if temp:
            self.email_access = temp

        temp = get_ldap_attribute(ldap_map, org_attr_map['plans'])
        if temp:
            self.plans = temp[0]
            
        temp = get_ldap_attribute(ldap_map, org_attr_map['postal_address'])
        if temp:
            self.postal_address = temp
            
        temp = get_ldap_attribute(ldap_map, org_attr_map['osi_latitude'])
        if temp:
            self.osi_latitude = temp
            
        temp = get_ldap_attribute(ldap_map, org_attr_map['osi_longitude'])
        if temp:
            self.osi_longitude = temp
            
        temp = get_ldap_attribute(ldap_map, org_attr_map['member_of'])
        if temp:
            self._member_of = temp

        temp = get_ldap_attribute(ldap_map, org_attr_map['weight'])
        if temp:
            weight = 0
            try:
                weight = int(temp[0])
            except Exception:
                pass
            
            self.weight = weight
        else:
            self.weight = 0
            
        temp = get_ldap_attribute(ldap_map, org_attr_map['ldap_object_class'])
        if temp:
            self.ldap_object_classes = temp

        return self
