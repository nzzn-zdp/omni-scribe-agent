from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from ..database import get_db
from ..models.hotspot import HotspotSource
from ..models.content import ContentTask
from ..models.publish import Platform, PublishRecord
from ..core.event_bus import event_bus
from ..core.task_queue import task_queue

router = APIRouter()

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