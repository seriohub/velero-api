import uuid

from sqlalchemy import Column, String, Boolean, DateTime as DateTimeA, func

from security.schemas.runtime.guid import GUID
from helpers.database.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True)
    full_name = Column(String)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    is_disabled = Column(Boolean, default=False)
    time_created = Column(DateTimeA(timezone=True), server_default=func.now())
    time_updated = Column(DateTimeA(timezone=True), onupdate=func.now())

    # Attributes not linked to the DB (for other forms of authentication)
    # is_nats = False         # Indicates authentication via NATS
    # is_ldap = False         # Indicates authentication via LDAP
    # cp_mapping_user = ""    # Mapping NATS client to first user db

    def toJSON(self):
        return {'username': self.username,
                'is_admin': self.is_admin,
                'is_default': self.is_default,
                'is_disabled': self.is_disabled,
                # 'is_nats': self.is_nats,
                # 'is_ldap': self.is_ldap,
                }
