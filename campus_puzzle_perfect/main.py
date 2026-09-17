from pathlib import Path

from src.utils import load_data, fit_message
from src.greedy_solver import build_conflict_graph, greedy_schedule
from src.graph_engine import welsh_powell, assign_time_slots, count_edges
from src.optimizer import optimize_schedule
from src.backtracker import best_effort_backtracking


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "constraints.json"


def print_schedule(title, schedule, unscheduled):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)

    for item in sorted(schedule, key=lambda x: (x["time"], x["class_id"])):
        print(
            f"Scheduled {item['class_id']:<10} "
            f"{item['time']:<5} "
            f"{item['room']:<6} "
            f"{fit_message(item['waste'])}"
        )

    if unscheduled:
        print("\nConflict Report")
        for item in unscheduled:
            print(
                f"Unscheduled {item['class_id']:<10} "
                f"N/A   N/A    {item['reason']}"
            )

    total_waste = sum(item["waste"] for item in schedule)

    print(
        f"\nSummary: {len(schedule)} scheduled, "
        f"{len(unscheduled)} unscheduled, "
        f"{total_waste} unused seats"
    )

    return total_waste


def main():
    data = load_data(DATA_FILE)

    classes = data["classes"]
    rooms = data["rooms"]
    time_slots = data["time_slots"]
    groups = data["student_groups"]

    print("CAMPUS PUZZLE - UNIVERSITY TIMETABLE SCHEDULER")
    print("-" * 72)
    print(
        f"Input: {len(classes)} classes | "
        f"{len(rooms)} rooms | "
        f"{len(time_slots)} time slots"
    )

    conflicts = build_conflict_graph(classes, groups)

    greedy, greedy_unscheduled = greedy_schedule(
        classes, rooms, time_slots, conflicts
    )
    greedy_waste = print_schedule(
        "STAGE 1 - GREEDY BASELINE",
        greedy,
        greedy_unscheduled
    )

    colors = welsh_powell(conflicts)
    class_times = assign_time_slots(colors, time_slots)

    print("\n" + "=" * 72)
    print("STAGE 2 - CONFLICT GRAPH + WELSH-POWELL")
    print("=" * 72)
    print(
        f"Conflict graph: {len(conflicts)} classes, "
        f"{count_edges(conflicts)} conflicts"
    )
    print(f"Time slots required by coloring: {max(colors.values()) + 1}")

    greedy_conflicts = sum(
        1
        for i, first in enumerate(greedy)
        for second in greedy[i + 1:]
        if first["time"] == second["time"]
        and (
            second["class_id"] in conflicts[first["class_id"]]
            or first["class_id"] in conflicts[second["class_id"]]
        )
    )

    graph_conflicts = sum(
        1
        for i, first in enumerate(classes)
        for second in classes[i + 1:]
        if class_times.get(first["id"]) is not None
        and class_times.get(first["id"]) == class_times.get(second["id"])
        and second["id"] in conflicts[first["id"]]
    )

    print("\nStage 2 Comparison")
    print(f"Greedy baseline conflicts: {greedy_conflicts}")
    print(f"Graph coloring conflicts:  {graph_conflicts}")
    print("Graph coloring uses the conflict graph to keep connected classes in different time slots.")

    print("\nClass -> Time Slot")
    for class_id in sorted(class_times):
        print(f"{class_id:<10} -> {class_times[class_id] or 'UNASSIGNED'}")

    optimized, dp_unscheduled = optimize_schedule(
        classes, rooms, class_times
    )
    dp_waste = print_schedule(
        "STAGE 3 - DYNAMIC PROGRAMMING ROOM OPTIMIZATION",
        optimized,
        dp_unscheduled
    )

    print("\nDP Comparison")
    print(f"Greedy room waste: {greedy_waste} seats")
    print(f"DP room waste:     {dp_waste} seats")

    if dp_waste < greedy_waste:
        print("DP reduced room-capacity waste.")
    elif dp_waste == greedy_waste:
        print("DP found the same minimum waste for this input.")
    else:
        print("DP prioritizes feasible allocation for the fixed time slots.")

    best, best_unscheduled, nodes = best_effort_backtracking(
        classes, rooms, time_slots, conflicts
    )
    final_waste = print_schedule(
        "STAGE 4 - BACKTRACKING BEST-EFFORT SOLUTION",
        best,
        best_unscheduled
    )

    print(f"Backtracking search nodes visited: {nodes}")

    print("\n" + "=" * 72)
    print("CONFLICT REPORT")
    print("=" * 72)

    if best_unscheduled:
        for item in best_unscheduled:
            print(
                f"Unscheduled {item['class_id']:<10} "
                f"N/A   N/A    {item['reason']}"
            )
    else:
        print("No unscheduled classes.")

    print("\n" + "=" * 72)
    print("MANUAL FIX LOG")
    print("=" * 72)

    if best_unscheduled:
        print("The following classes need manual review.")
        print("- Add another time slot")
        print("- Add or enlarge a room")
        print("- Split a large class")
        print("- Review student-group requirements")
        print("- Review professor constraints")
    else:
        print("All classes were scheduled successfully.")
        print("No manual intervention is required.")

    print("\nFINAL CHECK")
    print("-" * 72)
    print(f"Classes scheduled: {len(best)} / {len(classes)}")
    print(f"Final unused capacity: {final_waste} seats")
    print("Student-group and professor conflicts are treated as hard constraints.")


if __name__ == "__main__":
    main()
