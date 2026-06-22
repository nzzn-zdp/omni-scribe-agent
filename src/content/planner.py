from typing import Dict, Any, List
import json

class ContentPlanner:
    """内容策划器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    async def plan(self, hotspot: Dict[str, Any]) -> Dict[str, Any]:
        """策划内容"""
        prompt = f"""
        基于以下热点话题，策划一篇内容：
        
        标题：{hotspot.get('title', '')}
        内容：{hotspot.get('content', '')}
        推荐角度：{hotspot.get('angles', [])}
        
        请提供：
        1. 内容标题（吸引眼球）
        2. 内容大纲（3-5个要点）
        3. 目标受众
        4. 写作风格
        5. 预计字数
        
        请以JSON格式返回。
        """
        
        if self.llm_client:
            try:
                response = await self.llm_client.generate(prompt)
                return json.loads(response)
            except Exception as e:
                print(f"LLM策划失败: {e}")
        
        # 默认策划逻辑
        title = hotspot.get("title", "")
        
        return {
            "title": f"深度解析：{title}",
            "outline": [
                "事件背景介绍",
                "核心要点分析",
                "影响和意义",
                "未来展望"
            ],
            "target_audience": "关注该话题的读者",
            "writing_style": "专业、客观、深入",
            "word_count": 1500
        }