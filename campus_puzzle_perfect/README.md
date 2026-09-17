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

Open the project folder in VS Code.

Open:

**Terminal → New Terminal**

Then run:

### macOS / Linux

```bash
python3 main.py
```

### Windows

```bash
python main.py
```

To generate a saved report in the `output` folder:

### macOS / Linux

```bash
python3 run_project.py
```

### Windows

```bash
python run_project.py
```

The saved result will be:

```text
output/schedule_report.txt
```

---

# 3. Input Data

The input is stored in:

```text
data/constraints.json
```

The file contains four important sections.

### Classes

Each class has:

- class ID
- number of students
- professor ID

Example:

```json
{
    "id": "CS101",
    "students": 180,
    "professor_id": "P01"
}
```

### Rooms

Each room has:

- room ID
- seating capacity

### Time Slots

The example uses:

```text
09:00
10:00
11:00
12:00
14:00
15:00
```

### Student Groups

Student groups show which classes are required by the same group.

For example:

```text
YEAR1_CS
    CS101
    CS102
    MATH101
    PHY101
    ENG101
```

Therefore, these classes cannot be scheduled at the same time.

This is important because checking only professors is not enough. Even when two classes have different professors, the students may still need both classes.

---

# 4. Stage 1 - Greedy Baseline

## What I did

For the first version, I used a greedy algorithm.

The classes are sorted by the number of enrolled students, from largest to smallest.

The program then tries to place each class into the first available combination of:

```text
time slot + room
```

The assignment is accepted only when:

- there is no student-group conflict
- there is no professor conflict
- the room is free
- the room is large enough

## Why sort by student count?

I selected the number of students as the sorting key because large classes are more difficult to place.

For example:

```text
200 students -> only large rooms can be used
10 students  -> many rooms can be used
```

If a large class is left until the end, the suitable rooms may already be occupied.

So I place the larger classes first.

## Complexity

If:

- C = number of classes
- T = number of time slots
- R = number of rooms

the main placement loop is approximately:

```text
O(C × T × R)
```

Conflict lookup is performed using sets, which keeps the checks simple and fast.

## Limitation

The greedy algorithm makes a decision and moves forward. It does not normally go back and change an earlier decision.

Because of that, the result can be valid but not necessarily the most efficient timetable.

---

# 5. Stage 2 - Conflict Graph

The second stage models the timetable as a graph.

Each class becomes a node.

Two classes are connected when:

1. They have the same professor, or
2. They are required by at least one common student group.

Example:

```text
CS101 -------- MATH101
   \              /
    \            /
       YEAR1_CS
```

CS101 and MATH101 are connected because YEAR1_CS needs both.

Connected classes must have different time slots.

## Welsh-Powell

I used the Welsh-Powell graph coloring approach.

The algorithm:

1. Calculates the degree of each class.
2. Processes classes with more conflicts first.
3. Gives each class the first color that none of its neighbours already has.
4. Treats each color as a timetable time slot.

For example:

```text
Color 0 -> 09:00
Color 1 -> 10:00
Color 2 -> 11:00
```

## Complexity

The conflict graph is built by comparing pairs of classes:

```text
O(C²)
```

The coloring process is also approximately:

```text
O(C²)
```

for this implementation.

This gives a much clearer representation of student and professor conflicts than checking classes independently.

---

# 6. Stage 3 - Dynamic Programming

After the graph stage assigns time slots, the next problem is room allocation.

The question becomes:

> For each time slot, which room should each class use so that the total unused room capacity is as small as possible?

I used Dynamic Programming for this part.

## DP State

The state is:

```text
dp(i, j)
```

where:

- `i` = number of classes being considered
- `j` = number of rooms being considered

The value represents the minimum unused capacity possible.

## Recurrence

There are two choices for each room.

### Option 1 - Do not use the room

```text
dp(i, j - 1)
```

### Option 2 - Use the room

If the room can fit the class:

```text
dp(i - 1, j - 1)
+ room capacity
- number of students
```

Therefore:

```text
dp(i, j) =
min(
    dp(i, j - 1),
    dp(i - 1, j - 1) + room capacity - students
)
```

## Why Dynamic Programming?

Trying every possible room assignment directly would create many combinations.

The DP solution reuses previously calculated states.

For `C` classes and `R` rooms in one time slot:

```text
Time complexity: O(C × R)
Space complexity: O(C × R)
```

This is much more manageable for the room-allocation part of the problem.

---

# 7. Stage 4 - Backtracking

The final stage is used when the earlier approaches cannot produce a complete timetable.

Backtracking works by trying an assignment and continuing recursively.

The basic idea is:

```text
Choose class
      ↓
Try time slot and room
      ↓
Is it valid?
   /       \
 Yes        No
  ↓          ↓
Next       Try another
class      assignment
```

If the program reaches a dead end, it goes back to an earlier decision and tries another option.

## Best-Effort Requirement

