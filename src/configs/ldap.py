import os


class LDAPConfig:
    def __init__(self):
        self.server = os.getenv('LDAP_URI', '').split(',')
        self.base_dn = os.getenv('LDAP_BASE_DN', '')
        self.bind_dn = os.getenv('LDAP_BIND_DN', '')
        self.bind_password = os.getenv('LDAP_BIND_PASSWORD', '')
        self.use_ssl = os.getenv('LDAP_USE_SSL', 'False').lower() == 'true'
        self.search_filter = os.getenv('LDAP_USER_SEARCH_FILTER', '(&(objectClass=person)(uid={username}))')

        self.authz_strategy = os.getenv('LDAP_AUTHZ_STRATEGY', 'GROUP').upper()
        self.authz_enabled = os.getenv('LDAP_AUTHZ_ENABLED', 'False').lower() == 'true'
        self.authz_base_dn = os.getenv('LDAP_AUTHZ_BASE_DN', '')
        self.authz_filter = os.getenv('LDAP_AUTHZ_FILTER', '')
        self.authz_attribute = os.getenv('LDAP_AUTHZ_ATTRIBUTE', '')
        self.authz_value = os.getenv('LDAP_AUTHZ_VALUE', '')
