def best_effort_backtracking(classes, rooms, time_slots, conflicts, node_limit=100000):
    room_options = {
        cls["id"]: [
            room for room in rooms
            if room["capacity"] >= cls["students"]
        ]
        for cls in classes
    }

    def option_count(cls):
        return len(time_slots) * len(room_options[cls["id"]])

    ordered = sorted(
        classes,
        key=lambda cls: (
            option_count(cls),
            -cls["students"],
            -len(conflicts[cls["id"]])
        )
    )

    best = []
    nodes = 0

    def valid(cls, time, room, current):
        for item in current:
            if item["time"] != time:
                continue

            if item["room"] == room["id"]:
                return False

            if item["class_id"] in conflicts[cls["id"]]:
                return False

        return True

    def search(index, current):
        nonlocal best, nodes

        if nodes >= node_limit:
            return

        nodes += 1

        if len(current) > len(best):
            best = current.copy()

        remaining = len(ordered) - index
        if len(current) + remaining <= len(best):
            return

        if index == len(ordered):
            return

        cls = ordered[index]

        candidate_rooms = sorted(
            room_options[cls["id"]],
            key=lambda room: room["capacity"] - cls["students"]
        )

        if not candidate_rooms:
            search(index + 1, current)
            return

        for time in time_slots:
            for room in candidate_rooms:
                if nodes >= node_limit:
                    return

                if valid(cls, time, room, current):
                    current.append({
                        "class_id": cls["id"],
                        "time": time,
                        "room": room["id"],
                        "capacity": room["capacity"],
                        "students": cls["students"],
                        "waste": room["capacity"] - cls["students"]
                    })

                    search(index + 1, current)
                    current.pop()

        search(index + 1, current)

    search(0, [])

    scheduled_ids = {item["class_id"] for item in best}
    unscheduled = []

    for cls in classes:
        if cls["id"] not in scheduled_ids:
            if not room_options[cls["id"]]:
                reason = "No room has enough seats"
            else:
                reason = "No valid time/room combination found"

            unscheduled.append({
                "class_id": cls["id"],
                "reason": reason
            })

    return best, unscheduled, nodes
