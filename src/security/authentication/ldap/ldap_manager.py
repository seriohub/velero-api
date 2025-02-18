from ldap3 import Server, Connection, ALL
from core.config import ConfigHelper
from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError
import time

config_app = ConfigHelper()

logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))

# Load configs
ldap_servers = config_app.get_ldap_server()
ldap_use_ssl = config_app.get_ldap_use_ssl()

ldap_base_dn = config_app.get_ldap_base_dn()
ldap_bind_dn = config_app.get_ldap_bind_dn()
ldap_bind_password = config_app.get_ldap_bind_password()
ldap_user_search_filter = config_app.ldap_user_search_filter()
ldap_authz_strategy = config_app.get_ldap_authz_strategy()

# Authorization options
ldap_authz_enable = config_app.get_ldap_authz_enabled()
ldap_authz_base_dn = config_app.get_ldap_authz_base_dn()
ldap_authz_filter = config_app.get_ldap_authz_filter()
ldap_authz_attribute = config_app.get_ldap_authz_attribute()
ldap_authz_value = config_app.get_ldap_authz_value()

# Timeout e Retry Configuration
max_retries = 3
retry_delay = 2


class LdapManager:

    def get_ldap_connection(self):
        """
        Attempts to connect to the specified LDAP servers with retries.
        Returns a valid LDAP connection or None if the attempt fails.
        """
        for ldap_server in ldap_servers:
            for attempt in range(max_retries):
                try:
                    server = Server(ldap_server, use_ssl=ldap_use_ssl, get_info=ALL, connect_timeout=5)
                    conn = Connection(server, ldap_bind_dn, ldap_bind_password, auto_bind=True)
                    logger.info(f"Connected to {ldap_server} after {attempt + 1} attempts")
                    return conn
                except (LDAPSocketOpenError, Exception) as e:
                    logger.error(f"Attempt {attempt + 1}: connection error to {ldap_server}: {e}")
                    time.sleep(retry_delay)
            logger.critical(f"LDAP server {ldap_server} unavailable after multiple attempts.")

        logger.critical("No LDAP servers available. Aborting.")
        return None

    def ldap_authorization_check(self,
                                 conn,
                                 user_dn,
                                 ldap_authz_enabled,
                                 ldap_authz_base_dn=None,
                                 ldap_authz_filter=None,
                                 ldap_authz_attribute=None,
                                 ldap_authz_value=None):
        """
        Generic function to verify LDAP authorization.

        Supports:
            Group membership verification (e.g., member=group_dn)
            Matching on custom attributes (e.g., department=IT)
            Application of base_dn, filter, attribute, and value individually or in combination

        Parameters:
            conn (ldap3.Connection): Active LDAP connection.
            user_dn (str): Distinguished Name (DN) of the authenticated user.
            ldap_authz_enabled (bool): Whether to enable authorization checks.
            ldap_authz_base_dn (str, optional): Base DN for search (can be None).
            ldap_authz_filter (str, optional): LDAP filter to select entries (can be None).
            ldap_authz_attribute (str, optional): LDAP attribute used for membership verification (can be None).
            ldap_authz_value (str, optional): Attribute value to compare against (can be None)

        Returns:
            bool: True if the user is authorized, False otherwise.
        """

        if not ldap_authz_enabled:
            logger.warning("Authorization disabled, access granted to all authenticated users.")
            return True  # If authorization is disabled, grant access.

        # Dynamically constructs the LDAP filter if specified.
        search_filter = ldap_authz_filter.replace("{user_dn}", user_dn) if ldap_authz_filter else "(objectClass=*)"

        # Sets the default base DN if not specified.
        search_base = ldap_authz_base_dn if ldap_authz_base_dn else user_dn

        logger.debug(f"Executing LDAP search with filter: {search_filter} on base: {search_base}")

        # Performs the LDAP search.
        try:
            conn.search(search_base, search_filter,
                        attributes=[ldap_authz_attribute] if ldap_authz_strategy == 'ATTRIBUTE' else ["*"])
        except Exception as ex:
            logger.error("error " + str(ex))
            return False

        # If the search returned no results, the user is not authorized
        if not conn.entries:
            logger.warning(f"No LDAP results found for filter: {search_filter}")
            return False

        # If no attribute to compare is specified, the search results are sufficient for authorization.
        if ldap_authz_strategy == 'GROUP':
            logger.info(f"Authorization granted: entry found with filter {search_filter}")
            return True

        if ldap_authz_strategy == 'ATTRIBUTE':
            # Checks the attribute value if specified
            for entry in conn.entries:
                if ldap_authz_attribute in entry:
                    attr_values = entry[ldap_authz_attribute].value
                    if isinstance(attr_values, list):  # Se l'attributo ha più valori
                        if ldap_authz_value in attr_values:
                            logger.info(f"User authorized ({ldap_authz_attribute} = {attr_values})")
                            return True
                    elif ldap_authz_value is None or ldap_authz_value == attr_values:
                        logger.info(f"User NOT authorized ({ldap_authz_attribute} != {ldap_authz_value})")
                        return True

        logger.warning(f"User NOT authorized ({ldap_authz_attribute} != {ldap_authz_value})")
        return False

    def ldap_authenticate(self, username, password):

        conn = self.get_ldap_connection()
        if not conn:
            return False  # No LDAP connection available

        # Searches for the user's DN
        user_search_filter = ldap_user_search_filter.replace("{username}", username)
        try:
            conn.search(ldap_base_dn, user_search_filter)
        except Exception as Ex:
            logger.error("---" + str(Ex))

        if not conn.entries:
            logger.warning("User not found in LDAP")
            return False

        user_dn = conn.entries[0].entry_dn

        logger.info("LDAP authentication successfull!")

        # Bind authentication with user credentials
        try:
            with Connection(conn.server, user_dn, password) as user_conn:
                logger.info("LDAP authentication successful!")
                user = {
                    'username': username,
                    'id': -1
                }
        except LDAPBindError:
            logger.warning("Incorrect password or invalid user")
            return False
        except LDAPSocketOpenError:
            logger.error("Network error: unable to connect to the LDAP server.")
            return False

        authorized = self.ldap_authorization_check(
            conn=conn,
            user_dn=user_dn,
            ldap_authz_enabled=ldap_authz_enable,
            ldap_authz_base_dn=ldap_authz_base_dn,
            ldap_authz_filter=ldap_authz_filter,
            ldap_authz_attribute=ldap_authz_attribute,
            ldap_authz_value=ldap_authz_value
        )

        if authorized:
            return user
        else:
            return None
