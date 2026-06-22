import redis.asyncio as redis
import json
from typing import Dict, Any, Optional
from ..config import settings


class TaskQueue:
    """基于Redis的任务队列"""
    
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url)
        self.queue_prefix = "task_queue:"
    
    async def enqueue(self, queue_name: str, task_type: str, data: Dict[str, Any], priority: int = 0):
        """将任务加入队列"""
        task_data = {
            "task_type": task_type,
            "data": json.dumps(data),
            "priority": priority
        }
        
        # 使用有序集合，按优先级排序
        await self.redis.zadd(
            f"{self.queue_prefix}{queue_name}",
            {json.dumps(task_data): priority}
        )
    
    async def dequeue(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """从队列取出任务"""
        # 从有序集合中取出优先级最高的任务
        result = await self.redis.bzpopmin(
            f"{self.queue_prefix}{queue_name}",
            timeout=timeout
        )
        
        if result:
            _, task_data, _ = result
            return json.loads(task_data)
        
        return None
    
    async def get_queue_size(self, queue_name: str) -> int:
        """获取队列大小"""
        return await self.redis.zcard(f"{self.queue_prefix}{queue_name}")
    
    async def close(self):
        """关闭连接"""
        await self.redis.close()


# 全局任务队列实例
task_queue = TaskQueue()