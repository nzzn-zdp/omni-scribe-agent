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

@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_content_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个内容任务"""
    task = await db.query(ContentTask).filter(ContentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="内容任务不存在")
    
    return {
        "id": task.id,
        "hotspot_id": task.hotspot_id,
        "content_type": task.content_type,
        "status": task.status,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }

@router.get("/drafts/{draft_id}", response_model=Dict[str, Any])
async def get_content_draft(draft_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个内容草稿"""
    draft = await db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="内容草稿不存在")
    
    return {
        "id": draft.id,
        "task_id": draft.task_id,
        "title": draft.title,
        "content": draft.content,
        "summary": draft.summary,
        "keywords": draft.keywords,
        "seo_score": draft.seo_score,
        "readability_score": draft.readability_score,
        "created_at": draft.created_at
    }

@router.put("/drafts/{draft_id}", response_model=Dict[str, Any])
async def update_content_draft(draft_id: int, draft_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """更新内容草稿"""
    draft = await db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="内容草稿不存在")
    
    draft.title = draft_data.get("title", draft.title)
    draft.content = draft_data.get("content", draft.content)
    draft.summary = draft_data.get("summary", draft.summary)
    draft.keywords = draft_data.get("keywords", draft.keywords)
    draft.seo_score = draft_data.get("seo_score", draft.seo_score)
    draft.readability_score = draft_data.get("readability_score", draft.readability_score)
    
    await db.commit()
    await db.refresh(draft)
    
    return {
        "id": draft.id,
        "task_id": draft.task_id,
        "title": draft.title,
        "content": draft.content,
        "summary": draft.summary,
        "seo_score": draft.seo_score,
        "readability_score": draft.readability_score
    }