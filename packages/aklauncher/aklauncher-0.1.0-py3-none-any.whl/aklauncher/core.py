# aklauncher/core.py
import subprocess
import os

def launch(*scripts):
    for script in scripts:
        script_path = os.path.abspath(script)

        subprocess.Popen(
            f'start cmd /k python "{script_path}"',
            shell=True
        )

    print("All programs launched in separate CMD windows.")
