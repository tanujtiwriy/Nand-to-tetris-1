import subprocess, sys, os

here = os.path.dirname(os.path.abspath(__file__))
asm = os.path.join(here, "..", "Part_B_Assembler", "assembler.py")

for name in ["Add", "Max", "Rect", "Pong"]:
    mine = os.path.join(here, f"{name}Mine.hack")
    subprocess.run([sys.executable, asm, os.path.join(here, f"{name}.asm"), mine],
                   stdout=subprocess.DEVNULL, check=True)
    off = os.path.join(here, f"{name}.hack")  # official assembler wali file
    a = open(mine).read().split()
    b = open(off).read().split()
    print(name, "SAME" if a == b else "DIFFERENT")