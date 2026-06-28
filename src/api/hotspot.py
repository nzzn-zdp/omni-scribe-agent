import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from ..database import get_db
from ..models.hotspot import HotspotSource, Hotspot
from ..core.event_bus import event_bus

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_hotspots(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取热点列表"""
    result = await db.execute(select(Hotspot).offset(skip).limit(limit))
    hotspots = result.scalars().all()
    return [
        {
            "id": h.id,
            "title": h.title,
            "content": h.content,
            "url": h.url,
            "score": h.score,
            "status": h.status,
            "created_at": h.created_at
        }
        for h in hotspots
    ]

@router.get("/{hotspot_id}", response_model=Dict[str, Any])
async def get_hotspot(hotspot_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个热点"""
    result = await db.execute(select(Hotspot).filter(Hotspot.id == hotspot_id))
    hotspot = result.scalar_one_or_none()
    if not hotspot:
        raise HTTPException(status_code=404, detail="热点不存在")
    
    return {
        "id": hotspot.id,
        "title": hotspot.title,
        "content": hotspot.content,
        "url": hotspot.url,
        "score": hotspot.score,
        "status": hotspot.status,
        "created_at": hotspot.created_at,
        "processed_at": hotspot.processed_at
    }

@router.post("/sources/", response_model=Dict[str, Any])
async def create_hotspot_source(source_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """创建热点源"""
    source = HotspotSource(
        name=source_data.get("name"),
        source_type=source_data.get("source_type"),
        config=json.dumps(source_data.get("config", {}))
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    return {
        "id": source.id,
        "name": source.name,
        "source_type": source.source_type,
        "is_active": source.is_active
    }

@router.post("/evaluate/{hotspot_id}")
async def evaluate_hotspot(hotspot_id: int, db: AsyncSession = Depends(get_db)):
    """评估热点质量"""
    result = await db.execute(select(Hotspot).filter(Hotspot.id == hotspot_id))
    hotspot = result.scalar_one_or_none()
    if not hotspot:
        raise HTTPException(status_code=404, detail="热点不存在")
    
    # 发布评估事件
    await event_bus.publish("hotspot", "hotspot_evaluation_requested", {
        "hotspot_id": hotspot_id,
        "title": hotspot.title
    })
    
    return {"message": "评估请求已提交"}

@router.get("/sources/", response_model=List[Dict[str, Any]])
async def get_hotspot_sources(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取热点源列表"""
    result = await db.execute(select(HotspotSource).offset(skip).limit(limit))
    sources = result.scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "is_active": s.is_active,
            "created_at": s.created_at
        }
        for s in sources
    ]

@router.get("/sources/{source_id}", response_model=Dict[str, Any])
async def get_hotspot_source(source_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个热点源"""
    result = await db.execute(select(HotspotSource).filter(HotspotSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="热点源不存在")
    
    return {
        "id": source.id,
        "name": source.name,
        "source_type": source.source_type,
        "config": source.config,
        "is_active": source.is_active,
        "created_at": source.created_at
    }

@router.put("/sources/{source_id}", response_model=Dict[str, Any])
async def update_hotspot_source(source_id: int, source_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """更新热点源"""
    result = await db.execute(select(HotspotSource).filter(HotspotSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="热点源不存在")
    
    source.name = source_data.get("name", source.name)
    source.source_type = source_data.get("source_type", source.source_type)
    source.config = json.dumps(source_data.get("config", {}))
    source.is_active = source_data.get("is_active", source.is_active)
    
    await db.commit()
    await db.refresh(source)
    
    return {
        "id": source.id,
        "name": source.name,
        "source_type": source.source_type,
        "is_active": source.is_active
    }

@router.delete("/sources/{source_id}")
async def delete_hotspot_source(source_id: int, db: AsyncSession = Depends(get_db)):
    """删除热点源"""
    result = await db.execute(select(HotspotSource).filter(HotspotSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="热点源不存在")
    
    await db.delete(source)
    await db.commit()
    
    return {"message": "热点源已删除"}