A complete timetable is not always possible.

For example:

- there may be more classes than available rooms
- a room may be too small
- several classes may require the same time period because of other constraints

Instead of simply failing, the program stores the largest valid partial schedule it has found.

The remaining classes are printed in the Conflict Report.

---

# 8. Backtracking Pruning

Backtracking can become expensive because many combinations may need to be tested.

I used several simple techniques to reduce the search.

### Most-constrained-first

Classes with fewer possible room/time combinations are considered earlier.

### Large classes first

If two classes have similar constraints, the larger class is considered first because it has fewer room choices.

### Lower-waste rooms first

Rooms that leave less unused capacity are tried first.

### Immediate rejection

An assignment is rejected immediately when:

- the room is already occupied
- the professor has a conflict
- a shared student group has a conflict

### Branch-and-bound

If the current branch cannot produce a schedule larger than the best schedule already found, the branch is stopped.

A search-node limit is also used so that the program remains practical when the input becomes much larger.

---

# 9. Conflict Report

The main requirement of this project is the Conflict Report.

The program uses the following format:

```text
Scheduled CS101      09:00 R-107 Perfect Fit
Scheduled MATH202    10:00 R-102 Wasted 5 seats
Unscheduled HIST101  N/A   N/A    No valid time/room combination found
```

The report tells the manager:

- which classes were scheduled
- when they were scheduled
- which room was selected
- how many seats were unused
- which classes could not be scheduled
- why they could not be scheduled

---

# 10. Manual Fix Log

The final output is intended to support a human university manager.

If one or two classes remain unscheduled, the manager does not need to rebuild the entire timetable.

The manager can review the Conflict Report and consider:

1. Adding another time slot.
2. Adding another lecture room.
3. Using a larger room.
4. Splitting a large class into multiple sections.
5. Reviewing student-group requirements.
6. Reviewing exceptional professor constraints.

The software therefore handles the majority of the scheduling work while leaving difficult exceptions for manual review.

---

# 11. Comparison of the Four Stages

| Stage | Algorithm | Main Purpose |
|---|---|---|
| 1 | Greedy | Quickly create an initial timetable |
| 2 | Welsh-Powell | Prevent student/professor time conflicts |
| 3 | Dynamic Programming | Reduce unused room capacity |
| 4 | Backtracking | Find the largest valid schedule when constraints are tight |

Each algorithm has a different job. The project does not depend on one algorithm for the entire problem.

---

# 12. Why These Algorithms Were Used

### Greedy

Greedy is simple and fast, so it is useful for producing an initial schedule quickly.

### Graph Coloring

The biggest hidden problem is the relationship between classes through student groups. A conflict graph represents those relationships directly.

### Dynamic Programming

Room allocation is an optimization problem. DP avoids checking every possible room arrangement from scratch.

### Backtracking

Backtracking is useful when a valid solution is difficult to find because of tightly connected constraints. It can undo previous decisions and try alternatives.

---

# 13. Example of a Student Group Conflict

Suppose:

```text
YEAR1_CS:
    CS101
    MATH101
    CS102
```

Then:

```text
CS101 != MATH101
CS101 != CS102
MATH101 != CS102
```

for their time slots.

The professors can all be different and the rooms can all be different. The classes still cannot overlap because the same students need to attend them.

This is one of the main reasons the conflict graph is important.

---

# 14. Testing

The project was tested by running:

```bash
python3 main.py
```

The sample input contains:

```text
18 classes
8 rooms
6 time slots
5 student groups
```

The program successfully executes all four stages.

---

# 15. GitHub Submission

After uploading the project to GitHub, another person can clone it using:

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK
```

Then:

```bash
cd campus_puzzle_scheduler
```

Run:

```bash
python3 main.py
```

or:

```bash
python3 run_project.py
```

The second command creates:

```text
output/schedule_report.txt
```

---

# 16. Future Improvements

The current version uses JSON so that the algorithms are easy to understand.

A larger version could later support:

- Excel/CSV input
- database storage
- a web interface
- individual student-level conflicts
- professor availability
- room building/location constraints
- lunch breaks
- preferred teaching times
- multiple sections
- timetable export to Excel/PDF

---

## Conclusion

The Campus Puzzle demonstrates how different algorithms can be combined to solve a real scheduling problem.

The project starts with a fast Greedy solution, uses Graph Theory to understand conflicts, applies Dynamic Programming to improve room usage, and finally uses Backtracking to handle difficult cases.

The final result is a practical timetable together with a Conflict Report, so the university manager can see exactly what was scheduled and what still needs attention.


## Final Output

The terminal output shows all four stages.

The final stage prints:

```text
Scheduled CLASS TIME ROOM Perfect Fit
Scheduled CLASS TIME ROOM Wasted X seats
Unscheduled CLASS N/A N/A reason
```

It also prints a final check showing how many classes were scheduled and the total unused room capacity.
