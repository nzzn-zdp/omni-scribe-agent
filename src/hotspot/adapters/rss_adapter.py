import feedparser
import httpx
from typing import List, Dict, Any
from .base import BaseAdapter


class RSSAdapter(BaseAdapter):
    """RSS热点源适配器"""
    
    async def fetch_hotspots(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取RSS热点
        
        Args:
            config: 配置字典，包含url字段
            
        Returns:
            热点数据列表
        """
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
        """验证RSS配置
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        return "url" in config