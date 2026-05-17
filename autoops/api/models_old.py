from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime, timezone
from database import Base

class Metrics(Base):

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)

    server_name = Column(String, index=True)

    cpu = Column(Float)
    memory = Column(Float)
    disk = Column(Float)

    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )