from sqlalchemy import Column, String, ForeignKey, DateTime as DateTimeA, func

from security.schemas.guid import GUID
from helpers.database.base import Base


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
