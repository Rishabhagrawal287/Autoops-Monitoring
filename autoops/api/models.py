from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from database import Base

class Metrics(Base):
    __tablename__ = "metrics"
    id          = Column(Integer, primary_key=True, index=True)
    server_name = Column(String)
    cpu         = Column(Float)
    memory      = Column(Float)
    disk        = Column(Float)
    timestamp   = Column(DateTime, default=datetime.utcnow)

class ServerStatus(Base):
    __tablename__ = "server_status"
    id          = Column(Integer, primary_key=True, index=True)
    server_name = Column(String, unique=True, index=True)
    last_seen   = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id          = Column(Integer, primary_key=True, index=True)
    server_name = Column(String)
    message     = Column(String)
    timestamp   = Column(DateTime, default=datetime.utcnow)

class HealingAction(Base):
    __tablename__ = "healing_actions"
    id          = Column(Integer, primary_key=True, index=True)
    server_name = Column(String)
    action      = Column(String)
    timestamp   = Column(DateTime, default=datetime.utcnow)