import redis.asyncio as redis
import json
from typing import Callable, Dict, Any, Optional
from ..config import settings


class EventBus:
    """基于Redis Streams的事件总线"""
    
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url)
        self.consumers: Dict[str, Callable] = {}
    
    async def publish(self, stream: str, event_type: str, data: Dict[str, Any]):
        """发布事件到指定流"""
        event_data = {
            "event_type": event_type,
            "data": json.dumps(data)
        }
        await self.redis.xadd(stream, event_data)
    
    async def subscribe(self, stream: str, group: str, consumer: str, handler: Callable):
        """订阅事件流"""
        # 创建消费者组
        try:
            await self.redis.xgroup_create(stream, group, id="0", mkstream=True)
        except redis.ResponseError:
            pass  # 组已存在
        
        self.consumers[f"{stream}:{group}:{consumer}"] = handler
        
        # 开始消费
        while True:
            try:
                messages = await self.redis.xreadgroup(
                    groupname=group,
                    consumername=consumer,
                    streams={stream: ">"},
                    count=1,
                    block=1000
                )
                
                for stream_name, messages in messages:
                    for message_id, message_data in messages:
                        try:
                            event_type = message_data.get("event_type")
                            data = json.loads(message_data.get("data", "{}"))
                            
                            if handler:
                                await handler(event_type, data)
                            
                            # 确认消息
                            await self.redis.xack(stream, group, message_id)
                        except Exception as e:
                            print(f"处理消息失败: {e}")
            except Exception as e:
                print(f"订阅事件失败: {e}")
    
    async def close(self):
        """关闭连接"""
        await self.redis.close()


# 全局事件总线实例
event_bus = EventBus()