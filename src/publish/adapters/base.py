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