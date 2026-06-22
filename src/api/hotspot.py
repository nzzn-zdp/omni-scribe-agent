import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from ..database import get_db
from ..models.hotspot import HotspotSource, Hotspot
from ..core.event_bus import event_bus

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_hotspots(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取热点列表"""
    hotspots = await db.query(Hotspot).offset(skip).limit(limit).all()
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
    hotspot = await db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
    if not hotspot:
        raise HTTPException(status_code=404, detail="热点不存在")
    
    # 发布评估事件
    await event_bus.publish("hotspot", "hotspot_evaluation_requested", {
        "hotspot_id": hotspot_id,
        "title": hotspot.title
    })
    
    return {"message": "评估请求已提交"}