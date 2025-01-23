# import re
import uuid

from sqlalchemy import create_engine, Column, String, Boolean, DateTime as DateTimeA, ForeignKey, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from core.config import ConfigHelper
from helpers.database import GUID
# from sqlalchemy.dialects.postgresql import UUID

from helpers.printer import PrintHelper

config_app = ConfigHelper()
print_ls = PrintHelper('[helpers.database]',
                       level=config_app.get_internal_log_level())
path_db = config_app.get_path_db()
# SQLite database initialization
DATABASE_URL = f"sqlite:///./{path_db}/data.db"
print_ls.info(f"Users database {DATABASE_URL}")

Base = declarative_base()


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
    is_nats = False
    cp_mapping_user = ""

    def toJSON(self):
        return {'username': self.username,
                'is_admin': self.is_admin,
                'is_default': self.is_default,
                'is_disabled': self.is_disabled
                }


class RefreshToken(Base):
    __tablename__ = 'tokens'
    token = Column(String(36),
                   nullable=False,
                   primary_key=True,
                   unique=True)
    user_id = Column(GUID(),
                     ForeignKey('users.id'),
                     nullable=False)
    time_created = Column(DateTimeA(timezone=True), server_default=func.now())
    time_updated = Column(DateTimeA(timezone=True), onupdate=func.now())

    # user = orm.relationship("User", backref="tokens")

    def toJSON(self):
        return {'token': self.token,
                'user_id': self.user_id
                }


class ProjectsVersion(Base):
    __tablename__ = 'pv'

    pv_1 = Column(String(30), nullable=True)
    pv_2 = Column(String(30), nullable=True)
    pv_3 = Column(String(30), nullable=True)
    pv_4 = Column(String(30), nullable=True)
    pv_5 = Column(String(30), nullable=True)
    pv_6 = Column(String(30), nullable=True)
    time_created = Column(DateTimeA(timezone=True), primary_key=True)
    time_updated = Column(DateTimeA(timezone=True), onupdate=func.now())

    def toJSON(self):
        return {'pv_1': self.pv_1,
                'pv_2': self.pv_2,
                'pv_3': self.pv_3,
                'pv_4': self.pv_4,
                'pv_5': self.pv_5,
                'pv_6': self.pv_6,
                'time_created': self.time_created
                }


engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}
)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# User CRUD operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
