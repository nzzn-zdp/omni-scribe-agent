### 任务4：热点监控模块

**Files:**
- Create: `src/hotspot/__init__.py`
- Create: `src/hotspot/monitor.py`
- Create: `src/hotspot/adapters/__init__.py`
- Create: `src/hotspot/adapters/base.py`
- Create: `src/hotspot/adapters/rss_adapter.py`
- Create: `src/hotspot/adapters/api_adapter.py`
- Create: `src/hotspot/adapters/crawler_adapter.py`
- Create: `src/hotspot/evaluator.py`
- Create: `src/hotspot/filter.py`
- Create: `src/api/hotspot.py`

**Interfaces:**
- Consumes: 事件总线，任务队列，数据模型
- Produces: 热点事件，供内容生产模块使用

- [ ] **步骤1：创建热点源适配器接口**

```python
# src/hotspot/adapters/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAdapter(ABC):
    """热点源适配器基类"""
    
    @abstractmethod
    async def fetch_hotspots(self) -> List[Dict[str, Any]]:
        """获取热点列表"""
        pass
    
    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效"""
        pass
```

- [ ] **步骤2：创建RSS适配器**

```python
# src/hotspot/adapters/rss_adapter.py
import feedparser
import httpx
from typing import List, Dict, Any
from .base import BaseAdapter

class RSSAdapter(BaseAdapter):
    """RSS热点源适配器"""
    
    async def fetch_hotspots(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取RSS热点"""
        url = config.get("url")
        if not url:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                
                feed = feedparser.parse(response.text)
                hotspots = []
                
                for entry in feed.entries[:10]:  # 限制前10条
                    hotspots.append({
                        "title": entry.get("title", ""),
                        "content": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "published": entry.get("published", "")
                    })
                
                return hotspots
        except Exception as e:
            print(f"获取RSS失败: {e}")
            return []
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证RSS配置"""
        return "url" in config
```

- [ ] **步骤3：创建API适配器**

```python
# src/hotspot/adapters/api_adapter.py
import httpx
from typing import List, Dict, Any
from .base import BaseAdapter

class APIAdapter(BaseAdapter):
    """API热点源适配器"""
    
    async def fetch_hotspots(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取API热点"""
        url = config.get("url")
        headers = config.get("headers", {})
        method = config.get("method", "GET")
        
        if not url:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, timeout=10)
                else:
                    response = await client.post(url, headers=headers, timeout=10)
                
                response.raise_for_status()
                data = response.json()
                
                # 根据配置的字段映射提取数据
                field_mapping = config.get("field_mapping", {})
                hotspots = []
                
                items = data if isinstance(data, list) else data.get("items", [])
                for item in items[:10]:
                    hotspot = {}
                    for target_field, source_field in field_mapping.items():
                        hotspot[target_field] = item.get(source_field, "")
                    hotspots.append(hotspot)
                
                return hotspots
        except Exception as e:
            print(f"获取API热点失败: {e}")
            return []
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证API配置"""
        return "url" in config
```

- [ ] **步骤4：创建网页爬虫适配器**

```python
# src/hotspot/adapters/crawler_adapter.py
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseAdapter

class CrawlerAdapter(BaseAdapter):
    """网页爬虫热点源适配器"""
    
    async def fetch_hotspots(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """爬取网页热点"""
        url = config.get("url")
        selectors = config.get("selectors", {})
        
        if not url:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                hotspots = []
                
                # 根据选择器提取数据
                items = soup.select(selectors.get("item", "article"))
                
                for item in items[:10]:
                    title_elem = item.select_one(selectors.get("title", "h2"))
                    content_elem = item.select_one(selectors.get("content", "p"))
                    link_elem = item.select_one(selectors.get("link", "a"))
                    
                    hotspot = {
                        "title": title_elem.get_text().strip() if title_elem else "",
                        "content": content_elem.get_text().strip() if content_elem else "",
                        "url": link_elem.get("href", "") if link_elem else ""
                    }
                    
                    hotspots.append(hotspot)
                
                return hotspots
        except Exception as e:
            print(f"爬取网页失败: {e}")
            return []
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证爬虫配置"""
        return "url" in config and "selectors" in config
```

- [ ] **步骤5：创建热点评估器**

