from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAdapter(ABC):
    """热点源适配器基类"""
    
    @abstractmethod
    async def fetch_hotspots(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取热点列表
        
        Args:
            config: 适配器配置
            
        Returns:
            热点数据列表，每个热点包含title、content、url等字段
        """
        pass
    
    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效
        
        Args:
            config: 适配器配置
            
        Returns:
            配置是否有效
        """
        pass