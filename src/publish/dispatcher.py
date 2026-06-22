import json
import asyncio
from typing import Dict, Any, List
from ..core.event_bus import event_bus
from ..core.task_queue import task_queue
from ..models.publish import Platform, PublishRecord
from ..database import get_db
from .adapters import WechatAdapter, WeiboAdapter, ZhihuAdapter, XiaohongshuAdapter, WordPressAdapter
from .formatter import ContentFormatter


class PublishDispatcher:
    """发布调度器"""
    
    def __init__(self):
        self.adapters = {
            "wechat": WechatAdapter(),
            "weibo": WeiboAdapter(),
            "zhihu": ZhihuAdapter(),
            "xiaohongshu": XiaohongshuAdapter(),
            "wordpress": WordPressAdapter()
        }
        self.formatter = ContentFormatter()
    
    async def dispatch(self, content: Dict[str, Any], platforms: List[str]):
        """分发内容到多个平台"""
        for platform_name in platforms:
            try:
                await self._publish_to_platform(content, platform_name)
            except Exception as e:
                print(f"发布到 {platform_name} 失败: {e}")
    
    async def _publish_to_platform(self, content: Dict[str, Any], platform_name: str):
        """发布到单个平台"""
        adapter = self.adapters.get(platform_name)
        if not adapter:
            raise Exception(f"不支持的平台: {platform_name}")
        
        async with get_db() as db:
            # 获取平台配置
            platform = await db.query(Platform).filter(
                Platform.platform_type == platform_name,
                Platform.is_active == True
            ).first()
            
            if not platform:
                raise Exception(f"平台 {platform_name} 未配置")
            
            config = json.loads(platform.config)
            
            # 格式化内容
            formatted_content = self.formatter.format_for_platform(content, platform_name)
            
            # 创建发布记录
            record = PublishRecord(
                draft_id=content.get("draft_id"),
                platform_id=platform.id,
                status="publishing"
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
            
            try:
                # 发布内容
                result = await adapter.publish(formatted_content, config)
                
                # 更新发布记录
                record.status = result.get("status", "published")
                record.platform_post_id = result.get("post_id")
                record.platform_url = result.get("url")
                
                await db.commit()
                
                # 发布发布成功事件
                await event_bus.publish("publish", "content_published", {
                    "record_id": record.id,
                    "platform": platform_name,
                    "post_id": result.get("post_id")
                })
                
            except Exception as e:
                # 更新发布记录为失败
                record.status = "failed"
                await db.commit()
                
                # 发布发布失败事件
                await event_bus.publish("publish", "content_publish_failed", {
                    "record_id": record.id,
                    "platform": platform_name,
                    "error": str(e)
                })
                
                raise e


# 全局发布调度器实例
publish_dispatcher = PublishDispatcher()