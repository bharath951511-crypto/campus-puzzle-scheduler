import json


def load_data(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_waste(room_capacity, student_count):
    return room_capacity - student_count


def fit_message(waste):
    if waste == 0:
        return "Perfect Fit"
    return f"Wasted {waste} seats"
