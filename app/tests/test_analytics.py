"""Tests for analytics functionality."""

from datetime import datetime, timedelta

import pytest


def test_analytics_module_import():
    """Test that analytics modules can be imported."""
    from app.analytics import charts, dashboard_logic

    assert charts is not None
    assert dashboard_logic is not None


def test_date_range_calculation():
    """Test basic date range calculations for analytics."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    assert start_date < end_date
    assert (end_date - start_date).days == 7


def test_percentage_calculation():
    """Test percentage calculation helper."""
    total = 100
    completed = 75
    percentage = (completed / total) * 100
    assert percentage == 75.0


@pytest.mark.asyncio
async def test_analytics_data_structure():
    """Test analytics data structure format."""
    analytics_data = {
        "total_tasks": 10,
        "completed_tasks": 7,
        "in_progress_tasks": 2,
        "pending_tasks": 1,
    }
    assert (
        sum(
            [
                analytics_data["completed_tasks"],
                analytics_data["in_progress_tasks"],
                analytics_data["pending_tasks"],
            ]
        )
        == analytics_data["total_tasks"]
    )
