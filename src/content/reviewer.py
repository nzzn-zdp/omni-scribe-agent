from typing import Dict, Any, List
import re

class ContentReviewer:
    """内容审核器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.sensitive_words = ["敏感词1", "敏感词2"]  # 可配置
    
    async def review(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """审核内容"""
        # 质量检查
        quality_score = await self._check_quality(content)
        
        # 合规性检查
        compliance_score = await self._check_compliance(content)
        
        # 原创性检查
        originality_score = await self._check_originality(content)
        
        # 计算总分
        total_score = (quality_score + compliance_score + originality_score) / 3
        
        return {
            **content,
            "quality_score": quality_score,
            "compliance_score": compliance_score,
            "originality_score": originality_score,
            "review_score": total_score,
            "review_passed": total_score >= 0.7
        }
    
    async def _check_quality(self, content: Dict[str, Any]) -> float:
        """质量检查"""
        body = content.get("content", "")
        
        score = 0.0
        
        # 内容长度检查
        if len(body) >= 500:
            score += 0.3
        
        # 语法检查（简单实现）
        if not self._has_grammar_errors(body):
            score += 0.3
        
        # 逻辑连贯性检查
        if self._is_coherent(body):
            score += 0.4
        
        return min(score, 1.0)
    
    async def _check_compliance(self, content: Dict[str, Any]) -> float:
        """合规性检查"""
        body = content.get("content", "")
        title = content.get("title", "")
        
        score = 1.0
        
        # 敏感词检查
        for word in self.sensitive_words:
            if word in body or word in title:
                score -= 0.3
        
        # 版权检查（简单实现）
        if self._has_copyright_issues(body):
            score -= 0.5
        
        return max(score, 0.0)
    
    async def _check_originality(self, content: Dict[str, Any]) -> float:
        """原创性检查"""
        # 简单的原创性检查
        # 实际应用中应该使用专业的查重服务
        return 0.8
    
    def _has_grammar_errors(self, text: str) -> bool:
        """检查语法错误"""
        # 简单的语法检查
        return False
    
    def _is_coherent(self, text: str) -> bool:
        """检查逻辑连贯性"""
        # 简单的连贯性检查
        paragraphs = text.split("\n\n")
        return len(paragraphs) >= 2
    
    def _has_copyright_issues(self, text: str) -> bool:
        """检查版权问题"""
        # 简单的版权检查
        return False