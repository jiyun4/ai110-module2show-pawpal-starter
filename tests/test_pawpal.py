import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(description="Walk", time=30, frequency="daily")

    assert task.completed is False          # starts incomplete

    task.mark_complete()

    assert task.completed is True           # mark_complete() flipped it


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="Dog", breed="Corgi")

    assert len(pet.tasks) == 0             # starts empty

    pet.add_task(Task(description="Feed", time=10, frequency="daily"))

    assert len(pet.tasks) == 1             # one task added


def test_completing_daily_task_spawns_next_occurrence():
    pet = Pet(name="Mochi", species="Dog", breed="Corgi")
    task = Task(description="Feed", time=10, frequency="daily")
    pet.add_task(task)
    owner = Owner(name="Jiyeon", available_time=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    upcoming = scheduler.complete_task(task)

    assert task.completed is True                         # original marked done
    assert upcoming is not None                           # a new instance was created
    assert upcoming.completed is False                    # the new one starts fresh
    assert upcoming.due_date == date.today() + timedelta(days=1)   # due tomorrow
    assert pet.tasks == [task, upcoming]                  # auto-attached to the pet


def test_completing_weekly_task_is_due_in_seven_days():
    task = Task(description="Groom", time=45, frequency="weekly")

    upcoming = task.next_occurrence()

    assert upcoming.due_date == date.today() + timedelta(weeks=1)


def test_non_repeating_task_has_no_next_occurrence():
    task = Task(description="Vet visit", time=60, frequency="once")

    assert task.next_occurrence() is None                 # unknown frequency doesn't repeat


def test_detect_conflicts_flags_same_start_time_across_pets():
    mochi = Pet(name="Mochi", species="Dog", breed="Corgi")
    mochi.add_task(Task("Feed", time=10, frequency="daily", start="07:00"))
    luna = Pet(name="Luna", species="Cat", breed="Tabby")
    luna.add_task(Task("Clean litter", time=15, frequency="daily", start="7:00"))  # unpadded, same slot
    owner = Owner(name="Jiyeon", available_time=60)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    conflicts = Scheduler(owner).detect_conflicts()

    assert len(conflicts) == 1                            # one clashing time slot
    assert "07:00" in conflicts[0]
    assert "Feed" in conflicts[0] and "Clean litter" in conflicts[0]


def test_no_conflicts_when_times_differ():
    pet = Pet(name="Mochi", species="Dog", breed="Corgi")
    pet.add_task(Task("Feed", time=10, frequency="daily", start="07:00"))
    pet.add_task(Task("Walk", time=30, frequency="daily", start="07:30"))
    owner = Owner(name="Jiyeon", available_time=60)
    owner.add_pet(pet)

    assert Scheduler(owner).detect_conflicts() == []      # different times, no warning
