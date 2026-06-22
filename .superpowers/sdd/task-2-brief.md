### 任务2：数据模型定义

**Files:**
- Create: `src/models/__init__.py`
- Create: `src/models/hotspot.py`
- Create: `src/models/content.py`
- Create: `src/models/publish.py`
- Create: `src/models/platform.py`

**Interfaces:**
- Consumes: 数据库连接（来自任务1）
- Produces: 数据模型，供其他模块使用

- [ ] **步骤1：创建热点数据模型**

```python
# src/models/hotspot.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from ..database import Base

class HotspotSource(Base):
    """热点源配置表"""
    __tablename__ = "hotspot_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # rss, api, crawler
    config = Column(Text, nullable=False)  # JSON格式配置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Hotspot(Base):
    """热点数据表"""
    __tablename__ = "hotspots"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("hotspot_sources.id"))
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000))
    score = Column(Float, default=0.0)  # 热点评分
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
```

- [ ] **步骤2：创建内容数据模型**

```python
# src/models/content.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class ContentTask(Base):
    """内容任务表"""
    __tablename__ = "content_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"))
    content_type = Column(String(50), nullable=False)  # article, post
    status = Column(String(50), default="pending")  # pending, planning, generating, optimizing, reviewing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContentDraft(Base):
    """内容草稿表"""
    __tablename__ = "content_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("content_tasks.id"))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    keywords = Column(Text)  # JSON格式关键词列表
    seo_score = Column(Float, default=0.0)
    readability_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **步骤3：创建发布数据模型**

```python
# src/models/publish.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Platform(Base):
    """平台配置表"""
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    platform_type = Column(String(50), nullable=False)  # wechat, weibo, zhihu, etc.
    config = Column(Text, nullable=False)  # JSON格式配置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PublishRecord(Base):
    """发布记录表"""
    __tablename__ = "publish_records"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("content_drafts.id"))
    platform_id = Column(Integer, ForeignKey("platforms.id"))
    status = Column(String(50), default="pending")  # pending, publishing, published, failed
    platform_post_id = Column(String(200))  # 平台返回的帖子ID
    platform_url = Column(String(1000))  # 平台帖子链接
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **步骤4：创建模型索引和关系**

```python
# src/models/__init__.py
from .hotspot import HotspotSource, Hotspot
from .content import ContentTask, ContentDraft
from .publish import Platform, PublishRecord

__all__ = [
    "HotspotSource", "Hotspot",
    "ContentTask", "ContentDraft",
    "Platform", "PublishRecord"
]
```

- [ ] **步骤5：运行模型测试**

```bash
pytest tests/test_models.py -v
```

- [ ] **步骤6：提交数据模型代码**

```bash
git add src/models/
git commit -m "feat: 添加数据模型定义"
```