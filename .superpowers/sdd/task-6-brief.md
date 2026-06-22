### 任务6：多平台发布模块

**Files:**
- Create: `src/publish/__init__.py`
- Create: `src/publish/dispatcher.py`
- Create: `src/publish/adapters/__init__.py`
- Create: `src/publish/adapters/base.py`
- Create: `src/publish/adapters/wechat_adapter.py`
- Create: `src/publish/adapters/weibo_adapter.py`
- Create: `src/publish/adapters/zhihu_adapter.py`
- Create: `src/publish/adapters/xiaohongshu_adapter.py`
- Create: `src/publish/adapters/wordpress_adapter.py`
- Create: `src/publish/adapters/custom_adapter.py`
- Create: `src/publish/formatter.py`
- Create: `src/publish/tracker.py`
- Create: `src/api/publish.py`

**Interfaces:**
- Consumes: 内容草稿事件，平台配置
- Produces: 发布记录，发布状态

- [ ] **步骤1：创建平台适配器接口**

```python
# src/publish/adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlatformAdapter(ABC):
    """平台适配器基类"""
    
    @abstractmethod
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布内容到平台"""
        pass
    
    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证平台配置"""
        pass
    
    @abstractmethod
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        pass
```

- [ ] **步骤2：创建微信公众号适配器**

```python
# src/publish/adapters/wechat_adapter.py
import httpx
from typing import Dict, Any, Optional
from .base import BasePlatformAdapter

class WechatAdapter(BasePlatformAdapter):
    """微信公众号适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到微信公众号"""
        access_token = await self._get_access_token(config)
        if not access_token:
            raise Exception("获取access_token失败")
        
        # 创建草稿
        draft_data = {
            "articles": [{
                "title": content.get("title"),
                "content": content.get("content"),
                "digest": content.get("summary"),
                "thumb_media_id": config.get("thumb_media_id")
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}",
                json=draft_data
            )
            result = response.json()
            
            if "media_id" in result:
                # 发布草稿
                publish_response = await client.post(
                    f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}",
                    json={"media_id": result["media_id"]}
                )
                publish_result = publish_response.json()
                
                return {
                    "post_id": publish_result.get("publish_id"),
                    "status": "published" if publish_result.get("errcode") == 0 else "failed",
                    "platform": "wechat"
                }
            else:
                raise Exception(f"创建草稿失败: {result}")
    
    async def _get_access_token(self, config: Dict[str, Any]) -> Optional[str]:
        """获取access_token"""
        app_id = config.get("app_id")
        app_secret = config.get("app_secret")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
            )
            result = response.json()
            return result.get("access_token")
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证微信配置"""
        return "app_id" in config and "app_secret" in config
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        access_token = await self._get_access_token(config)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={access_token}",
                json={"publish_id": post_id}
            )
            result = response.json()
            
            return {
                "post_id": post_id,
                "status": "published" if result.get("publish_status") == 0 else "failed",
                "platform": "wechat"
            }
```

- [ ] **步骤3：创建其他平台适配器**

```python
# src/publish/adapters/weibo_adapter.py
import httpx
from typing import Dict, Any
from .base import BasePlatformAdapter

class WeiboAdapter(BasePlatformAdapter):
    """微博适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到微博"""
        access_token = config.get("access_token")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.weibo.com/2/statuses/share.json",
                data={
                    "access_token": access_token,
                    "status": content.get("content")
                }
            )
            result = response.json()
            
            if "id" in result:
                return {
                    "post_id": str(result.get("id")),
                    "status": "published",
                    "platform": "weibo"
                }
            else:
                raise Exception(f"发布微博失败: {result}")
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证微博配置"""
        return "access_token" in config
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        # 微博API不提供直接的状态查询
        return {
            "post_id": post_id,
            "status": "unknown",
            "platform": "weibo"
        }
```

（其他适配器类似实现）

- [ ] **步骤4：创建内容格式转换器**

