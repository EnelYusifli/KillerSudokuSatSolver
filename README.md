# KillerSudokuSatSolver
## 1. Problem Description

I wrote a Python program that solves Killer Sudoku by turning the puzzle into a SAT problem and solving it with the Glucose SAT solver.

In Killer Sudoku:
- Each row, column, and box must contain numbers 1…n exactly once.
- The puzzle also contains “cages.” Each cage has:
  - a target sum,
  - a group of cells,
  - and all numbers in the cage must be different and must add up to the target.

My program creates a CNF file, runs Glucose, and then prints the solved Sudoku grid.

---

## 2. What Each Function Does

### varnum(r, c, v, n)
This function turns a triple (row, column, value) into a single SAT variable number.  
SAT solvers only understand variables like 1, 2, 3, so I convert each (r,c,v) into one integer.

---

### encode_killer_sudoku(n, cages)
This function creates all CNF clauses for the puzzle.  
It adds:
- cell constraints (each cell has exactly one value),
- row constraints,
- column constraints,
- box constraints,
- and cage constraints (sum + no duplicates).

It returns a big list of clauses.

---

### write_cnf(clauses, n, filename)
This writes the SAT instance in *DIMACS CNF format* to a file.  
The Glucose solver can then read this file.

---

### run_glucose(solver_path, cnf_file)
This function starts the Glucose SAT solver with the CNF file and returns its output text.

---

### decode_solution(output, n)
This reads the SAT solver output, extracts all *true* variables, and rebuilds the solved Sudoku grid.  
If Glucose says UNSAT, it prints “Unsatisfiable”.

---

### if __name__ == "__main__":
This is the main part of the script.  
Here I:
- choose the puzzle instance,
- generate CNF clauses,
- write the CNF file,
- run Glucose,
- and print the final solution.

---

## 3. CNF Encoding (How I Translate the Puzzle)

### Variables
I use SAT variables of the form:


X(r, c, v) = the cell at row r and column c contains value v


Mapped into a single integer with:


varnum(r, c, v) = r*n*n + c*n + v


Values range from 1 to n³.

### Constraints
- *Cell:*  
  each cell has at least one value and at most one value.
- *Rows:*  
  each number 1…n appears exactly once in every row.
- *Columns:*  
  each number appears exactly once in every column.
- *Boxes:*  
  each number appears exactly once in each sqrt(n) × sqrt(n) box.
- *Cages:*  
  I check all possible combinations of values in a cage.  
  Every invalid combination (wrong sum or duplicates) becomes a forbidden clause.

This encoding is simple but becomes very large for big puzzles.

---

## 4. How to Run the Script

1. Install Glucose.
2. Set the correct solver_path in the script.
3. Choose which puzzle to solve (9×9 SAT, 9×9 UNSAT, or 16×16).
4. Set n accordingly.
5. Run:


python3 killer_sudoku_sat.py


The program:
- creates puzzle.cnf,
- calls Glucose,
- prints either the solved grid or “Unsatisfiable”.

---

## 5. Puzzle Instances I Included

- *9×9 SAT:*  
  I took this from an wikipedia Killer Sudoku and converted it to cage format.

- *9×9 UNSAT:*  
  Same puzzle but I changed one cage so it becomes impossible.

- *16×16:*  
  I created this myself because I could not find a real 16×16 Killer Sudoku.

---

## 6. Experiment Results

| Puzzle | Result | Time |
|--------|--------|------|
| 9×9 SAT | Solved | < 1 second |
| 9×9 UNSAT | UNSAT | < 1 second |
| 16×16 | Extremely slow | Did not finish |

The 9×9 puzzles work instantly.  
The 16×16 puzzle becomes too big because the cage combinations explode in size.

---
