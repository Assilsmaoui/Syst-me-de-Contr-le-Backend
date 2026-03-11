from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    id = Column(String, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    app = Column(String)
    duration = Column(Float)
    username = Column(String)
    __table_args__ = (
        UniqueConstraint('start', 'end', 'app', 'username', name='unique_activity'),
    )
