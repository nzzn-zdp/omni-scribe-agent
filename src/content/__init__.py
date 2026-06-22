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