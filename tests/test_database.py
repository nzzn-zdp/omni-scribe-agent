import pytest
from src.database import engine, async_session, Base, init_db

def test_engine_creation():
    assert engine is not None

def test_session_maker():
    assert async_session is not None

def test_base_class():
    assert hasattr(Base, 'metadata')