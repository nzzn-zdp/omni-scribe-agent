import httpx
from typing import Dict, Any
from .base import BasePlatformAdapter


class XiaohongshuAdapter(BasePlatformAdapter):
    """小红书适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到小红书"""
        access_token = config.get("access_token")
        
        async with httpx.AsyncClient() as client:
            # 创建笔记
            note_data = {
                "title": content.get("title"),
                "content": content.get("content"),
                "type": "normal"
            }
            
            response = await client.post(
                "https://www.xiaohongshu.com/api/v1/notes",
                json=note_data,
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
                    "platform": "xiaohongshu"
                }
            else:
                raise Exception(f"发布小红书笔记失败: {result}")
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证小红书配置"""
        return "access_token" in config
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        # 小红书API不提供直接的状态查询
        return {
            "post_id": post_id,
            "status": "unknown",
            "platform": "xiaohongshu"
        }