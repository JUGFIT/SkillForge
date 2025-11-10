"""Pytest configuration and shared fixtures."""

import asyncio
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user_id():
    """Provide a mock user ID for testing."""
    return 1


@pytest.fixture
def mock_project_id():
    """Provide a mock project ID for testing."""
    return 1


@pytest.fixture
def mock_task_id():
    """Provide a mock task ID for testing."""
    return 1


@pytest.fixture
def sample_task_data():
    """Provide sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium",
        "assignee_id": 1,
        "project_id": 1,
    }


@pytest.fixture
def sample_project_data():
    """Provide sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "This is a test project",
        "status": "active",
        "owner_id": 1,
    }


@pytest.fixture
def sample_comment_data():
    """Provide sample comment data for testing."""
    return {
        "content": "This is a test comment",
        "author_id": 1,
        "task_id": 1,
    }


@pytest.fixture
def sample_notification_data():
    """Provide sample notification data for testing."""
    return {
        "user_id": 1,
        "type": "task_assigned",
        "message": "You have been assigned a new task",
        "is_read": False,
    }
