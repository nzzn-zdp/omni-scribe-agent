from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class HotspotSource(Base):
    """热点源配置表"""
    __tablename__ = "hotspot_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # rss, api, crawler
    config = Column(Text, nullable=False)  # JSON格式配置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Hotspot(Base):
    """热点数据表"""
    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("hotspot_sources.id"))
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000))
    score = Column(Float, default=0.0)  # 热点评分
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
