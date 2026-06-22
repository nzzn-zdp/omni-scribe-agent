from typing import Dict, Any, List
import re


class HotspotFilter:
    """热点过滤器"""
    
    def __init__(self):
        self.sensitive_words = ["敏感词1", "敏感词2"]  # 可配置
        self.min_score = 0.6
    
    async def filter(self, hotspots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤热点列表
        
        Args:
            hotspots: 热点数据列表
            
        Returns:
            过滤后的热点列表
        """
        filtered = []
        
        for hotspot in hotspots:
            # 检查评分
            if hotspot.get("score", 0) < self.min_score:
                continue
            
            # 检查敏感词
            if self._contains_sensitive_words(hotspot.get("title", "")):
                continue
            
            # 检查内容质量
            if not self._is_quality_content(hotspot):
                continue
            
            filtered.append(hotspot)
        
        return filtered
    
    def _contains_sensitive_words(self, text: str) -> bool:
        """检查是否包含敏感词
        
        Args:
            text: 待检查文本
            
        Returns:
            是否包含敏感词
        """
        for word in self.sensitive_words:
            if word in text:
                return True
        return False
    
    def _is_quality_content(self, hotspot: Dict[str, Any]) -> bool:
        """检查内容质量
        
        Args:
            hotspot: 热点数据字典
            
        Returns:
            内容质量是否合格
        """
        title = hotspot.get("title", "")
        content = hotspot.get("content", "")
        
        # 标题长度检查
        if len(title) < 5:
            return False
        
        # 内容长度检查
        if len(content) < 20:
            return False
        
        return True