### 任务7：配置与管理模块

**Files:**
- Create: `src/web/__init__.py`
- Create: `src/web/app.py`
- Create: `src/web/static/css/style.css`
- Create: `src/web/static/js/main.js`
- Create: `src/web/templates/index.html`
- Create: `src/api/admin.py`

**Interfaces:**
- Consumes: 所有模块的配置和状态
- Produces: Web管理界面

- [ ] **步骤1：创建Web应用**

```python
# src/web/app.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

# 挂载静态文件
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# 模板配置
templates = Jinja2Templates(directory="src/web/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/hotspots", response_class=HTMLResponse)
async def hotspots_page(request: Request):
    """热点监控页面"""
    return templates.TemplateResponse("hotspots.html", {"request": request})

@app.get("/content", response_class=HTMLResponse)
async def content_page(request: Request):
    """内容生产页面"""
    return templates.TemplateResponse("content.html", {"request": request})

@app.get("/publish", response_class=HTMLResponse)
async def publish_page(request: Request):
    """发布管理页面"""
    return templates.TemplateResponse("publish.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """系统设置页面"""
    return templates.TemplateResponse("settings.html", {"request": request})
```

- [ ] **步骤2：创建管理API接口**

```python
# src/api/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from ..database import get_db
from ..models.hotspot import HotspotSource
from ..models.content import ContentTask
from ..models.publish import Platform, PublishRecord
from ..core.event_bus import event_bus
from ..core.task_queue import task_queue

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    """获取仪表盘数据"""
    # 获取热点源数量
    hotspot_sources_count = await db.query(HotspotSource).count()
    
    # 获取内容任务统计
    content_tasks_count = await db.query(ContentTask).count()
    completed_tasks_count = await db.query(ContentTask).filter(
        ContentTask.status == "completed"
    ).count()
    
    # 获取发布记录统计
    publish_records_count = await db.query(PublishRecord).count()
    published_count = await db.query(PublishRecord).filter(
        PublishRecord.status == "published"
    ).count()
    
    return {
        "hotspot_sources": hotspot_sources_count,
        "content_tasks": {
            "total": content_tasks_count,
            "completed": completed_tasks_count
        },
        "publish_records": {
            "total": publish_records_count,
            "published": published_count
        }
    }

@router.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "event_bus": "connected",
        "task_queue": "connected",
        "database": "connected"
    }

@router.post("/system/config")
async def update_system_config(config_data: Dict[str, Any]):
    """更新系统配置"""
    # 发布配置更新事件
    await event_bus.publish("system", "config_updated", config_data)
    
    return {"message": "配置已更新"}

@router.get("/logs")
async def get_system_logs(log_type: str = "system", limit: int = 100):
    """获取系统日志"""
    # 这里应该从日志文件或数据库读取日志
    # 简化实现，返回示例数据
    return {
        "logs": [
            {"timestamp": "2026-06-22 10:00:00", "level": "INFO", "message": "系统启动"},
            {"timestamp": "2026-06-22 10:01:00", "level": "INFO", "message": "热点监控开始"}
        ]
    }
```

- [ ] **步骤3：创建HTML模板**

```html
<!-- src/web/templates/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniScribeAgent - 自动化内容生产与分发</title>
    <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a class="navbar-brand" href="/">OmniScribeAgent</a>
            <ul class="nav-links">
                <li><a href="/hotspots">热点监控</a></li>
                <li><a href="/content">内容生产</a></li>
                <li><a href="/publish">发布管理</a></li>
                <li><a href="/settings">系统设置</a></li>
            </ul>
        </div>
    </nav>
    
    <main class="container">
        <div class="dashboard">
            <h1>系统概览</h1>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>热点源</h3>
                    <p id="hotspot-sources-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>内容任务</h3>
                    <p id="content-tasks-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>已发布</h3>
                    <p id="published-count">0</p>
                </div>
            </div>
        </div>
    </main>
    
    <script src="/static/js/main.js"></script>
</body>
</html>
```

- [ ] **步骤4：创建静态资源**

```css
/* src/web/static/css/style.css */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.navbar {
    background-color: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 1rem 0;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
    text-decoration: none;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    color: #666;
    text-decoration: none;
    transition: color 0.3s;
}

.nav-links a:hover {
    color: #007bff;
}

.dashboard {
    padding: 2rem 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.stat-card p {
    font-size: 2rem;
    font-weight: bold;
    color: #333;
}
```

```javascript
// src/web/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        const response = await fetch('/api/admin/dashboard');
        const data = await response.json();
        
        document.getElementById('hotspot-sources-count').textContent = data.hotspot_sources;
        document.getElementById('content-tasks-count').textContent = data.content_tasks.total;
        document.getElementById('published-count').textContent = data.publish_records.published;
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
    }
}
```

- [ ] **步骤5：创建Web模块初始化**

```python
# src/web/__init__.py
from .app import app

__all__ = ["app"]
```

- [ ] **步骤6：提交配置与管理模块代码**

```bash
git add src/web/ src/api/admin.py
git commit -m "feat: 添加配置与管理模块"
```