import pytest
from src.models import (
    HotspotSource, Hotspot,
    ContentTask, ContentDraft,
    Platform, PublishRecord
)
from src.database import Base


def test_hotspot_source_model():
    assert HotspotSource.__tablename__ == "hotspot_sources"
    assert hasattr(HotspotSource, "id")
    assert hasattr(HotspotSource, "name")
    assert hasattr(HotspotSource, "source_type")
    assert hasattr(HotspotSource, "config")
    assert hasattr(HotspotSource, "is_active")
    assert hasattr(HotspotSource, "created_at")
    assert hasattr(HotspotSource, "updated_at")


def test_hotspot_model():
    assert Hotspot.__tablename__ == "hotspots"
    assert hasattr(Hotspot, "id")
    assert hasattr(Hotspot, "source_id")
    assert hasattr(Hotspot, "title")
    assert hasattr(Hotspot, "content")
    assert hasattr(Hotspot, "url")
    assert hasattr(Hotspot, "score")
    assert hasattr(Hotspot, "status")
    assert hasattr(Hotspot, "created_at")
    assert hasattr(Hotspot, "processed_at")


def test_content_task_model():
    assert ContentTask.__tablename__ == "content_tasks"
    assert hasattr(ContentTask, "id")
    assert hasattr(ContentTask, "hotspot_id")
    assert hasattr(ContentTask, "content_type")
    assert hasattr(ContentTask, "status")
    assert hasattr(ContentTask, "created_at")
    assert hasattr(ContentTask, "updated_at")


def test_content_draft_model():
    assert ContentDraft.__tablename__ == "content_drafts"
    assert hasattr(ContentDraft, "id")
    assert hasattr(ContentDraft, "task_id")
    assert hasattr(ContentDraft, "title")
    assert hasattr(ContentDraft, "content")
    assert hasattr(ContentDraft, "summary")
    assert hasattr(ContentDraft, "keywords")
    assert hasattr(ContentDraft, "seo_score")
    assert hasattr(ContentDraft, "readability_score")
    assert hasattr(ContentDraft, "created_at")


def test_platform_model():
    assert Platform.__tablename__ == "platforms"
    assert hasattr(Platform, "id")
    assert hasattr(Platform, "name")
    assert hasattr(Platform, "platform_type")
    assert hasattr(Platform, "config")
    assert hasattr(Platform, "is_active")
    assert hasattr(Platform, "created_at")
    assert hasattr(Platform, "updated_at")


def test_publish_record_model():
    assert PublishRecord.__tablename__ == "publish_records"
    assert hasattr(PublishRecord, "id")
    assert hasattr(PublishRecord, "draft_id")
    assert hasattr(PublishRecord, "platform_id")
    assert hasattr(PublishRecord, "status")
    assert hasattr(PublishRecord, "platform_post_id")
    assert hasattr(PublishRecord, "platform_url")
    assert hasattr(PublishRecord, "published_at")
    assert hasattr(PublishRecord, "created_at")


def test_models_registered_in_metadata():
    table_names = Base.metadata.tables.keys()
    assert "hotspot_sources" in table_names
    assert "hotspots" in table_names
    assert "content_tasks" in table_names
    assert "content_drafts" in table_names
    assert "platforms" in table_names
    assert "publish_records" in table_names


def test_foreign_key_relationships():
    hotspot_source_fk = Hotspot.__table__.columns["source_id"].foreign_keys
    assert len(hotspot_source_fk) == 1
    assert str(list(hotspot_source_fk)[0].target_fullname) == "hotspot_sources.id"

    hotspot_fk = ContentTask.__table__.columns["hotspot_id"].foreign_keys
    assert len(hotspot_fk) == 1
    assert str(list(hotspot_fk)[0].target_fullname) == "hotspots.id"

    task_fk = ContentDraft.__table__.columns["task_id"].foreign_keys
    assert len(task_fk) == 1
    assert str(list(task_fk)[0].target_fullname) == "content_tasks.id"

    draft_fk = PublishRecord.__table__.columns["draft_id"].foreign_keys
    assert len(draft_fk) == 1
    assert str(list(draft_fk)[0].target_fullname) == "content_drafts.id"

    platform_fk = PublishRecord.__table__.columns["platform_id"].foreign_keys
    assert len(platform_fk) == 1
    assert str(list(platform_fk)[0].target_fullname) == "platforms.id"
