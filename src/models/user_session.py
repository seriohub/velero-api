import uuid
from datetime import datetime


class UserSession:
    """User entity"""

    def __init__(self, uid=None, username=None, full_name=None, is_ldap=False, is_oauth=False, is_nats=False):
        self.id = str(uuid.uuid4()) if uid is None else uid
        self.username = username
        self.full_name = full_name
        self.is_ldap = is_ldap
        self.is_oauth = is_oauth
        self.is_nats = is_nats
        self.time_created = datetime.utcnow()
        self.time_updated = datetime.utcnow()

    def toJSON(self):
        return {'username': self.username,
                'is_nats': self.is_nats,
                'is_ldap': self.is_ldap}
