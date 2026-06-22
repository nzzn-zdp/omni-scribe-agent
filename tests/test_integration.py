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