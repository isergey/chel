# -*- coding: utf-8 -*-

LDAP = {
    'server_uri': 'ldap://ldap.arbicon.ru:389',
    'bind_dn': 'cn=Manager,dc=Arbicon,dc=ru',
    'bind_password': 'Ass-12rack',
    'base_dn': 'dc=arbicon,dc=ru'
}


from ldap_work import LdapWork, LdapConnection, LdapUser

ldap_connection = LdapConnection(LDAP)
lw = LdapWork(ldap_connection)

print len(lw.get_users_by_attr(username='edd_contact', password='9vsicXrRT'))
#for user in lw.get_users_by_attr(username='edd_contact'):
#    print user,'\n'



