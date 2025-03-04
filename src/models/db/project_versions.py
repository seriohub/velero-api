from sqlalchemy import Column, String, DateTime as DateTimeA, func

from database.base import Base


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
