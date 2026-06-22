import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseAdapter


class CrawlerAdapter(BaseAdapter):
    """网页爬虫热点源适配器"""
    
    async def fetch_hotspots(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """爬取网页热点
        
        Args:
            config: 配置字典，包含url、selectors等字段
            
        Returns:
            热点数据列表
        """
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
        """验证爬虫配置
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        return "url" in config and "selectors" in config