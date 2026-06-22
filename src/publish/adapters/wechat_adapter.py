import httpx
from typing import Dict, Any, Optional
from .base import BasePlatformAdapter


class WechatAdapter(BasePlatformAdapter):
    """微信公众号适配器"""
    
    async def publish(self, content: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """发布到微信公众号"""
        access_token = await self._get_access_token(config)
        if not access_token:
            raise Exception("获取access_token失败")
        
        # 创建草稿
        draft_data = {
            "articles": [{
                "title": content.get("title"),
                "content": content.get("content"),
                "digest": content.get("summary"),
                "thumb_media_id": config.get("thumb_media_id")
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}",
                json=draft_data
            )
            result = response.json()
            
            if "media_id" in result:
                # 发布草稿
                publish_response = await client.post(
                    f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}",
                    json={"media_id": result["media_id"]}
                )
                publish_result = publish_response.json()
                
                return {
                    "post_id": publish_result.get("publish_id"),
                    "status": "published" if publish_result.get("errcode") == 0 else "failed",
                    "platform": "wechat"
                }
            else:
                raise Exception(f"创建草稿失败: {result}")
    
    async def _get_access_token(self, config: Dict[str, Any]) -> Optional[str]:
        """获取access_token"""
        app_id = config.get("app_id")
        app_secret = config.get("app_secret")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
            )
            result = response.json()
            return result.get("access_token")
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证微信配置"""
        return "app_id" in config and "app_secret" in config
    
    async def get_post_status(self, post_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取帖子状态"""
        access_token = await self._get_access_token(config)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={access_token}",
                json={"publish_id": post_id}
            )
            result = response.json()
            
            return {
                "post_id": post_id,
                "status": "published" if result.get("publish_status") == 0 else "failed",
                "platform": "wechat"
            }