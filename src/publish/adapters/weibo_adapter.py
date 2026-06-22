import httpx
from typing import Dict, Any
from .base import BasePlatformAdapter


class WeiboAdapter(BasePlatformAdapter):
    """微博适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到微博"""
        access_token = config.get("access_token")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.weibo.com/2/statuses/share.json",
                data={
                    "access_token": access_token,
                    "status": content.get("content")
                }
            )
            result = response.json()
            
            if "id" in result:
                return {
                    "post_id": str(result.get("id")),
                    "status": "published",
                    "platform": "weibo"
                }
            else:
                raise Exception(f"发布微博失败: {result}")
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证微博配置"""
        return "access_token" in config
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        # 微博API不提供直接的状态查询
        return {
            "post_id": post_id,
            "status": "unknown",
            "platform": "weibo"
        }