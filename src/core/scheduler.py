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