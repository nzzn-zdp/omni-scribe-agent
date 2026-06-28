import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from ..database import get_db
from ..models.publish import Platform, PublishRecord
from ..core.event_bus import event_bus

router = APIRouter()


@router.get("/platforms/", response_model=List[Dict[str, Any]])
async def get_platforms(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取平台列表"""
    platforms = await db.query(Platform).offset(skip).limit(limit).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "platform_type": p.platform_type,
            "is_active": p.is_active
        }
        for p in platforms
    ]


@router.post("/platforms/", response_model=Dict[str, Any])
async def create_platform(platform_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """创建平台配置"""
    platform = Platform(
        name=platform_data.get("name"),
        platform_type=platform_data.get("platform_type"),
        config=json.dumps(platform_data.get("config", {}))
    )
    db.add(platform)
    await db.commit()
    await db.refresh(platform)
    
    return {
        "id": platform.id,
        "name": platform.name,
        "platform_type": platform.platform_type,
        "is_active": platform.is_active
    }


@router.get("/records/", response_model=List[Dict[str, Any]])
async def get_publish_records(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取发布记录"""
    records = await db.query(PublishRecord).offset(skip).limit(limit).all()
    return [
        {
            "id": r.id,
            "draft_id": r.draft_id,
            "platform_id": r.platform_id,
            "status": r.status,
            "platform_post_id": r.platform_post_id,
            "platform_url": r.platform_url,
            "published_at": r.published_at
        }
        for r in records
    ]


@router.post("/publish/{draft_id}")
async def publish_content(draft_id: int, platforms: List[str], db: AsyncSession = Depends(get_db)):
    """发布内容"""
    # 发布发布请求事件
    await event_bus.publish("publish", "content_publish_requested", {
        "draft_id": draft_id,
        "platforms": platforms
    })
    
    return {"message": "发布请求已提交"}

@router.get("/platforms/{platform_id}", response_model=Dict[str, Any])
async def get_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个平台配置"""
    platform = await db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    return {
        "id": platform.id,
        "name": platform.name,
        "platform_type": platform.platform_type,
        "config": platform.config,
        "is_active": platform.is_active,
        "created_at": platform.created_at
    }

@router.put("/platforms/{platform_id}", response_model=Dict[str, Any])
async def update_platform(platform_id: int, platform_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """更新平台配置"""
    platform = await db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    platform.name = platform_data.get("name", platform.name)
    platform.platform_type = platform_data.get("platform_type", platform.platform_type)
    platform.config = json.dumps(platform_data.get("config", {}))
    platform.is_active = platform_data.get("is_active", platform.is_active)
    
    await db.commit()
    await db.refresh(platform)
    
    return {
        "id": platform.id,
        "name": platform.name,
        "platform_type": platform.platform_type,
        "is_active": platform.is_active
    }

@router.delete("/platforms/{platform_id}")
async def delete_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    """删除平台配置"""
    platform = await db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    await db.delete(platform)
    await db.commit()
    
    return {"message": "平台配置已删除"}