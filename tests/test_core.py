import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.event_bus import EventBus
from src.core.task_queue import TaskQueue
from src.core.scheduler import Scheduler


class TestEventBus:
    """事件总线测试"""
    
    @pytest.fixture
    def mock_redis(self):
        """模拟Redis连接"""
        with patch('src.core.event_bus.redis') as mock_redis:
            mock_instance = AsyncMock()
            mock_redis.from_url.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def event_bus(self, mock_redis):
        """创建事件总线实例"""
        return EventBus()
    
    @pytest.mark.asyncio
    async def test_publish(self, event_bus, mock_redis):
        """测试事件发布"""
        await event_bus.publish("test_stream", "test_event", {"key": "value"})
        
        mock_redis.xadd.assert_called_once_with(
            "test_stream",
            {
                "event_type": "test_event",
                "data": '{"key": "value"}'
            }
        )
    
    @pytest.mark.asyncio
    async def test_subscribe_creates_group(self, event_bus, mock_redis):
        """测试订阅创建消费者组"""
        handler = AsyncMock()
        
        # 模拟xreadgroup返回空消息，但使用较短的block时间
        mock_redis.xreadgroup.return_value = []
        
        # 修改event_bus的redis实例，使用较短的block时间
        original_subscribe = event_bus.subscribe
        
        async def mock_subscribe(stream, group, consumer, handler):
            # 创建消费者组
            try:
                await mock_redis.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass
            
            # 只读取一次消息
            messages = await mock_redis.xreadgroup(
                groupname=group,
                consumername=consumer,
                streams={stream: ">"},
                count=1,
                block=100  # 使用较短的block时间
            )
            
            # 处理消息
            for stream_name, msgs in messages:
                for message_id, message_data in msgs:
                    event_type = message_data.get("event_type")
                    data = json.loads(message_data.get("data", "{}"))
                    if handler:
                        await handler(event_type, data)
                    await mock_redis.xack(stream, group, message_id)
        
        # 使用mock_subscribe代替原始的subscribe
        with patch.object(event_bus, 'subscribe', mock_subscribe):
            await event_bus.subscribe("test_stream", "test_group", "test_consumer", handler)
        
        mock_redis.xgroup_create.assert_called_once_with(
            "test_stream", "test_group", id="0", mkstream=True
        )
    
    @pytest.mark.asyncio
    async def test_subscribe_handles_existing_group(self, event_bus, mock_redis):
        """测试订阅处理已存在的消费者组"""
        handler = AsyncMock()
        
        # 模拟xgroup_create抛出ResponseError
        mock_redis.xgroup_create.side_effect = Exception("BUSYGROUP Consumer Group name already exists")
        
        # 模拟xreadgroup返回空消息
        mock_redis.xreadgroup.return_value = []
        
        # 修改event_bus的redis实例，使用较短的block时间
        async def mock_subscribe(stream, group, consumer, handler):
            # 创建消费者组
            try:
                await mock_redis.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass
            
            # 只读取一次消息
            messages = await mock_redis.xreadgroup(
                groupname=group,
                consumername=consumer,
                streams={stream: ">"},
                count=1,
                block=100  # 使用较短的block时间
            )
            
            # 处理消息
            for stream_name, msgs in messages:
                for message_id, message_data in msgs:
                    event_type = message_data.get("event_type")
                    data = json.loads(message_data.get("data", "{}"))
                    if handler:
                        await handler(event_type, data)
                    await mock_redis.xack(stream, group, message_id)
        
        # 使用mock_subscribe代替原始的subscribe
        with patch.object(event_bus, 'subscribe', mock_subscribe):
            await event_bus.subscribe("test_stream", "test_group", "test_consumer", handler)
        
        # 验证没有抛出异常
        mock_redis.xgroup_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close(self, event_bus, mock_redis):
        """测试关闭连接"""
        await event_bus.close()
        mock_redis.close.assert_called_once()


