# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design included five classes:
- `Owner` — holds the owner's name and total available minutes per day.
- `Pet` — holds pet name, species, and a reference to its `Owner`.
- `Task` — represents a single care activity with a title, duration in minutes, and a priority level (`high`, `medium`, `low`).
- `Scheduler` — stateless class with a `build_plan()` method that receives a list of `Task` objects and available minutes, then returns a `DailyPlan`.
- `DailyPlan` — holds two lists: `scheduled` (list of `ScheduledTask`) and `skipped` (list of task + reason tuples).
- `ScheduledTask` — wraps a `Task` with a `start_minute` and a human-readable `reason` string.

Each class had a single clear responsibility, keeping concerns separated.

**b. Design changes**

Originally `Scheduler` was going to accept an `Owner` object directly and read `available_minutes` from it. During implementation it became cleaner to pass `available_minutes` as an explicit parameter so the scheduler stays reusable regardless of where the time limit comes from (e.g., a UI slider). The `Owner` object is still used in the UI layer but is not required by the core scheduler.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints:
1. **Time** — total duration of scheduled tasks must not exceed `available_minutes`.
2. **Priority** — `high` tasks are always attempted before `medium`, and `medium` before `low`.

Within the same priority tier, shorter tasks are attempted first so that more tasks can fit in the available window.

Priority was treated as the primary constraint because missing a high-priority task (e.g., medication) is more harmful than skipping a low-priority one (e.g., a bath).

**b. Tradeoffs**

The greedy approach may skip a long high-priority task early and then fill the remaining time with many short low-priority tasks. For example, if 25 minutes remain and the next high-priority task takes 30 minutes, it is skipped — even though dropping one low-priority task would have made room for it.

This tradeoff is reasonable for a daily pet care planner because the schedule is regenerated each day. A skipped task simply reappears tomorrow, and the simple greedy model is easy to understand and verify.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used to:
- Brainstorm the class structure and responsibilities during the design phase.
- Generate initial stubs and then the full implementation of `scheduler.py`.
- Write comprehensive tests covering priority ordering, time constraints, edge cases, and time-slot correctness.
- Build the Streamlit UI in `app.py`, including the colored priority indicators and bordered task cards.

The most helpful prompts were specific: "implement the scheduling logic as a greedy algorithm sorted by priority then duration" rather than vague requests like "make a scheduler."

**b. Judgment and verification**

The AI initially suggested using `available_minutes=0` as a valid input (no guard). After reviewing the `Owner` class, a `__post_init__` check was added to raise a `ValueError` for non-positive values, since an owner with zero available time is a data error, not a valid scheduling scenario. The test `test_zero_available_time_skips_all_tasks` was kept separate because passing `0` directly to `build_plan` is still a valid edge case to handle gracefully.

---

## 4. Testing and Verification

**a. What you tested**

- High-priority tasks are always scheduled before medium and low.
- Tasks that exceed remaining time are skipped and include a reason string.
- Total duration of the plan never exceeds available time.
- Empty task list returns an empty plan.
- Zero available time skips all tasks.
- Exact-fit tasks (duration == available time) are scheduled.
- Time slots do not overlap.
- The plan always starts at 8:00 AM.
- Invalid priority values and negative durations raise `ValueError`.

These tests are important because they cover the core guarantee of the scheduler — that the plan is always time-safe and priority-correct.

**b. Confidence**

Confidence in the core scheduling logic is high. The greedy algorithm is simple enough to reason about manually, and the test suite covers all identified edge cases.

Edge cases to test next with more time:
- Two tasks with identical priority and duration (tie-breaking behavior).
- Very large task lists (performance).
- Tasks with `duration_minutes` equal to 1 (minimum boundary).
- Scheduling across midnight (plans that extend past 11:59 PM).

---

## 5. Reflection

**a. What went well**

The separation of concerns between `Scheduler` (pure logic, no UI), `DailyPlan` / `ScheduledTask` (data), and `app.py` (presentation) made it straightforward to test the logic independently and then wire it into Streamlit without mixing concerns.

**b. What you would improve**

In the next iteration I would add support for time windows — for example, "feeding must happen between 7 AM and 9 AM." The current model schedules all tasks sequentially from 8 AM with no awareness of time-of-day constraints. Adding a `preferred_window` field to `Task` and updating the scheduler to respect it would make the planner significantly more realistic.

**c. Key takeaway**

Designing the class interfaces before writing any logic (even just stubs with `pass`) forces you to think about what each piece of code *needs to know* versus what it *needs to do*. Keeping `Scheduler.build_plan()` independent of `Owner` made it immediately testable in isolation — a small design decision that paid off throughout the project.
