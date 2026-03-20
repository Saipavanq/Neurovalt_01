from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from app.database import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), index=True, nullable=False)
    user_id = Column(String(100), index=True, nullable=False)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    query_used = Column(Text, nullable=True)
    relevance_score = Column(Float, default=0.0)
    access_type = Column(String(50), default="search")  # search, direct, system
