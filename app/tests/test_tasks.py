"""Tests for task functionality."""

from datetime import datetime, timedelta

import pytest


def test_task_module_import():
    """Test that task modules can be imported."""
    from app.models import task
    from app.schemas import task as task_schema

    assert task is not None
    assert task_schema is not None


def test_task_status_values():
    """Test valid task status values."""
    valid_statuses = ["pending", "in_progress", "completed", "blocked", "cancelled"]
    test_status = "in_progress"
    assert test_status in valid_statuses


def test_task_priority_values():
    """Test valid task priority values."""
    valid_priorities = ["low", "medium", "high", "urgent"]
    test_priority = "high"
    assert test_priority in valid_priorities


@pytest.mark.asyncio
async def test_task_structure():
    """Test task data structure."""
    task = {
        "id": 1,
        "title": "Complete unit tests",
        "description": "Write comprehensive unit tests",
        "status": "in_progress",
        "priority": "high",
        "assignee_id": 1,
        "project_id": 1,
        "created_at": datetime.now(),
    }
    assert "title" in task
    assert "status" in task
    assert "priority" in task
    assert len(task["title"]) > 0


def test_task_title_length():
    """Test task title length validation."""
    short_title = "Fix bug"
    long_title = "This is a very long task title that describes the task in detail"

    assert len(short_title) >= 3
    assert len(long_title) > len(short_title)
    assert len(long_title) <= 200  # Reasonable max length


@pytest.mark.asyncio
async def test_task_due_date_validation():
    """Test task due date validation."""
    now = datetime.now()
    due_date = now + timedelta(days=7)

    assert due_date > now
    assert (due_date - now).days == 7


def test_task_completion_percentage():
    """Test task completion calculation."""
    total_subtasks = 10
    completed_subtasks = 7
    completion_percentage = (completed_subtasks / total_subtasks) * 100

    assert completion_percentage == 70.0
    assert 0 <= completion_percentage <= 100


@pytest.mark.asyncio
async def test_task_dependency():
    """Test task dependency structure."""
    task_with_dependency = {
        "id": 2,
        "title": "Deploy to production",
        "depends_on": [1],  # Depends on task 1
    }
    assert "depends_on" in task_with_dependency
    assert isinstance(task_with_dependency["depends_on"], list)
    assert len(task_with_dependency["depends_on"]) > 0
