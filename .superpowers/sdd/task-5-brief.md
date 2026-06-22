### 任务5：内容生产模块

**Files:**
- Create: `src/content/__init__.py`
- Create: `src/content/planner.py`
- Create: `src/content/generator.py`
- Create: `src/content/optimizer.py`
- Create: `src/content/reviewer.py`
- Create: `src/api/content.py`

**Interfaces:**
- Consumes: 热点事件，LLM接口
- Produces: 内容草稿，供发布模块使用

- [ ] **步骤1：创建内容策划器**

```python
# src/content/planner.py
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
```

- [ ] **步骤2：创建内容生成器**

```python
# src/content/generator.py
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
```

- [ ] **步骤3：创建内容优化器**

```python
# src/content/optimizer.py
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
```

- [ ] **步骤4：创建内容审核器**

```python
# src/content/reviewer.py
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
```

- [ ] **步骤5：创建内容生产管道**

```python
# src/content/__init__.py
import json
from typing import Dict, Any, List
from .planner import ContentPlanner
from .generator import ContentGenerator
from .optimizer import ContentOptimizer
from .reviewer import ContentReviewer
from ..core.event_bus import event_bus
from ..core.task_queue import task_queue
from ..models.content import ContentTask, ContentDraft
from ..database import get_db

class ContentPipeline:
    """内容生产管道"""
    
    def __init__(self, llm_client=None):
        self.planner = ContentPlanner(llm_client)
        self.generator = ContentGenerator(llm_client)
        self.optimizer = ContentOptimizer(llm_client)
        self.reviewer = ContentReviewer(llm_client)
    
    async def process_hotspot(self, hotspot_data: Dict[str, Any]):
        """处理热点，生成内容"""
        # 创建内容任务
        async with get_db() as db:
            task = ContentTask(
                hotspot_id=hotspot_data.get("hotspot_id"),
                content_type="article",
                status="planning"
            )
            db.add(task)
            await db.commit()
            await db.refresh(task)
            
            try:
                # 1. 内容策划
                plan = await self.planner.plan(hotspot_data)
                
                # 更新任务状态
                task.status = "generating"
                await db.commit()
                
                # 2. 内容生成
                content = await self.generator.generate(plan, hotspot_data)
                
                # 更新任务状态
                task.status = "optimizing"
                await db.commit()
                
                # 3. 内容优化
                optimized_content = await self.optimizer.optimize(content)
                
                # 更新任务状态
                task.status = "reviewing"
                await db.commit()
                
                # 4. 内容审核
                reviewed_content = await self.reviewer.review(optimized_content)
                
                # 保存内容草稿
                draft = ContentDraft(
                    task_id=task.id,
                    title=reviewed_content.get("title"),
                    content=reviewed_content.get("content"),
                    summary=reviewed_content.get("summary"),
                    keywords=json.dumps(self._extract_keywords(reviewed_content)),
                    seo_score=reviewed_content.get("seo_score", 0),
                    readability_score=reviewed_content.get("readability_score", 0)
                )
                db.add(draft)
                
                # 更新任务状态
                task.status = "completed"
                await db.commit()
                
                # 发布内容生成完成事件
                await event_bus.publish("content", "content_generated", {
                    "task_id": task.id,
                    "draft_id": draft.id,
                    "title": draft.title
                })
                
            except Exception as e:
                # 更新任务状态为失败
                task.status = "failed"
                await db.commit()
                
                # 发布内容生成失败事件
                await event_bus.publish("content", "content_generation_failed", {
                    "task_id": task.id,
                    "error": str(e)
                })
                
                raise e
    
    def _extract_keywords(self, content: Dict[str, Any]) -> List[str]:
        """提取关键词"""
        title = content.get("title", "")
        # 简单的关键词提取
        words = title.split()
        return [w for w in words if len(w) >= 2]

# 全局内容生产管道实例
content_pipeline = ContentPipeline()
```

- [ ] **步骤6：创建内容API接口**

```python
# src/api/content.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from ..database import get_db
from ..models.content import ContentTask, ContentDraft
from ..core.event_bus import event_bus

router = APIRouter()

@router.get("/tasks/", response_model=List[Dict[str, Any]])
async def get_content_tasks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取内容任务列表"""
    tasks = await db.query(ContentTask).offset(skip).limit(limit).all()
    return [
        {
            "id": t.id,
            "hotspot_id": t.hotspot_id,
            "content_type": t.content_type,
            "status": t.status,
            "created_at": t.created_at
        }
        for t in tasks
    ]

@router.get("/drafts/", response_model=List[Dict[str, Any]])
async def get_content_drafts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取内容草稿列表"""
    drafts = await db.query(ContentDraft).offset(skip).limit(limit).all()
    return [
        {
            "id": d.id,
            "task_id": d.task_id,
            "title": d.title,
            "content": d.content[:200] + "..." if len(d.content) > 200 else d.content,
            "summary": d.summary,
            "seo_score": d.seo_score,
            "readability_score": d.readability_score,
            "created_at": d.created_at
        }
        for d in drafts
    ]

@router.post("/generate/{hotspot_id}")
async def generate_content(hotspot_id: int, db: AsyncSession = Depends(get_db)):
    """生成内容"""
    # 发布内容生成请求事件
    await event_bus.publish("content", "content_generation_requested", {
        "hotspot_id": hotspot_id
    })
    
    return {"message": "内容生成请求已提交"}
```

- [ ] **步骤7：提交内容生产模块代码**

```bash
git add src/content/ src/api/content.py
git commit -m "feat: 添加内容生产模块"
```