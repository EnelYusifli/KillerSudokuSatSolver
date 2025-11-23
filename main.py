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
    cages_satisfiable = [
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
    cages_unsatisfiable = [
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
        (17, [(8,7),(8,8)])
        ]
    cages_satisfiable16x16 = [
        (14, [(0,0),(0,1),(1,0),(1,1)]),
        (22, [(0,2),(0,3),(1,2),(1,3)]),
        (46, [(2,0),(2,1),(3,0),(3,1)]),
        (54, [(2,2),(2,3),(3,2),(3,3)]),

        (30, [(0,4),(0,5),(1,4),(1,5)]),
        (38, [(0,6),(0,7),(1,6),(1,7)]),
        (30, [(2,4),(2,5),(3,4),(3,5)]),
        (38, [(2,6),(2,7),(3,6),(3,7)]),

        (46, [(0,8),(0,9),(1,8),(1,9)]),
        (54, [(0,10),(0,11),(1,10),(1,11)]),
        (14, [(2,8),(2,9),(3,8),(3,9)]),
        (22, [(2,10),(2,11),(3,10),(3,11)]),

        (30, [(0,12),(0,13),(1,12),(1,13)]),
        (38, [(0,14),(0,15),(1,14),(1,15)]),
        (30, [(2,12),(2,13),(3,12),(3,13)]),
        (38, [(2,14),(2,15),(3,14),(3,15)]),

        (14, [(4,0),(4,1),(5,0),(5,1)]),
        (22, [(4,2),(4,3),(5,2),(5,3)]),
        (46, [(6,0),(6,1),(7,0),(7,1)]),
        (54, [(6,2),(6,3),(7,2),(7,3)]),

        (30, [(4,4),(4,5),(5,4),(5,5)]),
        (38, [(4,6),(4,7),(5,6),(5,7)]),
        (30, [(6,4),(6,5),(7,4),(7,5)]),
        (38, [(6,6),(6,7),(7,6),(7,7)]),

        (46, [(4,8),(4,9),(5,8),(5,9)]),
        (54, [(4,10),(4,11),(5,10),(5,11)]),
        (14, [(6,8),(6,9),(7,8),(7,9)]),
        (22, [(6,10),(6,11),(7,10),(7,11)]),

        (30, [(4,12),(4,13),(5,12),(5,13)]),
        (38, [(4,14),(4,15),(5,14),(5,15)]),
        (30, [(6,12),(6,13),(7,12),(7,13)]),
        (38, [(6,14),(6,15),(7,14),(7,15)]),

        (14, [(8,0),(8,1),(9,0),(9,1)]),
        (22, [(8,2),(8,3),(9,2),(9,3)]),
        (46, [(10,0),(10,1),(11,0),(11,1)]),
        (54, [(10,2),(10,3),(11,2),(11,3)]),

        (30, [(8,4),(8,5),(9,4),(9,5)]),
        (38, [(8,6),(8,7),(9,6),(9,7)]),
        (30, [(10,4),(10,5),(11,4),(11,5)]),
        (38, [(10,6),(10,7),(11,6),(11,7)]),

        (46, [(8,8),(8,9),(9,8),(9,9)]),
        (54, [(8,10),(8,11),(9,10),(9,11)]),
        (14, [(10,8),(10,9),(11,8),(11,9)]),
        (22, [(10,10),(10,11),(11,10),(11,11)]),

        (30, [(8,12),(8,13),(9,12),(9,13)]),
        (38, [(8,14),(8,15),(9,14),(9,15)]),
        (30, [(10,12),(10,13),(11,12),(11,13)]),
        (38, [(10,14),(10,15),(11,14),(11,15)]),

        (14, [(12,0),(12,1),(13,0),(13,1)]),
        (22, [(12,2),(12,3),(13,2),(13,3)]),
        (46, [(14,0),(14,1),(15,0),(15,1)]),
        (54, [(14,2),(14,3),(15,2),(15,3)]),

        (30, [(12,4),(12,5),(13,4),(13,5)]),
        (38, [(12,6),(12,7),(13,6),(13,7)]),
        (30, [(14,4),(14,5),(15,4),(15,5)]),
        (38, [(14,6),(14,7),(15,6),(15,7)]),

        (46, [(12,8),(12,9),(13,8),(13,9)]),
        (54, [(12,10),(12,11),(13,10),(13,11)]),
        (14, [(14,8),(14,9),(15,8),(15,9)]),
        (22, [(14,10),(14,11),(15,10),(15,11)]),

        (30, [(12,12),(12,13),(13,12),(13,13)]),
        (38, [(12,14),(12,15),(13,14),(13,15)]),
        (30, [(14,12),(14,13),(15,12),(15,13)]),
        (38, [(14,14),(14,15),(15,14),(15,15)]),
    ]
    clauses = encode_killer_sudoku(n, cages_satisfiable)
    write_cnf(clauses, n, "puzzle.cnf")
    output = run_glucose(solver_path, "puzzle.cnf")
    # print(output) 
    decode_solution(output,n)
