from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(200), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(String(500))
    help = Column(Text)  # 帮助信息
    category = Column(String(100), nullable=False)  # llm, platform, system
    platform = Column(String(100))  # 平台类型（如 wechat, weibo 等）
    is_sensitive = Column(Boolean, default=False)  # 是否敏感信息（如API密钥）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())