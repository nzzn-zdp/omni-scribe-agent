from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from ..database import get_db
from ..models.content import ContentTask, ContentDraft
from ..core.event_bus import event_bus

router = APIRouter()

@router.get("/tasks/", response_model=List[Dict[str, Any]])
async def get_content_tasks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取内容任务列表"""
    tasks = await db.query(ContentTask).offset(skip).limit(limit).all()
    return [
        {
            "id": t.id,
            "hotspot_id": t.hotspot_id,
            "content_type": t.content_type,
            "status": t.status,
            "created_at": t.created_at
        }
        for t in tasks
    ]

@router.get("/drafts/", response_model=List[Dict[str, Any]])
async def get_content_drafts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取内容草稿列表"""
    drafts = await db.query(ContentDraft).offset(skip).limit(limit).all()
    return [
        {
            "id": d.id,
            "task_id": d.task_id,
            "title": d.title,
            "content": d.content[:200] + "..." if len(d.content) > 200 else d.content,
            "summary": d.summary,
            "seo_score": d.seo_score,
            "readability_score": d.readability_score,
            "created_at": d.created_at
        }
        for d in drafts
    ]

@router.post("/generate/{hotspot_id}")
async def generate_content(hotspot_id: int, db: AsyncSession = Depends(get_db)):
    """生成内容"""
    # 发布内容生成请求事件
    await event_bus.publish("content", "content_generation_requested", {
        "hotspot_id": hotspot_id
    })
    
    return {"message": "内容生成请求已提交"}