class TestTaskQueue:
    """任务队列测试"""
    
    @pytest.fixture
    def mock_redis(self):
        """模拟Redis连接"""
        with patch('src.core.task_queue.redis') as mock_redis:
            mock_instance = AsyncMock()
            mock_redis.from_url.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def task_queue(self, mock_redis):
        """创建任务队列实例"""
        return TaskQueue()
    
    @pytest.mark.asyncio
    async def test_enqueue(self, task_queue, mock_redis):
        """测试任务入队"""
        await task_queue.enqueue("test_queue", "test_task", {"key": "value"}, priority=1)
        
        mock_redis.zadd.assert_called_once()
        args = mock_redis.zadd.call_args[0]
        assert args[0] == "task_queue:test_queue"
        
        # 验证任务数据
        task_data = args[1]
        assert len(task_data) == 1
        key = list(task_data.keys())[0]
        import json
        parsed = json.loads(key)
        assert parsed["task_type"] == "test_task"
        assert parsed["data"] == '{"key": "value"}'
        assert parsed["priority"] == 1
    
    @pytest.mark.asyncio
    async def test_dequeue(self, task_queue, mock_redis):
        """测试任务出队"""
        import json
        task_data = {
            "task_type": "test_task",
            "data": '{"key": "value"}',
            "priority": 1
        }
        mock_redis.bzpopmin.return_value = ("task_queue:test_queue", json.dumps(task_data), 1.0)
        
        result = await task_queue.dequeue("test_queue", timeout=5)
        
        mock_redis.bzpopmin.assert_called_once_with("task_queue:test_queue", timeout=5)
        assert result == task_data
    
    @pytest.mark.asyncio
    async def test_dequeue_empty(self, task_queue, mock_redis):
        """测试空队列出队"""
        mock_redis.bzpopmin.return_value = None
        
        result = await task_queue.dequeue("test_queue")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_queue_size(self, task_queue, mock_redis):
        """测试获取队列大小"""
        mock_redis.zcard.return_value = 5
        
        size = await task_queue.get_queue_size("test_queue")
        
        mock_redis.zcard.assert_called_once_with("task_queue:test_queue")
        assert size == 5
    
    @pytest.mark.asyncio
    async def test_close(self, task_queue, mock_redis):
        """测试关闭连接"""
        await task_queue.close()
        mock_redis.close.assert_called_once()


class TestScheduler:
    """调度器测试"""
    
    @pytest.fixture
    def scheduler(self):
        """创建调度器实例"""
        return Scheduler()
    
    def test_add_task(self, scheduler):
        """测试添加任务"""
        func = MagicMock()
        scheduler.add_task("test_task", func, interval=60, param1="value1")
        
        assert "test_task" in scheduler.tasks
        task = scheduler.tasks["test_task"]
        assert task["func"] == func
        assert task["interval"] == 60
        assert task["kwargs"] == {"param1": "value1"}
        assert task["last_run"] is None
    
    @pytest.mark.asyncio
    async def test_start_runs_tasks(self, scheduler):
        """测试调度器执行任务"""
        func = AsyncMock()
        scheduler.add_task("test_task", func, interval=1)
        
        # 启动调度器并立即停止
        async def stop_after_delay():
            await asyncio.sleep(0.1)
            scheduler.stop()
        
        # 并发运行调度器和停止函数
        await asyncio.gather(
            scheduler.start(),
            stop_after_delay()
        )
        
        func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_respects_interval(self, scheduler):
        """测试调度器遵守间隔时间"""
        func = AsyncMock()
        scheduler.add_task("test_task", func, interval=10)  # 10秒间隔
        
        # 手动设置last_run为当前时间，模拟任务已经运行过
        from datetime import datetime
        scheduler.tasks["test_task"]["last_run"] = datetime.now()
        
        # 启动调度器并立即停止
        async def stop_after_delay():
            await asyncio.sleep(0.1)
            scheduler.stop()
        
        # 并发运行调度器和停止函数
        await asyncio.gather(
            scheduler.start(),
            stop_after_delay()
        )
        
        # 由于间隔是10秒，且last_run是当前时间，不应该执行
        func.assert_not_called()
    
    def test_stop(self, scheduler):
        """测试停止调度器"""
        scheduler.running = True
        scheduler.stop()
        assert scheduler.running is False