"""
    admin_toolbelt.ldap_client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module provides a wrapper around the python-ldap library for 
    making certain operations against an LDAP server simpler.
"""
import hashlib

import ldap

__all__ = [
    'LdapClient',
]


class LdapClient(object):
    def __init__(self, base, host, user=None, cred=None, start_tls=True, 
            user_ou='People', group_ou='Group', username_attr='uid'):
        self.base = base
        self.conn = ldap.initialize(host)
        self.user_ou = user_ou
        self.group_ou = group_ou
        self.username_attr = username_attr
        if start_tls:
            self.conn.start_tls_s()
        if user and cred:
            self.conn.simple_bind_s(user, cred)
        
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _search_base(self, search_string):
        try:
            return self.conn.search_s(search_string, ldap.SCOPE_SUBTREE)[0][1]
        except Exception as e:
            return None

    def _search_base_multi(self, base, filterstr='(objectClass=*)', attrs=None):
        try:
            return [ i[1] for i in self.conn.search_s(
                base, ldap.SCOPE_SUBTREE, filterstr=filterstr, attrlist=attrs
            )]
        except Exception as e:
            print(e)
            return []

    def _modify_base(self, search_string, action, attr, value):
        r = self.conn.modify_s(search_string, [(action, attr, value)])

    def close(self):
        self.conn.unbind_s()

    def get_user_string(self, username):
        return '{0}={1},ou={2},{3}'.format(self.username_attr, username, self.user_ou, self.base)

    def get_group_string(self, groupname):
        return 'cn={0},ou={1},{2}'.format(groupname, self.group_ou, self.base)

    def create_user(self, username, uid, fullname, email, password, primary_group, 
            surname=None, homedir='/nfs/user/{user}', shell='/bin/bash'):
        self.conn.add_s(self.get_user_string(username), [
            ('objectClass', ['inetOrgPerson', 'organizationalPerson', 'person', 
                'posixAccount', 'shadowAccount', 'account', 'top']),
            ('cn', [username]),
            ('sn', [surname if surname else fullname.split()[-1]]),
            ('uid', [username]),
            ('uidNumber', [str(uid)]),
            ('gidNumber', [self.search_group(primary_group)['gidNumber']]),
            ('homeDirectory', [homedir.format(user=username)]),
            ('loginShell', [shell]),
            ('gecos', [fullname]),
            ('mail', [email]),
            ('userPassword', [password]),
            ('shadowLastChange', ['0']),
            ('shadowMax', ['0']),
            ('shadowWarning', ['0']),
        ])

    def create_service_user(self, username, uid, password, primary_group, 
            homedir='/usr/local/{user}', shell='/sbin/nologin'):
        self.conn.add_s(self.get_user_string(username), [
            ('objectClass', ['posixAccount', 'shadowAccount', 'account', 'top']),
            ('cn', [username]),
            ('uid', [username]),
            ('uidNumber', [str(uid)]),
            ('gidNumber', [self.search_group(primary_group)['gidNumber']]),
            ('homeDirectory', [homedir.format(user=username)]),
            ('loginShell', [shell]),
            ('gecos', [fullname]),
            ('userPassword', [password]),
            ('shadowLastChange', ['0']),
            ('shadowMax', ['0']),
            ('shadowWarning', ['0']),
        ])

    def search_user(self, username):
        return self._search_base(self.get_user_string(username))

    def search_users(self, filterstr='(objectClass=*)', attrs=None):
        return self._search_base_multi(
            'ou={0},{1}'.format(self.user_ou, self.base), filterstr=filterstr, attrs=attrs
        )

    def add_user_attr(self, username, attr, value):
        self._modify_base(self.get_user_string(username), ldap.MOD_ADD, attr, value)

    def modify_user_attr(self, username, attr, value):
        self._modify_base(self.get_user_string(username), ldap.MOD_REPLACE, attr, value)

    def remove_user_attr(self, username, attr):
        self._modify_base(self.get_user_string(username), ldap.MOD_DELETE, attr, None)

    def next_user_uid(self, filterstr='(objectClass=posixUser)'):
        return 1 + max(map(
            lambda r: int(r['uidNumber'][0]), 
            self.search_groups(filterstr=filterstr, attrs=['uidNumber'])
        ))

    def create_group(self, groupname, gid, members=[], description=''):
        self.conn.add_s(self.get_group_string(groupname), [
            ('objectClass', ['posixGroup', 'top']),
            ('cn', [groupname]),
            ('gidNumber', [str(gid)]),
            ('description', [description]),
            ('memberUid', members)
        ])

    def search_group(self, groupname):
        return self._search_base(self.get_group_string(groupname))

    def search_groups(self, filterstr='(objectClass=*)', attrs=None):
        return self._search_base_multi(
            'ou={0},{1}'.format(self.group_ou, self.base), filterstr=filterstr, attrs=attrs
        )

    def add_group_attr(self, groupname, attr, value):
        self._modify_base(self.get_group_string(groupname), ldap.MOD_ADD, attr, value)

    def modify_group_attr(self, groupname, attr, value):
        self._modify_base(self.get_group_string(groupname), ldap.MOD_REPLACE, attr, value)

    def remove_group_attr(self, groupname, attr):
        self._modify_base(self.get_group_string(groupname), ldap.MOD_DELETE, attr, None)

    def next_group_gid(self):
        return 1 + max(map(
            lambda r: int(r['gidNumber'][0]), 
            self.search_groups(filterstr='(objectClass=posixGroup)', attrs=['gidNumber'])
        ))

    def add_user_to_group(self, username, groupname):
        self.add_group_attr(groupname, 'memberUid', username)

    @classmethod
    def hash_password(cls, passwd):
        h    = hashlib.new('sha1', passwd.encode('utf-8'))
        salt = os.urandom(4)
        h.update(salt)
        return "{SSHA}" +  str(encodebytes(h.digest() + salt))

    def change_password(self, username, passwd):
        self.modify_user_attr(username, 'userPassword', self.hash_password(passwd))


