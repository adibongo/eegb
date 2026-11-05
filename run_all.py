"""run_all.py — runs every Python figure script, lab and starter from the project root:  python run_all.py"""
import glob, subprocess, sys
fails = []
for f in sorted(glob.glob("sessions/s*/python/*.py")):
    print("running", f)
    if subprocess.run([sys.executable, f], capture_output=True).returncode: fails.append(f)
print("done;", "failed: " + ", ".join(fails) if fails else "all scripts ran cleanly")
