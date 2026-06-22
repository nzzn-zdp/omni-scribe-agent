import httpx
from typing import Dict, Any
from .base import BasePlatformAdapter


class CustomAdapter(BasePlatformAdapter):
    """自定义平台适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到自定义平台"""
        api_url = config.get("api_url")
        headers = config.get("headers", {})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                json=content,
                headers=headers
            )
            result = response.json()
            
            return {
                "post_id": result.get("id", "unknown"),
                "status": "published" if response.status_code == 200 else "failed",
                "platform": "custom",
                "raw_response": result
            }
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证自定义平台配置"""
        return "api_url" in config
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        status_url = config.get("status_url")
        if not status_url:
            return {
                "post_id": post_id,
                "status": "unknown",
                "platform": "custom"
            }
        
        headers = config.get("headers", {})
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{status_url}/{post_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "post_id": post_id,
                    "status": result.get("status", "unknown"),
                    "platform": "custom"
                }
            else:
                return {
                    "post_id": post_id,
                    "status": "unknown",
                    "platform": "custom"
                }