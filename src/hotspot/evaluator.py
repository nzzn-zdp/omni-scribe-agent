from typing import Dict, Any, List
import json


class HotspotEvaluator:
    """热点评估器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    async def evaluate(self, hotspot: Dict[str, Any]) -> Dict[str, Any]:
        """评估热点质量
        
        Args:
            hotspot: 热点数据字典
            
        Returns:
            评估结果，包含score、angles、evaluation等字段
        """
        # 使用LLM评估热点
        prompt = f"""
        请评估以下热点话题的质量和可写性：
        
        标题：{hotspot.get('title', '')}
        内容：{hotspot.get('content', '')}
        
        请从以下维度评分（0-1分）：
        1. 时效性：话题的新鲜程度
        2. 话题性：话题的讨论价值
        3. 相关性：与目标受众的相关程度
        4. 可写性：是否容易展开写作
        
        请以JSON格式返回评分和推荐内容角度。
        """
        
        if self.llm_client:
            try:
                response = await self.llm_client.generate(prompt)
                result = json.loads(response)
                return {
                    "score": result.get("score", 0.5),
                    "angles": result.get("angles", []),
                    "evaluation": result.get("evaluation", "")
                }
            except Exception as e:
                print(f"LLM评估失败: {e}")
        
        # 默认评估逻辑
        title = hotspot.get("title", "")
        content = hotspot.get("content", "")
        
        # 简单评分逻辑
        score = 0.5
        if len(title) > 10:
            score += 0.1
        if len(content) > 100:
            score += 0.1
        if "热点" in title or "热搜" in title:
            score += 0.2
        
        return {
            "score": min(score, 1.0),
            "angles": ["常规角度"],
            "evaluation": "基于规则评估"
        }