import itertools
import subprocess

# convert (r = row,c = column,v = value) into unique variable number
def varnum(r, c, v, n=9):
    return r * n * n + c * n + v

# encode constraints into clauses
def encode_killer_sudoku(n, cages):
    clauses = []

    # each cell has at least one number, i.e. (Xr,c,1 or Xr,c,2 or ... or Xr,c,9)
    for r in range(n):
        for c in range(n):
            clauses.append([varnum(r, c, v, n) for v in range(1, n + 1)])

    # each cell has at most one number, i.e (-Xr,c,1 or -Xr,c,2 or ... or -Xr,c,9)
    for r in range(n):
        for c in range(n):
            for v1 in range(1, n + 1):
                for v2 in range(v1 + 1, n + 1):
                    clauses.append([-varnum(r, c, v1, n), -varnum(r, c, v2, n)])

    # each row contains each value once, i.e (Xr,0,v or Xr,1,v or ... or Xr,8,v)
    # at least once
    for r in range(n):
        for v in range(1, n + 1):
            clauses.append([varnum(r, c, v, n) for c in range(n)])
    # at most once
    for r in range(n):
        for v in range(1, n + 1):
            for c1 in range(n):
                for c2 in range(c1 + 1, n):
                    clauses.append([-varnum(r, c1, v, n), -varnum(r, c2, v, n)])

    # each column contains each value once, i.e (Xr,0,v or Xr,1,v or ... or Xr,8,v)
    # at least once
    for c in range(n):
        for v in range(1, n + 1):
            clauses.append([varnum(r, c, v, n) for r in range(n)])
    # at most once
    for c in range(n):
        for v in range(1, n + 1):
            for r1 in range(n):
                for r2 in range(r1 + 1, n):
                    clauses.append([-varnum(r1, c, v, n), -varnum(r2, c, v, n)])

    # each box(3x3) contains each value once
    box_size = int(n ** 0.5)
    for br in range(box_size): #block row
        for bc in range(box_size): #block column
            for v in range(1, n + 1): 
                # at least once
                box_cells = []
                for r in range(br * box_size, (br + 1) * box_size):
                    for c in range(bc * box_size, (bc + 1) * box_size):
                        box_cells.append(varnum(r, c, v, n))
                # at most once
                clauses.append(box_cells)
                for i in range(len(box_cells)):
                    for j in range(i + 1, len(box_cells)):
                        clauses.append([-box_cells[i], -box_cells[j]])

   # the numbers inside each cage must add up to the given total
    for total, cells in cages:
        k = len(cells)
        # iterate over all assignments of 1-n to these k cells
        for values in itertools.product(range(1, n + 1), repeat=k):
            # if this assignment is invalid, forbid it
            if sum(values) != total or len(set(values)) < k: # set makes sure that there are no duplicates, eg. no (1,1,3)
                clause = [-varnum(r, c, v, n) for (r, c), v in zip(cells, values)]
                clauses.append(clause)
    return clauses

# write how the instance is encoded as a SAT problem in the DIMACS CNF format into the file
def write_cnf(clauses, n, filename):
    num_vars = n * n * n
    with open(filename, "w") as f:
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")

# run glucose
def run_glucose(solver_path, cnf_file):
    result = subprocess.run([solver_path, "-model", cnf_file], capture_output=True, text=True)
    return result.stdout

# parse output model and print Sudoku
def decode_solution(output, n):
    lines = output.splitlines()
    model_line = [l for l in lines if l.startswith("v ")]
    if not model_line:
        print("Unsatisfiable")
        return
    values = []
    for l in model_line:
        values.extend(map(int, l.split()[1:]))
    grid = [[0]*n for _ in range(n)]
    for val in values:
        if val > 0: # positive values are true
            val -= 1 # values start from 1
            v = val % n + 1 # value is in range 0-9
            c = (val // n) % n
            r = val // (n * n)
            grid[r][c] = v
    for row in grid:
        print(" ".join(map(str, row)))

if __name__ == "__main__":
    solver_path = "/home/enel/Downloads/glucose/simp/glucose"
    n = 9
    cages_satisfliable = [
        (3,  [(0,0),(0,1)]),
        (15, [(0,2),(0,3),(0,4)]),
        (22, [(0,5),(1,5),(1,4),(2,4)]),
        (4,  [(0,6),(1,6)]),
        (16, [(0,7),(1,7)]),
        (15, [(0,8),(1,8),(2,8),(3,8)]),
        (25, [(1,0),(1,1),(2,0),(2,1)]),
        (17, [(1,2),(1,3)]),
        (9,  [(2,2),(2,3),(3,3)]),
        (8,  [(2,5),(3,5),(4,5)]),
        (20, [(2,6),(2,7),(3,6)]),
        (6,  [(3,0),(4,0)]),
        (14, [(3,1),(3,2)]),
        (17, [(3,4),(4,4),(5,4)]),
        (17, [(3,7),(4,6),(4,7)]),
        (13, [(4,1),(4,2),(5,1)]),
        (20, [(4,3),(5,3),(6,3)]),
        (12, [(4,8),(5,8)]),
        (27, [(5,0),(6,0),(7,0),(8,0)]),
        (6,  [(5,2),(6,1),(6,2)]),
        (20, [(5,5),(6,5),(6,6)]),
        (6,  [(5,6),(5,7)]),
        (10, [(6,4),(7,4),(7,3),(8,3)]),
        (14, [(6,7),(6,8),(7,7),(7,8)]),
        (8,  [(7,1),(8,1)]),
        (16, [(7,2),(8,2)]),
        (15, [(7,5),(7,6)]),
        (13, [(8,4),(8,5),(8,6)]),
        (17, [(8,7),(8,8)]),
    ]
    cages_unsatisfliable = [
        (3,  [(0,0),(0,1)]),
        (15, [(0,2),(0,3),(0,4)]),
        (22, [(0,5),(1,5),(1,4),(2,4)]),
        (4,  [(0,6),(1,6)]),
        (16, [(0,7),(1,7)]),
        (15, [(0,8),(1,8),(2,8),(3,8)]),
        (25, [(1,0),(1,1),(2,0),(2,1)]),
        (17, [(1,2),(1,3)]),
        (9,  [(2,2),(2,3),(3,3)]),
        (8,  [(2,5),(3,5),(4,5)]),
        (20, [(2,6),(2,7),(3,6)]),
        (6,  [(3,0),(4,0)]),
        (14, [(3,1),(3,7)]), # changed this line
        (17, [(3,4),(4,4),(5,4)]),
        (17, [(3,7),(4,6),(4,7)]),
        (13, [(4,1),(4,2),(5,1)]),
        (20, [(4,3),(5,3),(6,3)]),
        (12, [(4,8),(5,8)]),
        (27, [(5,0),(6,0),(7,0),(8,0)]),
        (6,  [(5,2),(6,1),(6,2)]),
        (20, [(5,5),(6,5),(6,6)]),
        (6,  [(5,6),(5,7)]),
        (10, [(6,4),(7,4),(7,3),(8,3)]),
        (14, [(6,7),(6,8),(7,7),(7,8)]),
        (8,  [(7,1),(8,1)]),
        (16, [(7,2),(8,2)]),
        (15, [(7,5),(7,6)]),
        (13, [(8,4),(8,5),(8,6)]),
        (17, [(8,7),(8,8)]),
    ]
    clauses = encode_killer_sudoku(n, cages_satisfliable)
    write_cnf(clauses, n, "puzzle.cnf")
    output = run_glucose(solver_path, "puzzle.cnf")
    # print(output) 
    decode_solution(output,n)
