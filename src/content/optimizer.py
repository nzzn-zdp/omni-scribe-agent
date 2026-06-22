from typing import Dict, Any, List
import re

class ContentOptimizer:
    """内容优化器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    async def optimize(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """优化内容"""
        # SEO优化
        seo_score = await self._optimize_seo(content)
        
        # 可读性优化
        readability_score = await self._optimize_readability(content)
        
        # 格式优化
        formatted_content = await self._format_content(content)
        
        return {
            **formatted_content,
            "seo_score": seo_score,
            "readability_score": readability_score
        }
    
    async def _optimize_seo(self, content: Dict[str, Any]) -> float:
        """SEO优化"""
        title = content.get("title", "")
        body = content.get("content", "")
        
        score = 0.0
        
        # 标题长度检查
        if 10 <= len(title) <= 60:
            score += 0.3
        
        # 关键词密度检查
        keywords = self._extract_keywords(title)
        if keywords:
            density = self._calculate_keyword_density(body, keywords)
            if 0.01 <= density <= 0.03:
                score += 0.4
        
        # 内容长度检查
        if len(body) >= 500:
            score += 0.3
        
        return min(score, 1.0)
    
    async def _optimize_readability(self, content: Dict[str, Any]) -> float:
        """可读性优化"""
        body = content.get("content", "")
        
        score = 0.0
        
        # 段落长度检查
        paragraphs = body.split("\n\n")
        avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        if 50 <= avg_paragraph_length <= 200:
            score += 0.4
        
        # 句子长度检查
        sentences = re.split(r'[。！？.!?]', body)
        sentences = [s for s in sentences if s.strip()]
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        
        if 10 <= avg_sentence_length <= 50:
            score += 0.4
        
        # 标题层级检查
        if "#" in body:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _format_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """格式化内容"""
        body = content.get("content", "")
        
        # 添加适当的换行
        formatted = body.replace("\n", "\n\n")
        
        # 清理多余的空行
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)
        
        return {
            **content,
            "content": formatted
        }
    
    def _extract_keywords(self, title: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        words = title.split()
        return [w for w in words if len(w) >= 2]
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> float:
        """计算关键词密度"""
        if not content or not keywords:
            return 0.0
        
        total_words = len(content)
        keyword_count = sum(content.count(kw) for kw in keywords)
        
        return keyword_count / total_words if total_words > 0 else 0.0