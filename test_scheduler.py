"""
Tests for PawPal+ scheduling logic.
Run with: pytest test_scheduler.py
"""

import pytest
from scheduler import Owner, Pet, Task, Scheduler, DailyPlan


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_tasks():
    return [
        Task("Morning walk",   30, "high"),
        Task("Feeding",        10, "high"),
        Task("Grooming",       20, "medium"),
        Task("Enrichment toy", 15, "medium"),
        Task("Nail trim",      10, "low"),
        Task("Bath",           40, "low"),
    ]


# ---------------------------------------------------------------------------
# Priority ordering
# ---------------------------------------------------------------------------

def test_high_priority_scheduled_before_low():
    tasks = [
        Task("Low task",  10, "low"),
        Task("High task", 10, "high"),
    ]
    plan = Scheduler().build_plan(tasks, available_minutes=60)
    titles = [st.task.title for st in plan.scheduled]
    assert titles.index("High task") < titles.index("Low task")


def test_medium_scheduled_before_low():
    tasks = [
        Task("Low task",    10, "low"),
        Task("Medium task", 10, "medium"),
    ]
    plan = Scheduler().build_plan(tasks, available_minutes=60)
    titles = [st.task.title for st in plan.scheduled]
    assert titles.index("Medium task") < titles.index("Low task")


# ---------------------------------------------------------------------------
# Time constraint
# ---------------------------------------------------------------------------

def test_task_exceeding_available_time_is_skipped():
    tasks = [Task("Long task", 60, "high")]
    plan = Scheduler().build_plan(tasks, available_minutes=30)
    assert len(plan.scheduled) == 0
    assert len(plan.skipped) == 1


def test_total_duration_never_exceeds_available_time():
    tasks = make_tasks()
    available = 60
    plan = Scheduler().build_plan(tasks, available_minutes=available)
    assert plan.total_minutes <= available


def test_all_tasks_fit_when_time_is_sufficient():
    tasks = [Task("Walk", 10, "high"), Task("Feed", 5, "medium")]
    plan = Scheduler().build_plan(tasks, available_minutes=60)
    assert len(plan.scheduled) == 2
    assert len(plan.skipped) == 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_task_list_returns_empty_plan():
    plan = Scheduler().build_plan([], available_minutes=120)
    assert plan.scheduled == []
    assert plan.skipped == []


def test_zero_available_time_skips_all_tasks():
    tasks = [Task("Walk", 10, "high")]
    plan = Scheduler().build_plan(tasks, available_minutes=0)
    assert len(plan.scheduled) == 0
    assert len(plan.skipped) == 1


def test_exact_fit_task_is_scheduled():
    tasks = [Task("Walk", 30, "high")]
    plan = Scheduler().build_plan(tasks, available_minutes=30)
    assert len(plan.scheduled) == 1


def test_skipped_tasks_contain_reason():
    tasks = [Task("Long task", 100, "high")]
    plan = Scheduler().build_plan(tasks, available_minutes=50)
    _, reason = plan.skipped[0]
    assert "Skipped" in reason


# ---------------------------------------------------------------------------
# Time slots
# ---------------------------------------------------------------------------

def test_scheduled_tasks_have_non_overlapping_slots():
    tasks = [
        Task("Task A", 20, "high"),
        Task("Task B", 15, "medium"),
    ]
    plan = Scheduler().build_plan(tasks, available_minutes=120)
    for i in range(len(plan.scheduled) - 1):
        assert plan.scheduled[i].end_minute <= plan.scheduled[i + 1].start_minute


def test_plan_starts_at_8am():
    tasks = [Task("Walk", 10, "high")]
    plan = Scheduler().build_plan(tasks, available_minutes=60)
    assert plan.scheduled[0].start_minute == 8 * 60


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------

def test_invalid_priority_raises():
    with pytest.raises(ValueError):
        Task("Bad task", 10, "urgent")


def test_negative_duration_raises():
    with pytest.raises(ValueError):
        Task("Bad task", -5, "high")


def test_owner_zero_time_raises():
    with pytest.raises(ValueError):
        Owner("Jordan", 0)
