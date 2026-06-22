from typing import Dict, Any, List
from ..models.publish import PublishRecord
from ..database import get_db


class PublishTracker:
    """发布状态跟踪器"""
    
    async def track_status(self, record_id: int) -> Dict[str, Any]:
        """跟踪发布状态"""
        async with get_db() as db:
            record = await db.query(PublishRecord).filter(
                PublishRecord.id == record_id
            ).first()
            
            if not record:
                return {"error": "发布记录不存在"}
            
            return {
                "id": record.id,
                "status": record.status,
                "platform_post_id": record.platform_post_id,
                "platform_url": record.platform_url,
                "published_at": record.published_at
            }
    
    async def get_all_records(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有发布记录"""
        async with get_db() as db:
            records = await db.query(PublishRecord).offset(skip).limit(limit).all()
            
            return [
                {
                    "id": r.id,
                    "draft_id": r.draft_id,
                    "platform_id": r.platform_id,
                    "status": r.status,
                    "platform_post_id": r.platform_post_id,
                    "platform_url": r.platform_url,
                    "published_at": r.published_at,
                    "created_at": r.created_at
                }
                for r in records
            ]


# 全局发布状态跟踪器实例
publish_tracker = PublishTracker()