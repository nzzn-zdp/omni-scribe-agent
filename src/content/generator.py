from typing import Dict, Any, List
import json

class ContentGenerator:
    """内容生成器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    async def generate(self, plan: Dict[str, Any], hotspot: Dict[str, Any]) -> Dict[str, Any]:
        """生成内容"""
        prompt = f"""
        根据以下策划和热点信息，生成一篇完整内容：
        
        标题：{plan.get('title', '')}
        大纲：{json.dumps(plan.get('outline', []), ensure_ascii=False)}
        目标受众：{plan.get('target_audience', '')}
        写作风格：{plan.get('writing_style', '')}
        预计字数：{plan.get('word_count', 1000)}
        
        热点信息：
        标题：{hotspot.get('title', '')}
        内容：{hotspot.get('content', '')}
        
        请生成一篇高质量的内容，包括：
        1. 引人入胜的开头
        2. 有深度的分析
        3. 清晰的结论
        4. 总结摘要
        
        请以JSON格式返回，包含title、content、summary字段。
        """
        
        if self.llm_client:
            try:
                response = await self.llm_client.generate(prompt)
                return json.loads(response)
            except Exception as e:
                print(f"LLM生成失败: {e}")
        
        # 默认生成逻辑
        title = plan.get("title", "")
        outline = plan.get("outline", [])
        
        content = f"# {title}\n\n"
        for i, point in enumerate(outline, 1):
            content += f"## {i}. {point}\n\n"
            content += f"这里是关于{point}的详细内容...\n\n"
        
        content += "## 总结\n\n"
        content += "以上是对该话题的全面分析。"
        
        return {
            "title": title,
            "content": content,
            "summary": f"本文深入分析了{title}的相关内容。"
        }