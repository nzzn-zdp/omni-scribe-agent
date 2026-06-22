from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Platform(Base):
    """平台配置表"""
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    platform_type = Column(String(50), nullable=False)  # wechat, weibo, zhihu, etc.
    config = Column(Text, nullable=False)  # JSON格式配置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PublishRecord(Base):
    """发布记录表"""
    __tablename__ = "publish_records"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("content_drafts.id"))
    platform_id = Column(Integer, ForeignKey("platforms.id"))
    status = Column(String(50), default="pending")  # pending, publishing, published, failed
    platform_post_id = Column(String(200))  # 平台返回的帖子ID
    platform_url = Column(String(1000))  # 平台帖子链接
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
