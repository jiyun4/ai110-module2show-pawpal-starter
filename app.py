from datetime import time

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner & Pet setup ---

st.subheader("Quick Demo Inputs")
owner_name     = st.text_input("Owner name", value="Jordan")
available_time = st.number_input("Available time today (minutes)", min_value=1, max_value=480, value=60)
pet_name       = st.text_input("Pet name", value="Mochi")
species        = st.selectbox("Species", ["Dog", "Cat", "Other"])

# Initialize Owner and Pet in session state (runs once per session).
# Uses owner.add_pet() to link the pet into the owner's list.
if "owner" not in st.session_state:
    pet = Pet(name=pet_name, species=species, breed="Unknown")
    owner = Owner(name=owner_name, available_time=available_time)
    owner.add_pet(pet)              # Owner.add_pet() — registers the pet
    st.session_state.owner = owner
    st.session_state.pet   = pet

# --- Task entry ---

st.markdown("### Tasks")
st.caption("Add tasks for your pet. Each click calls pet.add_task() under the hood.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
with col4:
    priority = st.selectbox(
        "Priority",
        [1, 2, 3, 4, 5],
        index=2,
        help="1 = must-do (highest), 5 = optional (lowest)",
    )
with col5:
    start = st.time_input("Start time", value=time(9, 0))

if st.button("Add task"):
    new_task = Task(
        description=task_title,
        time=int(duration),
        frequency=frequency,
        priority=int(priority),
        start=start.strftime("%H:%M"),   # store as "HH:MM" string
    )
    st.session_state.pet.add_task(new_task)     # Pet.add_task() — attaches to this pet
    st.success(f"Added '{task_title}' to {st.session_state.pet.name}'s task list.")

# --- Task list with live sorting and conflict detection ---

current_tasks = st.session_state.pet.tasks
scheduler = Scheduler(st.session_state.owner)

if current_tasks:
    sort_mode = st.radio(
        "Sort tasks by",
        ["Chronological (start time)", "Priority (most important first)"],
        horizontal=True,
    )

    if sort_mode == "Chronological (start time)":
        display_tasks = scheduler.sort_by_time()
    else:
        all_tasks = scheduler.all_tasks()
        display_tasks = scheduler.prioritized_tasks(all_tasks)

    st.table([
        {
            "Start": t.start,
            "Task": t.description,
            "Duration (min)": t.time,
            "Frequency": t.frequency,
            "Priority": t.priority,
            "Due": str(t.due_date),
            "Done": "✓" if t.completed else "",
        }
        for t in display_tasks
    ])

    # Conflict warnings — always live, no button needed
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts detected.")
else:
    st.info("No tasks yet. Add one above.")

# --- Mark a task complete (auto-schedules the next occurrence) ---

pending = [t for t in current_tasks if not t.completed]
if pending:
    st.markdown("#### Complete a task")
    st.caption("Marking a daily/weekly/monthly task done auto-creates its next occurrence.")
    idx = st.selectbox(
        "Pick a task to mark complete",
        range(len(pending)),
        format_func=lambda i: f"{pending[i].description} ({pending[i].frequency})",
    )
    if st.button("Mark complete"):
        upcoming = scheduler.complete_task(pending[idx])
        if upcoming is not None:
            st.success(f"Done! Next '{upcoming.description}' scheduled for {upcoming.due_date}.")
        else:
            st.info("Done! This task does not repeat, so no new occurrence was created.")

st.divider()

# --- Schedule generation ---

st.subheader("Today's Plan")
st.caption("Tasks ranked by priority that fit within your available time.")

if st.button("Generate schedule"):
    plan = scheduler.tasks_that_fit()
    total_min = sum(t.time for t in plan)
    available = st.session_state.owner.available_time

    if not plan:
        st.warning(f"No tasks fit within {available} minutes today.")
    else:
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Tasks scheduled", len(plan))
        col_b.metric("Time used (min)", total_min)
        col_c.metric("Time remaining (min)", available - total_min)

        st.table([
            {
                "Priority": t.priority,
                "Start": t.start,
                "Task": t.description,
                "Duration (min)": t.time,
                "Frequency": t.frequency,
                "Due": str(t.due_date),
            }
            for t in plan
        ])

        conflicts = scheduler.detect_conflicts(plan)
        if conflicts:
            st.markdown("**Conflicts in this plan:**")
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No conflicts in today's plan.")
