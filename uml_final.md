# PawPal+ Final UML — Class Diagram

Copy the Mermaid code below into https://mermaid.live to view and export as `uml_final.png`.

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +__post_init__()
    }

    class Pet {
        +str name
        +str species
        +Owner owner
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +__post_init__()
    }

    class ScheduledTask {
        +Task task
        +int start_minute
        +str reason
        +end_minute() int
        +start_time_str() str
        +end_time_str() str
    }

    class DailyPlan {
        +List~ScheduledTask~ scheduled
        +List~tuple~ skipped
        +total_minutes() int
    }

    class Scheduler {
        +int START_MINUTE
        +build_plan(tasks, available_minutes) DailyPlan
    }

    Pet --> Owner : owned by
    ScheduledTask --> Task : wraps
    DailyPlan --> ScheduledTask : contains scheduled
    DailyPlan --> Task : contains skipped
    Scheduler --> DailyPlan : produces
    Scheduler --> Task : consumes
```

## How to export as PNG

1. Go to [https://mermaid.live](https://mermaid.live)
2. Paste the Mermaid code above into the editor
3. Click **Export → PNG**
4. Save the file as `uml_final.png` in this project folder

## Design notes

- `Scheduler` is stateless — it does not hold any pet or owner data, making it independently testable.
- `DailyPlan` separates `scheduled` (placed tasks) from `skipped` (tasks that did not fit), so the UI can display both clearly.
- `ScheduledTask` wraps a `Task` with a `start_minute` and a human-readable `reason`, keeping display logic out of `Task`.
- `Owner.available_minutes` is the single source of truth for the time constraint; the UI reads it and passes it to `Scheduler.build_plan()`.
```
