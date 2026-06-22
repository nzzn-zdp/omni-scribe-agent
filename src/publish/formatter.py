from typing import Dict, Any
import re


class ContentFormatter:
    """内容格式转换器"""
    
    def format_for_platform(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """根据平台格式化内容"""
        formatters = {
            "wechat": self._format_for_wechat,
            "weibo": self._format_for_weibo,
            "zhihu": self._format_for_zhihu,
            "xiaohongshu": self._format_for_xiaohongshu,
            "wordpress": self._format_for_wordpress
        }
        
        formatter = formatters.get(platform, self._format_default)
        return formatter(content)
    
    def _format_for_wechat(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """微信公众号格式化"""
        title = content.get("title", "")
        body = content.get("content", "")
        
        # 微信标题限制
        if len(title) > 64:
            title = title[:61] + "..."
        
        # 微信内容格式化
        formatted_body = self._add_wechat_formatting(body)
        
        return {
            **content,
            "title": title,
            "content": formatted_body
        }
    
    def _format_for_weibo(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """微博格式化"""
        title = content.get("title", "")
        body = content.get("content", "")
        
        # 微博字数限制
        weibo_content = f"{title}\n\n{body}"
        if len(weibo_content) > 2000:
            weibo_content = weibo_content[:1997] + "..."
        
        return {
            **content,
            "content": weibo_content
        }
    
    def _format_for_zhihu(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """知乎格式化"""
        # 知乎支持Markdown
        return content
    
    def _format_for_xiaohongshu(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """小红书格式化"""
        title = content.get("title", "")
        body = content.get("content", "")
        
        # 小红书标题格式
        xhs_title = f"#{title}#"
        
        # 小红书内容格式化
        xhs_body = self._add_xiaohongshu_tags(body)
        
        return {
            **content,
            "title": xhs_title,
            "content": xhs_body
        }
    
    def _format_for_wordpress(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """WordPress格式化"""
        # WordPress支持HTML
        return content
    
    def _format_default(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """默认格式化"""
        return content
    
    def _add_wechat_formatting(self, content: str) -> str:
        """添加微信格式"""
        # 添加段落间距
        formatted = content.replace("\n\n", "</p><p>")
        formatted = f"<p>{formatted}</p>"
        return formatted
    
    def _add_xiaohongshu_tags(self, content: str) -> str:
        """添加小红书标签"""
        # 简单的标签提取
        words = content.split()
        tags = [f"#{word}" for word in words if len(word) >= 2 and word.isalnum()]
        return f"{content}\n\n{' '.join(tags[:5])}"