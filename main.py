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
                box_cells = []
                # at least once
                for r in range(br * box_size, (br + 1) * box_size):
                    for c in range(bc * box_size, (bc + 1) * box_size):
                        box_cells.append(varnum(r, c, v, n))
                # at most once
                clauses.append(box_cells)
                for i in range(len(box_cells)):
                    for j in range(i + 1, len(box_cells)):
                        clauses.append([-box_cells[i], -box_cells[j]])

# run glucose
def run_glucose(solver_path, cnf_file):
    result = subprocess.run([solver_path, "-model", cnf_file], capture_output=True, text=True)
    return result.stdout
