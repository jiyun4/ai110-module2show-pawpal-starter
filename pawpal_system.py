"""
PawPal — a simple pet-care task scheduler.

Class hierarchy (who "owns" who):

    Owner  --has many-->  Pet  --has many-->  Task
    Scheduler  --reads-->  Owner (and everything under it)

    Owner, Pet, Task  -> data holders (dataclasses)
    Scheduler         -> the "brain" that retrieves & organizes tasks
"""

from dataclasses import dataclass, field
from datetime import date, time as clock, timedelta


# How far ahead each frequency repeats. timedelta gives accurate calendar math
# (it rolls month/year boundaries for us). "monthly" is approximated as 30 days,
# since calendar months vary in length.
FREQUENCY_DELTAS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),
}


def parse_hhmm(s: str) -> clock:
    """Turn a 'HH:MM' string like '07:30' into a comparable datetime.time.

    Using a real time object (instead of comparing the raw string) makes the
    sort robust to un-padded hours like '9:15'.
    """
    hours, minutes = s.split(":")
    return clock(int(hours), int(minutes))


# ---------------------------------------------------------------------------
# Task — a single activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """One pet-care activity, e.g. 'Walk the dog' for 30 minutes, daily."""
    description: str
    time: int              # how many minutes this task takes
    frequency: str         # e.g. "daily", "weekly", "monthly"
    priority: int = 3      # 1 = must-do (highest) ... 5 = optional (lowest)
    start: str = "09:00"   # clock time this task starts, "HH:MM"
    due_date: date = field(default_factory=date.today)   # calendar day this is due
    completed: bool = False

    def mark_complete(self) -> None:
        """Flip this task to done."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Build a fresh, incomplete copy of this task due at the next occurrence.

        The new due date is today plus this task's frequency interval (e.g. a
        completed 'daily' task comes due again tomorrow). Returns None for a
        task whose frequency doesn't repeat.
        """
        delta = FREQUENCY_DELTAS.get(self.frequency)
        if delta is None:
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            priority=self.priority,
            start=self.start,
            due_date=date.today() + delta,
        )

    def __str__(self) -> str:
        """Return a formatted string showing start time, completion status, description, duration, frequency, priority, and due date."""
        check = "✓" if self.completed else " "
        return f"{self.start} [{check}] {self.description} ({self.time} min, {self.frequency}, priority {self.priority}, due {self.due_date})"


# ---------------------------------------------------------------------------
# Pet — details + its own list of tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet, which keeps its own to-do list of tasks."""
    name: str
    species: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)


# ---------------------------------------------------------------------------
# Owner — manages multiple pets
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """The person. Owns several pets and can reach all their tasks."""
    name: str
    available_time: int                          # minutes free today
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten every pet's task list into one combined list."""
        return [task for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler — the brain
# ---------------------------------------------------------------------------

class Scheduler:
    """Reads an owner's pets/tasks and organizes them into a plan."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets and tasks this scheduler will manage."""
        self.owner = owner

    def all_tasks(self) -> list[Task]:
        """Every task across every pet the owner has."""
        return self.owner.all_tasks()

    def filter_by_completion(self, completed: bool) -> list[Task]:
        """Return every task whose completion status matches `completed`."""
        return [task for task in self.all_tasks() if task.completed == completed]

    def pending_tasks(self) -> list[Task]:
        """Only the tasks that still need doing (not completed)."""
        return self.filter_by_completion(False)

    def completed_tasks(self) -> list[Task]:
        """Only the tasks already finished."""
        return self.filter_by_completion(True)

    def complete_task(self, task: Task) -> "Task | None":
        """Mark a task complete and, if it recurs, automatically schedule its
        next occurrence onto the same pet. Returns the new task (or None if the
        task doesn't repeat)."""
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is None:
            return None
        for pet in self.owner.pets:
            if task in pet.tasks:
                pet.add_task(upcoming)
                break
        return upcoming

    def prioritized_tasks(self) -> list[Task]:
        """Pending tasks ordered by importance: highest priority first,
        and for ties the shorter task first so more work fits in the day."""
        return sorted(self.pending_tasks(), key=lambda task: (task.priority, task.time))

    def sort_by_time(self) -> list[Task]:
        """Pending tasks ordered chronologically by their 'HH:MM' start time."""
        return sorted(self.pending_tasks(), key=lambda task: parse_hhmm(task.start))

    def detect_conflicts(self) -> list[str]:
        """Lightweight check for tasks that start at the same clock time.

        Groups pending tasks (across all pets) by their normalized start time,
        so '9:15' and '09:15' count as the same slot. Returns one warning
        message per clashing time; an empty list means no conflicts. This never
        raises — a clash is reported, not treated as an error.
        """
        by_time: dict[clock, list[Task]] = {}
        for task in self.pending_tasks():
            by_time.setdefault(parse_hhmm(task.start), []).append(task)

        warnings = []
        for start_time, tasks in sorted(by_time.items()):
            if len(tasks) > 1:
                names = ", ".join(task.description for task in tasks)
                warnings.append(
                    f"⚠️  Time conflict at {start_time.strftime('%H:%M')}: {names}"
                )
        return warnings

    def tasks_that_fit(self) -> list[Task]:
        """Return pending tasks that fit within the owner's available time budget,
        packing the most important tasks first."""
        remaining = self.owner.available_time
        plan = []
        for task in self.prioritized_tasks():
            if task.time <= remaining:
                plan.append(task)
                remaining -= task.time
        return plan

    def display_plan(self) -> str:
        """Build a readable summary of today's plan for print / Streamlit."""
        plan = self.tasks_that_fit()
        if not plan:
            return f"{self.owner.name} has no tasks that fit today."

        lines = [f"📋 {self.owner.name}'s plan ({self.owner.available_time} min free):"]
        total = 0
        for task in plan:
            lines.append(f"  {task}")
            total += task.time
        lines.append(f"Total: {total} min")

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.extend(conflicts)

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Quick manual test (runs only when you execute this file directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Build an owner with two pets, each with a couple of tasks.
    mochi = Pet(name="Mochi", species="Dog", breed="Corgi")
    mochi.add_task(Task("Walk", time=30, frequency="daily", priority=2, start="07:30"))
    mochi.add_task(Task("Feed", time=10, frequency="daily", priority=1, start="07:00"))

    luna = Pet(name="Luna", species="Cat", breed="Tabby")
    luna.add_task(Task("Clean litter", time=15, frequency="daily", priority=1, start="18:00"))
    luna.add_task(Task("Groom", time=45, frequency="weekly", priority=4, start="9:15"))

    owner = Owner(name="Jiyeon", available_time=60)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    print(scheduler.display_plan())

    print("\nChronological (sort_by_time):")
    for task in scheduler.sort_by_time():
        print(f"  {task}")
