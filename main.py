from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create pets and assign tasks ---

mochi = Pet(name="Mochi", species="Dog", breed="Corgi")
mochi.add_task(Task(description="Morning walk",  time=30, frequency="daily", priority=2, start="07:30"))
mochi.add_task(Task(description="Feed breakfast", time=10, frequency="daily", priority=1, start="07:00"))
mochi.add_task(Task(description="Training session", time=20, frequency="weekly", priority=4, start="17:00"))

luna = Pet(name="Luna", species="Cat", breed="Tabby")
# Note: this task starts at 07:00 — the SAME time as Mochi's "Feed breakfast"
# above, so the Scheduler should flag a cross-pet time conflict (not crash).
luna.add_task(Task(description="Clean litter box", time=15, frequency="daily", priority=1, start="07:00"))
luna.add_task(Task(description="Brush fur",        time=25, frequency="weekly", priority=3, start="20:00"))

# --- Create owner, register pets ---

owner = Owner(name="Jiyeon", available_time=75)
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Run the scheduler and print today's plan ---

scheduler = Scheduler(owner)

print("=" * 40)
print("       TODAY'S SCHEDULE")
print("=" * 40)
print(scheduler.display_plan())
print("=" * 40)

# --- Conflict check (warns instead of crashing) ---

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\nSchedule warnings:")
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("\nNo scheduling conflicts. 🎉")
