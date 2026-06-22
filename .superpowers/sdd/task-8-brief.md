### 任务8：系统集成测试

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_integration.py`

**Interfaces:**
- Consumes: 所有模块
- Produces: 集成测试报告

- [ ] **步骤1：创建测试配置**

```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.database import Base, get_db
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(engine):
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client():
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

- [ ] **步骤2：创建集成测试**

```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_hotspot_workflow(client: AsyncClient):
    """测试热点监控工作流"""
    # 创建热点源
    source_data = {
        "name": "测试热点源",
        "source_type": "rss",
        "config": {"url": "https://example.com/rss"}
    }
    
    response = await client.post("/api/hotspots/sources/", json=source_data)
    assert response.status_code == 200
    source = response.json()
    assert source["name"] == "测试热点源"

@pytest.mark.asyncio
async def test_content_generation(client: AsyncClient):
    """测试内容生成工作流"""
    # 假设已有热点ID
    hotspot_id = 1
    
    response = await client.post(f"/api/content/generate/{hotspot_id}")
    assert response.status_code == 200
    assert "内容生成请求已提交" in response.json()["message"]

@pytest.mark.asyncio
async def test_publish_workflow(client: AsyncClient):
    """测试发布工作流"""
    # 假设已有草稿ID
    draft_id = 1
    platforms = ["wechat", "weibo"]
    
    response = await client.post(f"/api/publish/publish/{draft_id}", json=platforms)
    assert response.status_code == 200
    assert "发布请求已提交" in response.json()["message"]

@pytest.mark.asyncio
async def test_system_health(client: AsyncClient):
    """测试系统健康检查"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

- [ ] **步骤3：提交集成测试代码**

```bash
git add tests/
git commit -m "test: 添加集成测试"
```