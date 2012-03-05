# -*- coding: utf-8 -*-
try:
    from django.conf import settings
except ImportError:
    import settings

import ldap
import ldap.modlist as modlist
from ldapuser import LdapUser , user_attr_map, user_get_fields
from ldaporganisation import LdapOrganisation, org_attr_map, org_get_fields

class LdapWorkException(Exception): pass

class LdapConnection(object):
    def __init__(self, settings_map):

        """
        settings_map = {
            'server_uri': 'ldap://host:389',
            'bind_dn': 'cn=Manager,dc=Organisation,dc=ru',
            'bind_password': 'secret',
            'base_dn': 'dc=org,dc=com'
        }
        ldap_server_uri -- адрес LDAP сервера. eg ldap://localhost:389
        bind_dn -- dn для аутентификации. eg 'cn=Manager,dc=example,dc=com'
        password -- пароль
        base_dn -- корень, с которым будем работать
        """

        if 'server_uri' in settings_map and settings_map['server_uri']:
            ldap_server_uri = settings_map['server_uri']
        else: raise AttributeError('server_uri not defined')

        if 'bind_dn' in settings_map and settings_map['bind_dn']:
            bind_dn = settings_map['bind_dn']
        else: raise AttributeError('bind_dn not defined')

        if 'bind_password' in settings_map and settings_map['bind_password']:
            password = settings_map['bind_password']
        else: raise AttributeError('bind_password not defined')

        if 'base_dn' in settings_map and settings_map['base_dn']:
            base_dn = settings_map['base_dn']
        else: raise AttributeError('base_dn not defined')

        self.ldap_connection = ldap.initialize(ldap_server_uri)
        self.ldap_connection.set_option(ldap.OPT_NETWORK_TIMEOUT, 10)
        self.ldap_connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        try:
            self.ldap_connection.simple_bind_s(bind_dn, password)
        except ldap.SERVER_DOWN:
            raise LdapWorkException('LDAP server ' + ldap_server_uri + 'not founded')
        self.base_dn = base_dn

    def __del__(self):
        self.ldap_connection.unbind_s()

    def search(self, filter, attrs, base_dn='',node = ''):
        """
        node - dn отностительно base_dn. Если node не пустрой, то будет осуществляться поиск только по уровню
            Если node == '.' то поиск будет произведен только на уровне base_dn
        return list if results. if no results return emty list []
        """
        #print filter
        try:
            if base_dn == '':
                if node and node != '.': base_dn = node.strip(', ') + ',' + self.base_dn
                else: base_dn = self.base_dn
            if node:
                ldap_results = self.ldap_connection.search_s(base_dn, ldap.SCOPE_ONELEVEL, filter, attrs)
            else:
                ldap_results = self.ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
            return ldap_results
        except Exception as e:
            raise LdapWorkException(e)


    def create_record(self, ldap_map, creation_dn=''):
        if creation_dn:
            dn = creation_dn.strip(', ') + ',' + self.base_dn
        else:
            dn = self.base_dn
        ldif = modlist.addModlist(ldap_map)
        try:
            self.ldap_connection.add_s(dn,ldif)
        except ldap.INVALID_DN_SYNTAX:
            raise LdapWorkException("can't create record. Wrong dn")

