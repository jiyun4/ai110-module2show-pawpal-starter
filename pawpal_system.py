"""PawPal — a simple pet-care task scheduler.

This module defines the four core classes from the UML:
    Owner, Pet, Task  -> plain data holders (dataclasses)
    Scheduler         -> the "brain" that sorts/filters tasks into a plan
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data holders
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """The person doing the pet care. Just holds info the Scheduler reads."""
    name: str
    available_time: int  # total minutes they can dedicate today


@dataclass
class Pet:
    """The pet being cared for. Pure data — no behavior."""
    name: str
    species: str
    breed: str


@dataclass
class Task:
    """One pet-care task, e.g. 'Walk the dog' for 30 minutes."""
    name: str
    duration: int          # minutes this task takes
    priority: str          # "high", "medium", or "low"
    recurring: bool = False

    def is_high_priority(self) -> bool:
        """Helper so the Scheduler can sort/filter more easily."""
        return self.priority == "high"


# ---------------------------------------------------------------------------
# The worker
# ---------------------------------------------------------------------------

class Scheduler:
    """Takes an owner, a pet, and a list of tasks -> builds a daily plan."""

    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add one task to the list."""
        # TODO: append task to self.tasks
        pass

    def sort_by_priority(self) -> list[Task]:
        """Order tasks high -> medium -> low."""
        # TODO: return self.tasks sorted by priority
        pass

    def filter_by_time(self) -> list[Task]:
        """Keep only the tasks that fit in the owner's available time."""
        # TODO: drop tasks once we run out of available_time
        pass

    def generate_plan(self) -> list[Task]:
        """Main method: sort, then filter -> return the final schedule."""
        # TODO: call sort_by_priority(), then filter_by_time()
        pass

    def display_plan(self) -> str:
        """Format the plan as a nice string for printing / Streamlit."""
        # TODO: build a readable summary of the plan
        pass


# ---------------------------------------------------------------------------
# Quick manual test (runs only when you execute this file directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    owner = Owner(name="Jiyeon", available_time=60)
    pet = Pet(name="Mochi", species="Dog", breed="Corgi")

    scheduler = Scheduler(owner, pet)
    scheduler.add_task(Task("Walk", duration=30, priority="high", recurring=True))
    scheduler.add_task(Task("Feed", duration=10, priority="high"))
    scheduler.add_task(Task("Groom", duration=45, priority="low"))

    print(scheduler.display_plan())
