from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ClickLog(Base):
    __tablename__ = "click_logs"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False, index=True)
    ip_hash = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    country = Column(String(100), nullable=True)
    device = Column(String(100), nullable=True)
    referer = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    link = relationship("Link", back_populates="click_logs")
