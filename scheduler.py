"""
PawPal+ Scheduling Logic

Classes:
    Owner   — pet owner with a name and daily available time
    Pet     — pet with a name, species, and linked owner
    Task    — a care task with title, duration, and priority
    ScheduledTask — a task placed at a specific start time with a reason
    DailyPlan     — the full result: scheduled tasks + skipped tasks
    Scheduler     — builds a DailyPlan from tasks and constraints
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Owner:
    name: str
    available_minutes: int  # total time available in a day

    def __post_init__(self):
        if self.available_minutes <= 0:
            raise ValueError("available_minutes must be positive")


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "high", "medium", or "low"

    def __post_init__(self):
        if self.priority not in PRIORITY_ORDER:
            raise ValueError(f"priority must be one of {list(PRIORITY_ORDER)}")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")


@dataclass
class ScheduledTask:
    task: Task
    start_minute: int   # minutes from start of day (e.g. 480 = 8:00 AM)
    reason: str

    @property
    def end_minute(self) -> int:
        return self.start_minute + self.task.duration_minutes

    def start_time_str(self) -> str:
        return _minutes_to_time(self.start_minute)

    def end_time_str(self) -> str:
        return _minutes_to_time(self.end_minute)


@dataclass
class DailyPlan:
    scheduled: List[ScheduledTask] = field(default_factory=list)
    skipped: List[tuple] = field(default_factory=list)  # (Task, reason)

    @property
    def total_minutes(self) -> int:
        return sum(st.task.duration_minutes for st in self.scheduled)


class Scheduler:
    """Builds a DailyPlan by greedily scheduling tasks in priority order."""

    START_MINUTE = 8 * 60  # plans start at 8:00 AM

    def build_plan(
        self, tasks: List[Task], available_minutes: int
    ) -> DailyPlan:
        """
        Schedule tasks within available_minutes.

        Rules:
        - Tasks are ordered high → medium → low priority.
        - Within the same priority, shorter tasks come first (fit more in).
        - A task is skipped if it no longer fits in remaining time.
        """
        plan = DailyPlan()
        remaining = available_minutes
        current_minute = self.START_MINUTE

        sorted_tasks = sorted(
            tasks,
            key=lambda t: (PRIORITY_ORDER[t.priority], t.duration_minutes),
        )

        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                reason = (
                    f"Priority: {task.priority}. "
                    f"Fits within available time ({task.duration_minutes} min)."
                )
                plan.scheduled.append(
                    ScheduledTask(task, current_minute, reason)
                )
                current_minute += task.duration_minutes
                remaining -= task.duration_minutes
            else:
                reason = (
                    f"Skipped: only {remaining} min remaining, "
                    f"but task needs {task.duration_minutes} min."
                )
                plan.skipped.append((task, reason))

        return plan


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minutes_to_time(minutes: int) -> str:
    """Convert minutes-from-midnight to a readable time string."""
    h, m = divmod(minutes, 60)
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {period}"
