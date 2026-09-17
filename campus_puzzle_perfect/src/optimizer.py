from functools import lru_cache


def optimize_one_time_slot(classes, rooms):
    classes = list(classes)
    rooms = sorted(rooms, key=lambda room: room["capacity"])

    n = len(classes)
    m = len(rooms)

    @lru_cache(maxsize=None)
    def dp(room_index, used_mask):
        if room_index == m:
            return (0, 0)

        best_count, best_waste = dp(room_index + 1, used_mask)

        room = rooms[room_index]

        for class_index, cls in enumerate(classes):
            if used_mask & (1 << class_index):
                continue

            if room["capacity"] < cls["students"]:
                continue

            count, waste = dp(
                room_index + 1,
                used_mask | (1 << class_index)
            )

            candidate = (
                count + 1,
                waste + room["capacity"] - cls["students"]
            )

            if candidate[0] > best_count:
                best_count, best_waste = candidate
            elif candidate[0] == best_count and candidate[1] < best_waste:
                best_count, best_waste = candidate

        return best_count, best_waste

    best_count, best_waste = dp(0, 0)

    assignments = []
    room_index = 0
    used_mask = 0

    while room_index < m and len(assignments) < best_count:
        current = dp(room_index, used_mask)
        skip = dp(room_index + 1, used_mask)

        if current == skip:
            room_index += 1
            continue

        room = rooms[room_index]
        chosen = None

        for class_index, cls in enumerate(classes):
            if used_mask & (1 << class_index):
                continue
            if room["capacity"] < cls["students"]:
                continue

            next_value = dp(
                room_index + 1,
                used_mask | (1 << class_index)
            )

            candidate = (
                next_value[0] + 1,
                next_value[1] + room["capacity"] - cls["students"]
            )

            if candidate == current:
                chosen = class_index
                break

        if chosen is None:
            room_index += 1
            continue

        cls = classes[chosen]
        assignments.append({
            "class_id": cls["id"],
            "room": room["id"],
            "capacity": room["capacity"],
            "students": cls["students"],
            "waste": room["capacity"] - cls["students"]
        })

        used_mask |= 1 << chosen
        room_index += 1

    return assignments, best_waste


def optimize_schedule(classes, rooms, class_times):
    final_schedule = []
    unscheduled = []

    times = sorted(
        time for time in set(class_times.values())
        if time is not None
    )

    for time in times:
        slot_classes = [
            cls for cls in classes
            if class_times.get(cls["id"]) == time
        ]

        assignments, _ = optimize_one_time_slot(slot_classes, rooms)
        assigned_ids = {item["class_id"] for item in assignments}

        for item in assignments:
            item["time"] = time
            final_schedule.append(item)

        for cls in slot_classes:
            if cls["id"] not in assigned_ids:
                unscheduled.append({
                    "class_id": cls["id"],
                    "reason": "No feasible room available in this time slot"
                })

    for cls in classes:
        if class_times.get(cls["id"]) is None:
            unscheduled.append({
                "class_id": cls["id"],
                "reason": "No available time slot"
            })

    return final_schedule, unscheduled