class LdapWork(object):
    """
    Класс для работы с LDAP базой. 
    Содержит методы для управления организациями и пользователями
    """
    def __init__(self, ldap_connectiin):
        if isinstance(ldap_connectiin, LdapConnection):
            self.ldap_connectiin = ldap_connectiin
        elif isinstance(ldap_connectiin, dict):
            self.ldap_connectiin = LdapConnection(ldap_connectiin)
        else:
            raise TypeError("ldap_connectiin must be LdapConnection or config dict")

    def get_users_by_attr(self, username='', password='', member_of='', sn='', email='', phone='', node=''):
        """
        return list of users. if no users - return empty []
        """
        filter = []
        if username:
            filter.append('('+ user_attr_map['uid'] + '=' + username.encode('utf-8') +')')
        if password:
            filter.append('(' + user_attr_map['password'] + '=' + password.encode('utf-8') + ')')
        if member_of:
            filter.append('('+ attr_map['member_of'] +'=' + str(member_of) + ')')
        if sn:
            filter.append('('+ user_attr_map['sn'] +'=' + str(sn) + ')')
        if email:
            filter.append('('+ user_attr_map['email'] +'=' + str(email) + ')')
        if phone:
            filter.append('('+ user_attr_map['phone'] +'=' + str(phone) + ')')

        filter.append('(' + user_attr_map['ldap_ident'] + ')')
        if len(filter) > 1:
            filter.insert(0,'(&')
            filter.append(')')


        filter = ''.join(filter)
        ldap_results = self.ldap_connectiin.search(filter, user_get_fields, node=node)

        users = []
        for ldap_result in ldap_results:
            #print ldap_result
            users.append(LdapUser().from_ldap_map(ldap_result))

        return users


    
    def get_org_by_attr(self, code='', o='', display_name='', district='', member_of='', node=''):
        """
        return list of users. if no users - return empty []
        """
        o = o.replace('(','\(').replace(')','\)')
        filter = []
        if o:
             filter.append('('+ org_attr_map['o'] + '=' + o +')')
        if display_name:
            filter.append('('+ org_attr_map['display_name'] + '=' + display_name +')')

        if district:
            filter.append('('+ org_attr_map['district'] + '=' + district +')')

        if member_of:
            filter.append('('+ org_attr_map['member_of'] + '=' + member_of +')')
        elif not o:
            filter.append('('+ org_attr_map['member_of'] + '=' + 'library' +')')

        if code:
            filter.append('('+ org_attr_map['code'] + '=' + code +')')


        filter.append('(' + org_attr_map['ldap_ident'] + ')')
        if len(filter) > 1:
            filter.insert(0,'(&')
            filter.append(')')


        filter = ''.join(filter)
        #print filter
        ldap_results = self.ldap_connectiin.search(filter, org_get_fields, node=node)

        orgs = []
        for ldap_result in ldap_results:
            #print ldap_result
            orgs.append(LdapOrganisation().from_ldap_map(ldap_result))

        return orgs


    def user_registration(self, user, registration_dn=''):
        registration_dn = 'cn='+user.cn.strip(', ') + ','+ registration_dn
        try:
            self.ldap_connectiin.create_record(user.to_ldap_map(), registration_dn)
        except ldap.ALREADY_EXISTS:
            return False
        return True

    def reg_library(self, title, address, phone, site_url, 
                    email, latitude, longitude,
                    country, city, district, code, edd, time, paren_org = ''):
        """
        Метод для регистрации библиотеки
        """
        adding_oblect = {}
        adding_oblect['objectClass'] = ['RUSLANorg', 'organization', 'top']
        adding_oblect['o'] = title
        adding_oblect['displayname'] = title
        adding_oblect['mail'] = email
        
        if address != '': adding_oblect['postaladdress'] = address
        
        if phone != '': adding_oblect['telephonenumber'] = phone
        
        if site_url != '': adding_oblect['httpservice'] = site_url
        
        if latitude != '': adding_oblect['latitude'] = latitude
        
        if longitude != '': adding_oblect['longitude'] = longitude
        
        if country != '': adding_oblect['c'] = country
        
        if city != '': adding_oblect['l'] = city
        
        if district != '': adding_oblect['district'] = district
        
        if code != '': adding_oblect['code'] = code
        
        if edd != '': adding_oblect['eddservice'] = edd
        
        if edd != '': adding_oblect['plans'] = time
        
        if paren_org == '':
            dn_org = 'o=%s,%s' % (title, self.base_dn)
        else:
            dn_org = dn_org = 'o=%s,o=%s,%s' % (title, paren_org, self.base_dn)

        ldif = modlist.addModlist(adding_oblect)
        self.ldap_connection.add_s(dn_org,ldif)
        
        
                    
                    
