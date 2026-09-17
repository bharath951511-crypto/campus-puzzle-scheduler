def welsh_powell(graph):
    order = sorted(graph, key=lambda node: len(graph[node]), reverse=True)
    colors = {}

    for node in order:
        used = {colors[n] for n in graph[node] if n in colors}

        color = 0
        while color in used:
            color += 1

        colors[node] = color

    return colors


def assign_time_slots(colors, time_slots):
    result = {}

    for class_id, color in colors.items():
        result[class_id] = (
            time_slots[color]
            if color < len(time_slots)
            else None
        )

    return result


def count_edges(graph):
    return sum(len(neighbours) for neighbours in graph.values()) // 2
