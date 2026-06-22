import httpx
from typing import Dict, Any
from .base import BasePlatformAdapter


class ZhihuAdapter(BasePlatformAdapter):
    """知乎适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到知乎"""
        access_token = config.get("access_token")
        
        async with httpx.AsyncClient() as client:
            # 创建文章
            article_data = {
                "title": content.get("title"),
                "content": content.get("content"),
                "delta_time": 0
            }
            
            response = await client.post(
                "https://www.zhihu.com/api/v4/articles",
                json=article_data,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            result = response.json()
            
            if "id" in result:
                return {
                    "post_id": str(result.get("id")),
                    "status": "published",
                    "platform": "zhihu",
                    "url": result.get("url")
                }
            else:
                raise Exception(f"发布知乎文章失败: {result}")
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证知乎配置"""
        return "access_token" in config
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        access_token = config.get("access_token")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.zhihu.com/api/v4/articles/{post_id}",
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            if response.status_code == 200:
                return {
                    "post_id": post_id,
                    "status": "published",
                    "platform": "zhihu"
                }
            else:
                return {
                    "post_id": post_id,
                    "status": "unknown",
                    "platform": "zhihu"
                }