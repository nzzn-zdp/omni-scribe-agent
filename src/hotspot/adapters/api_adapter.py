import httpx
from typing import List, Dict, Any
from .base import BaseAdapter


class APIAdapter(BaseAdapter):
    """API热点源适配器"""
    
    async def fetch_hotspots(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取API热点
        
        Args:
            config: 配置字典，包含url、headers、method、field_mapping等字段
            
        Returns:
            热点数据列表
        """
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
        """验证API配置
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        return "url" in config