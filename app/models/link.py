from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(12), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    clicks = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    password_hash = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="links")
    click_logs = relationship("ClickLog", back_populates="link", cascade="all, delete-orphan")
