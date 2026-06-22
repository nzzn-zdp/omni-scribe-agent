### 任务3：事件总线和任务队列

**Files:**
- Create: `src/core/__init__.py`
- Create: `src/core/event_bus.py`
- Create: `src/core/task_queue.py`
- Create: `src/core/scheduler.py`

**Interfaces:**
- Consumes: Redis连接（来自任务1）
- Produces: 事件发布/订阅，任务调度

- [ ] **步骤1：创建事件总线**

```python
# src/core/event_bus.py
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
```

- [ ] **步骤2：创建任务队列**

```python
# src/core/task_queue.py
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
```

- [ ] **步骤3：创建调度器**

```python
# src/core/scheduler.py
import asyncio
from typing import Callable, Dict, Any
from datetime import datetime, timedelta

class Scheduler:
    """任务调度器"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running = False
    
    def add_task(self, name: str, func: Callable, interval: int, **kwargs):
        """添加定时任务"""
        self.tasks[name] = {
            "func": func,
            "interval": interval,
            "kwargs": kwargs,
            "last_run": None
        }
    
    async def start(self):
        """启动调度器"""
        self.running = True
        while self.running:
            now = datetime.now()
            
            for name, task in self.tasks.items():
                last_run = task["last_run"]
                interval = task["interval"]
                
                if last_run is None or (now - last_run).total_seconds() >= interval:
                    try:
                        if asyncio.iscoroutinefunction(task["func"]):
                            await task["func"](**task["kwargs"])
                        else:
                            task["func"](**task["kwargs"])
                        
                        task["last_run"] = now
                    except Exception as e:
                        print(f"执行任务 {name} 失败: {e}")
            
            await asyncio.sleep(1)
    
    def stop(self):
        """停止调度器"""
        self.running = False

# 全局调度器实例
scheduler = Scheduler()
```

- [ ] **步骤4：创建核心模块初始化**

```python
# src/core/__init__.py
from .event_bus import EventBus, event_bus
from .task_queue import TaskQueue, task_queue
from .scheduler import Scheduler, scheduler

__all__ = [
    "EventBus", "event_bus",
    "TaskQueue", "task_queue",
    "Scheduler", "scheduler"
]
```

- [ ] **步骤5：运行核心模块测试**

```bash
pytest tests/test_core.py -v
```

- [ ] **步骤6：提交核心模块代码**

```bash
git add src/core/
git commit -m "feat: 添加事件总线和任务队列"
```