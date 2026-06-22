import asyncio
import json
from typing import Dict, Any, List
from ..core.event_bus import event_bus
from ..database import get_db
from ..models.hotspot import HotspotSource, Hotspot
from .adapters import RSSAdapter, APIAdapter, CrawlerAdapter
from .evaluator import HotspotEvaluator
from .filter import HotspotFilter


class HotspotMonitor:
    """热点监控器"""
    
    def __init__(self):
        self.adapters = {
            "rss": RSSAdapter(),
            "api": APIAdapter(),
            "crawler": CrawlerAdapter()
        }
        self.evaluator = HotspotEvaluator()
        self.filter = HotspotFilter()
    
    async def start(self):
        """启动热点监控"""
        # 发布系统启动事件
        await event_bus.publish("system", "system_started", {
            "module": "hotspot_monitor"
        })
        
        # 开始监控热点源
        while True:
            try:
                await self._check_all_sources()
                await asyncio.sleep(300)  # 5分钟检查一次
            except Exception as e:
                print(f"热点监控异常: {e}")
                await asyncio.sleep(60)  # 异常后1分钟重试
    
    async def _check_all_sources(self):
        """检查所有热点源"""
        async with get_db() as db:
            # 获取所有活跃的热点源
            sources = await db.query(HotspotSource).filter(
                HotspotSource.is_active == True
            ).all()
            
            for source in sources:
                try:
                    await self._process_source(source)
                except Exception as e:
                    print(f"处理热点源 {source.name} 失败: {e}")
    
    async def _process_source(self, source: HotspotSource):
        """处理单个热点源
        
        Args:
            source: 热点源配置
        """
        adapter = self.adapters.get(source.source_type)
        if not adapter:
            print(f"未知的热点源类型: {source.source_type}")
            return
        
        # 获取热点
        config = json.loads(source.config)
        hotspots = await adapter.fetch_hotspots(config)
        
        # 评估热点
        evaluated_hotspots = []
        for hotspot in hotspots:
            evaluation = await self.evaluator.evaluate(hotspot)
            hotspot.update(evaluation)
            evaluated_hotspots.append(hotspot)
        
        # 过滤热点
        filtered_hotspots = await self.filter.filter(evaluated_hotspots)
        
        # 保存热点到数据库
        async with get_db() as db:
            for hotspot_data in filtered_hotspots:
                hotspot = Hotspot(
                    source_id=source.id,
                    title=hotspot_data.get("title"),
                    content=hotspot_data.get("content"),
                    url=hotspot_data.get("url"),
                    score=hotspot_data.get("score", 0),
                    status="pending"
                )
                db.add(hotspot)
            
            await db.commit()
        
        # 发布热点发现事件
        for hotspot_data in filtered_hotspots:
            await event_bus.publish("hotspot", "hotspot_discovered", {
                "source_id": source.id,
                "title": hotspot_data.get("title"),
                "score": hotspot_data.get("score", 0)
            })


# 全局热点监控器实例
hotspot_monitor = HotspotMonitor()