import sys
from bardlang import run_bard_code

if len(sys.argv) < 2:
    print("Usage: python bard.py <script.bard>")
    sys.exit(1)

filename = sys.argv[1]

if not filename.endswith(".bard"):
    print(f"Warning: '{filename}' does not have a .bard extension.")

try:
    with open(filename, "r") as f:
        source = f.read()
    run_bard_code(source)
except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)