```python
# src/publish/formatter.py
from typing import Dict, Any
import re

class ContentFormatter:
    """内容格式转换器"""
    
    def format_for_platform(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """根据平台格式化内容"""
        formatters = {
            "wechat": self._format_for_wechat,
            "weibo": self._format_for_weibo,
            "zhihu": self._format_for_zhihu,
            "xiaohongshu": self._format_for_xiaohongshu,
            "wordpress": self._format_for_wordpress
        }
        
        formatter = formatters.get(platform, self._format_default)
        return formatter(content)
    
    def _format_for_wechat(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """微信公众号格式化"""
        title = content.get("title", "")
        body = content.get("content", "")
        
        # 微信标题限制
        if len(title) > 64:
            title = title[:61] + "..."
        
        # 微信内容格式化
        formatted_body = self._add_wechat_formatting(body)
        
        return {
            **content,
            "title": title,
            "content": formatted_body
        }
    
    def _format_for_weibo(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """微博格式化"""
        title = content.get("title", "")
        body = content.get("content", "")
        
        # 微博字数限制
        weibo_content = f"{title}\n\n{body}"
        if len(weibo_content) > 2000:
            weibo_content = weibo_content[:1997] + "..."
        
        return {
            **content,
            "content": weibo_content
        }
    
    def _format_for_zhihu(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """知乎格式化"""
        # 知乎支持Markdown
        return content
    
    def _format_for_xiaohongshu(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """小红书格式化"""
        title = content.get("title", "")
        body = content.get("content", "")
        
        # 小红书标题格式
        xhs_title = f"#{title}#"
        
        # 小红书内容格式化
        xhs_body = self._add_xiaohongshu_tags(body)
        
        return {
            **content,
            "title": xhs_title,
            "content": xhs_body
        }
    
    def _format_for_wordpress(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """WordPress格式化"""
        # WordPress支持HTML
        return content
    
    def _format_default(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """默认格式化"""
        return content
    
    def _add_wechat_formatting(self, content: str) -> str:
        """添加微信格式"""
        # 添加段落间距
        formatted = content.replace("\n\n", "</p><p>")
        formatted = f"<p>{formatted}</p>"
        return formatted
    
    def _add_xiaohongshu_tags(self, content: str) -> str:
        """添加小红书标签"""
        # 简单的标签提取
        words = content.split()
        tags = [f"#{word}" for word in words if len(word) >= 2 and word.isalnum()]
        return f"{content}\n\n{' '.join(tags[:5])}"
```

- [ ] **步骤5：创建发布调度器**

```python
# src/publish/dispatcher.py
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
                record.published_at = func.now()
                
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
```

- [ ] **步骤6：创建发布状态跟踪器**

```python
# src/publish/tracker.py
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
```

- [ ] **步骤7：创建发布API接口**

```python
# src/api/publish.py
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
```

- [ ] **步骤8：创建发布模块初始化**

```python
# src/publish/__init__.py
from .dispatcher import PublishDispatcher, publish_dispatcher
from .tracker import PublishTracker, publish_tracker
from .formatter import ContentFormatter
from .adapters import WechatAdapter, WeiboAdapter, ZhihuAdapter, XiaohongshuAdapter, WordPressAdapter

__all__ = [
    "PublishDispatcher", "publish_dispatcher",
    "PublishTracker", "publish_tracker",
    "ContentFormatter",
    "WechatAdapter", "WeiboAdapter", "ZhihuAdapter", "XiaohongshuAdapter", "WordPressAdapter"
]
```

- [ ] **步骤9：创建适配器初始化**

```python
# src/publish/adapters/__init__.py
from .base import BasePlatformAdapter
from .wechat_adapter import WechatAdapter
from .weibo_adapter import WeiboAdapter
from .zhihu_adapter import ZhihuAdapter
from .xiaohongshu_adapter import XiaohongshuAdapter
from .wordpress_adapter import WordPressAdapter
from .custom_adapter import CustomAdapter

__all__ = [
    "BasePlatformAdapter",
    "WechatAdapter",
    "WeiboAdapter",
    "ZhihuAdapter",
    "XiaohongshuAdapter",
    "WordPressAdapter",
    "CustomAdapter"
]
```

- [ ] **步骤10：提交多平台发布模块代码**

```bash
git add src/publish/ src/api/publish.py
git commit -m "feat: 添加多平台发布模块"
```