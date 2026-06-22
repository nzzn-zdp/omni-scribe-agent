import httpx
from typing import Dict, Any
from .base import BasePlatformAdapter


class WordPressAdapter(BasePlatformAdapter):
    """WordPress适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到WordPress"""
        site_url = config.get("site_url")
        username = config.get("username")
        password = config.get("password")
        
        async with httpx.AsyncClient() as client:
            # 创建文章
            post_data = {
                "title": content.get("title"),
                "content": content.get("content"),
                "status": "publish"
            }
            
            response = await client.post(
                f"{site_url}/wp-json/wp/v2/posts",
                json=post_data,
                auth=(username, password)
            )
            result = response.json()
            
            if "id" in result:
                return {
                    "post_id": str(result.get("id")),
                    "status": "published",
                    "platform": "wordpress",
                    "url": result.get("link")
                }
            else:
                raise Exception(f"发布WordPress文章失败: {result}")
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证WordPress配置"""
        required_fields = ["site_url", "username", "password"]
        return all(field in config for field in required_fields)
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        site_url = config.get("site_url")
        username = config.get("username")
        password = config.get("password")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{site_url}/wp-json/wp/v2/posts/{post_id}",
                auth=(username, password)
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "post_id": post_id,
                    "status": "published" if result.get("status") == "publish" else "draft",
                    "platform": "wordpress",
                    "url": result.get("link")
                }
            else:
                return {
                    "post_id": post_id,
                    "status": "unknown",
                    "platform": "wordpress"
                }