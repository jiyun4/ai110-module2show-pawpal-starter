# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

========================================
       TODAY'S SCHEDULE
========================================
📋 Jiyeon's plan (75 min free):
  [ ] Morning walk (30 min, daily)
  [ ] Feed breakfast (10 min, daily)
  [ ] Training session (20 min, weekly)
  [ ] Clean litter box (15 min, daily)
Total: 75 min
========================================


## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here

===================================================== test session starts =====================================================
platform darwin -- Python 3.13.5, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/jiyeonkim/ai110-module2show-pawpal-starter
plugins: anyio-4.7.0
collected 10 items                                                                                                            

tests/test_pawpal.py ..........                                                                                         [100%]

===================================================== 10 passed in 0.03s ======================================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.prioritized_tasks()` | By start time, or by priority then duration |
| Filtering | `Scheduler.pending_tasks()`, `Scheduler.completed_tasks()` | By completion status (no per-pet filter yet) |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags pending tasks sharing the same start time |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | Computes next due date from `FREQUENCY_DELTAS`, re-adds to the same pet |


## 📸 Demo Walkthrough

Follow these steps to try the app yourself:

1. **Start the app.** Run `streamlit run app.py` in your terminal. A page called PawPal+ opens in your browser.

2. **Enter your info.** Type your name in the "Owner name" box and set how many minutes you have free today (for example, 60). Type your pet's name and pick their species.

3. **Add your first task.** Fill in the five task boxes — a title like "Morning walk", how long it takes (30 min), how often it repeats (daily), how important it is (priority 1 = must-do), and what time it starts (07:00). Click **Add task**. A green success message confirms it was saved.

4. **Add a few more tasks.** Try adding tasks at the same start time on purpose — for example two tasks both at 08:00. After you add them, a yellow warning box will appear automatically telling you there is a time conflict.

5. **Switch the sort view.** Use the "Sort tasks by" radio buttons above the table. Toggle between **Chronological** (tasks sorted by start time, earliest first) and **Priority** (most important tasks shown first). The table updates instantly.

6. **Mark a task complete.** Scroll to the "Complete a task" section. Pick a daily task from the dropdown and click **Mark complete**. A green message tells you the next occurrence was scheduled — for example, "Next 'Morning walk' scheduled for 2026-07-09." The task list now shows that new entry.

7. **Generate today's plan.** Click **Generate schedule**. Three tiles appear showing how many tasks fit, total time used, and minutes left over. Below them is a table of only the tasks that fit inside your available time, sorted by priority so the most important ones are at the top.

8. **See the conflict check again.** If any tasks in your generated plan share a start time, a yellow warning appears inside the plan section too — so you know exactly which tasks to reschedule.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
