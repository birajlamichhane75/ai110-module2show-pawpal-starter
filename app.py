import streamlit as st
from scheduler import Owner, Pet, Task, Scheduler, PRIORITY_ORDER

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A daily pet care planner that schedules tasks based on priority and available time.")

# ---------------------------------------------------------------------------
# Owner & Pet info
# ---------------------------------------------------------------------------

st.header("1. Owner & Pet Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=120, step=10
    )
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

# ---------------------------------------------------------------------------
# Task management
# ---------------------------------------------------------------------------

st.header("2. Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"title": "Morning walk",   "duration_minutes": 30, "priority": "high"},
        {"title": "Feeding",        "duration_minutes": 10, "priority": "high"},
        {"title": "Enrichment toy", "duration_minutes": 15, "priority": "medium"},
        {"title": "Grooming",       "duration_minutes": 20, "priority": "medium"},
        {"title": "Nail trim",      "duration_minutes": 10, "priority": "low"},
    ]

with st.expander("➕ Add a new task", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Bath time")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)

    col_add, col_clear = st.columns([1, 1])
    with col_add:
        if st.button("Add task", use_container_width=True):
            # Conflict check: duplicate task title
            existing_titles = [t["title"].lower() for t in st.session_state.tasks]
            if task_title.strip().lower() in existing_titles:
                st.warning(
                    f"⚠️ A task named **\"{task_title}\"** already exists. "
                    "Rename it or remove the existing one first."
                )
            else:
                st.session_state.tasks.append(
                    {"title": task_title.strip(), "duration_minutes": int(duration), "priority": priority}
                )
                st.success(f'✅ Added "{task_title}"')
    with col_clear:
        if st.button("Clear all tasks", use_container_width=True):
            st.session_state.tasks = []
            st.info("All tasks cleared.")

# --- Task list display ---
if st.session_state.tasks:
    total_task_minutes = sum(t["duration_minutes"] for t in st.session_state.tasks)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total tasks", len(st.session_state.tasks))
    col_b.metric("Total duration", f"{total_task_minutes} min")
    col_c.metric("Available time", f"{int(available_minutes)} min")

    # Conflict warning: tasks exceed available time
    if total_task_minutes > available_minutes:
        st.warning(
            f"⚠️ **Time conflict detected:** Your tasks total **{total_task_minutes} min** "
            f"but you only have **{int(available_minutes)} min** available. "
            f"The scheduler will skip the lowest-priority tasks to fit within your time limit."
        )
    else:
        st.success("✅ All tasks fit within your available time.")

    # Sort task list by priority for display
    sort_option = st.selectbox(
        "Sort task list by",
        ["Priority (high → low)", "Duration (short → long)", "Duration (long → short)", "As added"],
        index=0,
    )

    display_tasks = list(st.session_state.tasks)
    if sort_option == "Priority (high → low)":
        display_tasks = sorted(display_tasks, key=lambda t: PRIORITY_ORDER[t["priority"]])
    elif sort_option == "Duration (short → long)":
        display_tasks = sorted(display_tasks, key=lambda t: t["duration_minutes"])
    elif sort_option == "Duration (long → short)":
        display_tasks = sorted(display_tasks, key=lambda t: -t["duration_minutes"])

    # Add emoji to priority column for readability
    display_rows = [
        {
            "Priority": {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}.get(
                t["priority"], t["priority"]
            ),
            "Task": t["title"],
            "Duration (min)": t["duration_minutes"],
        }
        for t in display_tasks
    ]
    st.table(display_rows)

else:
    st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------

st.header("3. Generate Daily Schedule")
st.caption(f"Tasks will be scheduled starting at **8:00 AM** within **{int(available_minutes)} minutes**.")

if st.button("Generate schedule", type="primary", use_container_width=True):
    if not st.session_state.tasks:
        st.warning("⚠️ Add at least one task before generating a schedule.")
    else:
        owner = Owner(owner_name, int(available_minutes))
        pet = Pet(pet_name, species, owner)
        task_objects = [
            Task(t["title"], t["duration_minutes"], t["priority"])
            for t in st.session_state.tasks
        ]
        scheduler = Scheduler()
        plan = scheduler.build_plan(task_objects, int(available_minutes))

        st.success(
            f"✅ Schedule built for **{pet.name}** ({pet.species}) — "
            f"owner: **{owner.name}** — "
            f"**{plan.total_minutes} of {int(available_minutes)} min used.**"
        )

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Scheduled tasks", len(plan.scheduled))
        col2.metric("Skipped tasks", len(plan.skipped))
        col3.metric("Time used", f"{plan.total_minutes} min")

        st.divider()

        # Scheduled tasks
        if plan.scheduled:
            st.subheader("📋 Scheduled Tasks")
            for st_task in plan.scheduled:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    st_task.task.priority, ""
                )
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(
                            f"{priority_icon} **{st_task.task.title}**  \n"
                            f"🕐 {st_task.start_time_str()} → {st_task.end_time_str()}  \n"
                            f"_{st_task.reason}_"
                        )
                    with col_b:
                        st.metric("Duration", f"{st_task.task.duration_minutes} min")
        else:
            st.warning("⚠️ No tasks could be scheduled within the available time.")

        # Skipped tasks
        if plan.skipped:
            st.divider()
            st.subheader("⏭️ Skipped Tasks")
            st.caption(
                "These tasks did not fit within the remaining time. "
                "Consider increasing your available time or removing lower-priority tasks."
            )
            for task, reason in plan.skipped:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "")
                st.error(
                    f"{priority_icon} **{task.title}** ({task.duration_minutes} min, "
                    f"priority: {task.priority}) — {reason}"
                )
