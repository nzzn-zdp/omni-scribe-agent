from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from ..database import get_db
from ..models.hotspot import HotspotSource
from ..models.content import ContentTask
from ..models.publish import Platform, PublishRecord
from ..models.config import SystemConfig
from ..core.event_bus import event_bus
from ..core.task_queue import task_queue

router = APIRouter()

# 默认配置项
DEFAULT_CONFIGS = [
    {"key": "openai_api_key", "value": "", "description": "OpenAI API密钥", "category": "llm", "is_sensitive": True},
    {"key": "openai_model", "value": "gpt-4", "description": "OpenAI模型", "category": "llm", "is_sensitive": False},
    {"key": "claude_api_key", "value": "", "description": "Claude API密钥", "category": "llm", "is_sensitive": True},
    {"key": "claude_model", "value": "claude-3-opus-20240229", "description": "Claude模型", "category": "llm", "is_sensitive": False},
    {"key": "wechat_app_id", "value": "", "description": "微信公众号AppID", "category": "platform", "is_sensitive": False},
    {"key": "wechat_app_secret", "value": "", "description": "微信公众号AppSecret", "category": "platform", "is_sensitive": True},
    {"key": "weibo_access_token", "value": "", "description": "微博访问令牌", "category": "platform", "is_sensitive": True},
    {"key": "zhihu_client_id", "value": "", "description": "知乎客户端ID", "category": "platform", "is_sensitive": False},
    {"key": "zhihu_client_secret", "value": "", "description": "知乎客户端密钥", "category": "platform", "is_sensitive": True},
    {"key": "xiaohongshu_cookie", "value": "", "description": "小红书Cookie", "category": "platform", "is_sensitive": True},
    {"key": "wordpress_url", "value": "", "description": "WordPress站点地址", "category": "platform", "is_sensitive": False},
    {"key": "wordpress_username", "value": "", "description": "WordPress用户名", "category": "platform", "is_sensitive": False},
    {"key": "wordpress_password", "value": "", "description": "WordPress密码", "category": "platform", "is_sensitive": True},
    {"key": "hotspot_check_interval", "value": "300", "description": "热点检查间隔（秒）", "category": "system", "is_sensitive": False},
    {"key": "hotspot_min_score", "value": "0.6", "description": "热点最低分数", "category": "system", "is_sensitive": False},
    {"key": "publish_retry_count", "value": "3", "description": "发布重试次数", "category": "system", "is_sensitive": False},
    {"key": "publish_retry_delay", "value": "60", "description": "发布重试延迟（秒）", "category": "system", "is_sensitive": False},
]

@router.get("/dashboard")
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    """获取仪表盘数据"""
    # 获取热点源数量
    hotspot_sources_count = await db.query(HotspotSource).count()
    
    # 获取内容任务统计
    content_tasks_count = await db.query(ContentTask).count()
    completed_tasks_count = await db.query(ContentTask).filter(
        ContentTask.status == "completed"
    ).count()
    
    # 获取发布记录统计
    publish_records_count = await db.query(PublishRecord).count()
    published_count = await db.query(PublishRecord).filter(
        PublishRecord.status == "published"
    ).count()
    
    return {
        "hotspot_sources": hotspot_sources_count,
        "content_tasks": {
            "total": content_tasks_count,
            "completed": completed_tasks_count
        },
        "publish_records": {
            "total": publish_records_count,
            "published": published_count
        }
    }

@router.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "event_bus": "connected",
        "task_queue": "connected",
        "database": "connected"
    }

@router.post("/system/config")
async def update_system_config(config_data: Dict[str, Any]):
    """更新系统配置"""
    # 发布配置更新事件
    await event_bus.publish("system", "config_updated", config_data)
    
    return {"message": "配置已更新"}

@router.get("/logs")
async def get_system_logs(log_type: str = "system", limit: int = 100):
    """获取系统日志"""
    # 这里应该从日志文件或数据库读取日志
    # 简化实现，返回示例数据
    return {
        "logs": [
            {"timestamp": "2026-06-22 10:00:00", "level": "INFO", "message": "系统启动"},
            {"timestamp": "2026-06-22 10:01:00", "level": "INFO", "message": "热点监控开始"}
        ]
    }

@router.get("/configs", response_model=List[Dict[str, Any]])
async def get_all_configs(category: str = None, db: AsyncSession = Depends(get_db)):
    """获取所有配置"""
    query = db.query(SystemConfig)
    if category:
        query = query.filter(SystemConfig.category == category)
    configs = await query.all()
    
    return [
        {
            "id": c.id,
            "key": c.key,
            "value": "***" if c.is_sensitive and c.value else c.value,
            "description": c.description,
            "category": c.category,
            "is_sensitive": c.is_sensitive
        }
        for c in configs
    ]

@router.get("/configs/{key}")
async def get_config(key: str, db: AsyncSession = Depends(get_db)):
    """获取单个配置"""
    config = await db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return {
        "id": config.id,
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "category": config.category,
        "is_sensitive": config.is_sensitive
    }

@router.put("/configs/{key}")
async def update_config(key: str, config_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """更新配置"""
    config = await db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    config.value = config_data.get("value", config.value)
    await db.commit()
    
    # 发布配置更新事件
    await event_bus.publish("system", "config_updated", {"key": key, "value": config.value})
    
    return {"message": "配置已更新", "key": key}

@router.post("/configs/init")
async def init_default_configs(db: AsyncSession = Depends(get_db)):
    """初始化默认配置"""
    for config_data in DEFAULT_CONFIGS:
        existing = await db.query(SystemConfig).filter(SystemConfig.key == config_data["key"]).first()
        if not existing:
            config = SystemConfig(**config_data)
            db.add(config)
    
    await db.commit()
    return {"message": f"已初始化 {len(DEFAULT_CONFIGS)} 个默认配置"}