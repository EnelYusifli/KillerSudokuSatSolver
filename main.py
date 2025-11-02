import subprocess

solver_path = "/home/enel/Downloads/glucose/simp/glucose"  
cnf_file = "cnf_output/puzzle1.cnf"

result = subprocess.run([solver_path, "-model", cnf_file], capture_output=True, text=True)
print(result.stdout)
