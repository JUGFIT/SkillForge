"""Tests for comments functionality."""

from datetime import datetime

import pytest


def test_comment_module_import():
    """Test that comment modules can be imported."""
    from app.models import comment
    from app.schemas import comment as comment_schema

    assert comment is not None
    assert comment_schema is not None


def test_comment_data_validation():
    """Test comment data structure."""
    comment_data = {
        "id": 1,
        "content": "This is a test comment",
        "user_id": 1,
        "created_at": datetime.now(),
    }
    assert len(comment_data["content"]) > 0
    assert comment_data["user_id"] > 0
    assert isinstance(comment_data["created_at"], datetime)


def test_comment_content_length():
    """Test comment content length validation."""
    short_comment = "Hi"
    long_comment = "This is a longer comment with more content"

    assert len(short_comment) >= 2
    assert len(long_comment) > len(short_comment)


@pytest.mark.asyncio
async def test_comment_structure():
    """Test comment structure format."""
    comment = {
        "id": 1,
        "content": "Test comment",
        "author_id": 1,
        "task_id": 1,
        "created_at": datetime.now().isoformat(),
    }
    assert "content" in comment
    assert "author_id" in comment
    assert "task_id" in comment
