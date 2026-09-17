# Campus Puzzle - University Timetable Scheduler

## Project Overview

The Campus Puzzle is a university timetable scheduling problem.

For this project, I created a Python program that tries to build a timetable while following the main university rules:

- A professor should not have two classes at the same time.
- A student group should not have two required classes at the same time.
- A room should not be used by two classes at the same time.
- The room must have enough seats for the class.
- Smaller rooms should be preferred when possible so that room capacity is not unnecessarily wasted.

The project is divided into four stages. Each stage solves a different part of the problem.

---

## Folder Structure

```text
campus_puzzle_scheduler/
│
├── data/
│   └── constraints.json
│
├── src/
│   ├── __init__.py
│   ├── utils.py
│   ├── greedy_solver.py
│   ├── graph_engine.py
│   ├── optimizer.py
│   └── backtracker.py
│
├── output/
│   └── schedule_report.txt
│
├── main.py
├── run_project.py
├── README.md
└── .gitignore
```

---

# 1. Requirements

- Python 3
- VS Code
- Git (only required if the project is cloned from GitHub)

No third-party Python libraries are needed.

---

# 2. Running the Project in VS Code

If cloned from GitHub:

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK
cd campus_puzzle_perfect
```

Run the project:

```bash
python3 main.py
```

On Windows:

```bash
python main.py
```

To save the output to a file:

```bash
python3 run_project.py
```

The report is saved in:

```text
output/schedule_report.txt
```

## Input Data

The input is stored in:

```text
data/constraints.json
```

It contains:

- Class ID
- Number of students
- Professor ID
- Room ID and capacity
- Time slots
- Student groups and their required classes

Student groups are important because classes required by the same group cannot overlap.

# Stage 1 - Greedy Baseline

Classes are sorted by the number of enrolled students, from largest to smallest.

The program then places each class in the first available room and time slot that satisfies the constraints.

It checks:

- Student group conflicts
- Professor conflicts
- Room availability
- Room capacity

Large classes are placed first because they have fewer suitable rooms.

For `C` classes, `T` time slots and `R` rooms, the main placement loop is approximately:

```text
O(C × T × R)
```

The Greedy method is fast, but it does not normally change earlier decisions.

# Stage 2 - Conflict Graph

Each class becomes a node in a graph.

Two classes are connected if:

- They have the same professor, or
- They are required by the same student group

Connected classes cannot have the same time slot.

Welsh-Powell coloring assigns colors to the classes. Each color represents a time slot.

The graph is built by comparing class pairs:

```text
O(C²)
```

The coloring process is approximately:

```text
O(C²)
```

The program also compares the Greedy and graph-coloring conflicts.

# Stage 3 - Dynamic Programming

After time slots are assigned, Dynamic Programming is used to allocate rooms.

The goal is to minimize unused room capacity:

```text
room capacity - number of students
```

The DP keeps track of the rooms being considered and the classes already assigned in the current time slot.

For the supplied data:

```text
Greedy room waste: 295 seats
DP room waste:     235 seats
```

The DP therefore reduces unused capacity by 60 seats.

# Stage 4 - Backtracking

Backtracking tries different time and room assignments recursively.

If an assignment leads to a dead end, the program goes back and tries another option.

The program keeps the largest valid schedule it finds.

The search is reduced by:

- Trying highly constrained classes first
- Trying larger classes first
- Trying lower-waste rooms first
- Rejecting invalid assignments immediately
- Pruning branches that cannot improve the current solution
- Limiting the number of search nodes

# Conflict Report

If a class cannot be scheduled, the program reports it in this format:

```text
Scheduled CS101      09:00 R-107 Perfect Fit
Scheduled MATH202    10:00 R-102 Wasted 5 seats
Unscheduled HIST101  N/A   N/A    No valid time/room combination found
```

If all classes are scheduled:

```text
CONFLICT REPORT
No unscheduled classes.
```

# Manual Fix Log

If classes remain unscheduled, a manager can review the report and consider:

1. Adding another time slot
2. Adding another room
3. Using a larger room
4. Splitting a large class
5. Reviewing student-group requirements
6. Reviewing professor constraints

# Algorithm Summary

| Stage | Algorithm | Purpose |
|---|---|---|
| 1 | Greedy | Create an initial timetable quickly |
| 2 | Welsh-Powell | Prevent class time conflicts |
| 3 | Dynamic Programming | Reduce room capacity waste |
| 4 | Backtracking | Find the largest valid schedule |

# Testing

The sample data contains:

```text
18 classes
8 rooms
6 time slots
5 student groups
```

The project was tested using:

```bash
python3 main.py
```

The final example successfully schedules:

```text
18 / 18 classes
```

# GitHub

After cloning the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK
cd campus_puzzle_perfect
python3 main.py
```

To create the saved report:

```bash
python3 run_project.py
```

The report is created at:

```text
output/schedule_report.txt
```
