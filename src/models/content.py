from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class ContentTask(Base):
    """内容任务表"""
    __tablename__ = "content_tasks"

    id = Column(Integer, primary_key=True, index=True)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"))
    content_type = Column(String(50), nullable=False)  # article, post
    status = Column(String(50), default="pending")  # pending, planning, generating, optimizing, reviewing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContentDraft(Base):
    """内容草稿表"""
    __tablename__ = "content_drafts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("content_tasks.id"))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    keywords = Column(Text)  # JSON格式关键词列表
    seo_score = Column(Float, default=0.0)
    readability_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