```python
# src/hotspot/evaluator.py
from typing import Dict, Any, List
import json

class HotspotEvaluator:
    """热点评估器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    async def evaluate(self, hotspot: Dict[str, Any]) -> Dict[str, Any]:
        """评估热点质量"""
        # 使用LLM评估热点
        prompt = f"""
        请评估以下热点话题的质量和可写性：
        
        标题：{hotspot.get('title', '')}
        内容：{hotspot.get('content', '')}
        
        请从以下维度评分（0-1分）：
        1. 时效性：话题的新鲜程度
        2. 话题性：话题的讨论价值
        3. 相关性：与目标受众的相关程度
        4. 可写性：是否容易展开写作
        
        请以JSON格式返回评分和推荐内容角度。
        """
        
        if self.llm_client:
            try:
                response = await self.llm_client.generate(prompt)
                result = json.loads(response)
                return {
                    "score": result.get("score", 0.5),
                    "angles": result.get("angles", []),
                    "evaluation": result.get("evaluation", "")
                }
            except Exception as e:
                print(f"LLM评估失败: {e}")
        
        # 默认评估逻辑
        title = hotspot.get("title", "")
        content = hotspot.get("content", "")
        
        # 简单评分逻辑
        score = 0.5
        if len(title) > 10:
            score += 0.1
        if len(content) > 100:
            score += 0.1
        if "热点" in title or "热搜" in title:
            score += 0.2
        
        return {
            "score": min(score, 1.0),
            "angles": ["常规角度"],
            "evaluation": "基于规则评估"
        }
```

- [ ] **步骤6：创建热点过滤器**

```python
# src/hotspot/filter.py
from typing import Dict, Any, List
import re

class HotspotFilter:
    """热点过滤器"""
    
    def __init__(self):
        self.sensitive_words = ["敏感词1", "敏感词2"]  # 可配置
        self.min_score = 0.6
    
    async def filter(self, hotspots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤热点列表"""
        filtered = []
        
        for hotspot in hotspots:
            # 检查评分
            if hotspot.get("score", 0) < self.min_score:
                continue
            
            # 检查敏感词
            if self._contains_sensitive_words(hotspot.get("title", "")):
                continue
            
            # 检查内容质量
            if not self._is_quality_content(hotspot):
                continue
            
            filtered.append(hotspot)
        
        return filtered
    
    def _contains_sensitive_words(self, text: str) -> bool:
        """检查是否包含敏感词"""
        for word in self.sensitive_words:
            if word in text:
                return True
        return False
    
    def _is_quality_content(self, hotspot: Dict[str, Any]) -> bool:
        """检查内容质量"""
        title = hotspot.get("title", "")
        content = hotspot.get("content", "")
        
        # 标题长度检查
        if len(title) < 5:
            return False
        
        # 内容长度检查
        if len(content) < 20:
            return False
        
        return True
```

- [ ] **步骤7：创建热点监控器**

```python
# src/hotspot/monitor.py
import asyncio
import json
from typing import Dict, Any, List
from ..core.event_bus import event_bus
from ..core.task_queue import task_queue
from ..models.hotspot import HotspotSource, Hotspot
from ..database import get_db
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
        """处理单个热点源"""
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
```

- [ ] **步骤8：创建热点API接口**

```python
# src/api/hotspot.py
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
```

- [ ] **步骤9：创建热点模块初始化**

```python
# src/hotspot/__init__.py
from .monitor import HotspotMonitor, hotspot_monitor
from .evaluator import HotspotEvaluator
from .filter import HotspotFilter
from .adapters import RSSAdapter, APIAdapter, CrawlerAdapter

__all__ = [
    "HotspotMonitor", "hotspot_monitor",
    "HotspotEvaluator",
    "HotspotFilter",
    "RSSAdapter", "APIAdapter", "CrawlerAdapter"
]
```

- [ ] **步骤10：创建适配器初始化**

```python
# src/hotspot/adapters/__init__.py
from .base import BaseAdapter
from .rss_adapter import RSSAdapter
from .api_adapter import APIAdapter
from .crawler_adapter import CrawlerAdapter

__all__ = [
    "BaseAdapter",
    "RSSAdapter",
    "APIAdapter",
    "CrawlerAdapter"
]
```

- [ ] **步骤11：提交热点监控模块代码**

```bash
git add src/hotspot/ src/api/hotspot.py
git commit -m "feat: 添加热点监控模块"
```