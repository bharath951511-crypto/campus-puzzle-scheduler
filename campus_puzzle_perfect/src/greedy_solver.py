def build_conflict_graph(classes, student_groups):
    graph = {item["id"]: set() for item in classes}

    class_groups = {}
    for group, class_ids in student_groups.items():
        for class_id in class_ids:
            class_groups.setdefault(class_id, set()).add(group)

    for i, first in enumerate(classes):
        for second in classes[i + 1:]:
            same_professor = first["professor_id"] == second["professor_id"]
            shared_group = bool(
                class_groups.get(first["id"], set())
                & class_groups.get(second["id"], set())
            )

            if same_professor or shared_group:
                graph[first["id"]].add(second["id"])
                graph[second["id"]].add(first["id"])

    return graph


def can_use_time(class_id, time, schedule, conflicts):
    for item in schedule:
        if item["time"] == time:
            if item["class_id"] == class_id:
                return False
            if item["class_id"] in conflicts[class_id]:
                return False
    return True


def room_is_free(room_id, time, schedule):
    return not any(
        item["time"] == time and item["room"] == room_id
        for item in schedule
    )


def greedy_schedule(classes, rooms, time_slots, conflicts):
    ordered = sorted(classes, key=lambda item: item["students"], reverse=True)
    rooms_by_capacity = sorted(rooms, key=lambda item: item["capacity"])

    schedule = []
    unscheduled = []

    for cls in ordered:
        placed = False

        for time in time_slots:
            if not can_use_time(cls["id"], time, schedule, conflicts):
                continue

            for room in rooms_by_capacity:
                if room["capacity"] < cls["students"]:
                    continue

                if room_is_free(room["id"], time, schedule):
                    schedule.append({
                        "class_id": cls["id"],
                        "time": time,
                        "room": room["id"],
                        "capacity": room["capacity"],
                        "students": cls["students"],
                        "waste": room["capacity"] - cls["students"]
                    })
                    placed = True
                    break

            if placed:
                break

        if not placed:
            unscheduled.append({
                "class_id": cls["id"],
                "reason": "No available time slot and room"
            })

    return schedule, unscheduled
