# aklauncher/core.py
import subprocess
import os
import sys
import time
from typing import Dict, List

# Map absolute_script_path -> list of subprocess.Popen objects
_launched: Dict[str, List[subprocess.Popen]] = {}


def _abs(path: str) -> str:
    return os.path.abspath(path)


def launch(*scripts: str, python_executable: str = None):
    """
    Launch each script in its own new console window and remember the process.
    Usage:
        launch("prog1.py", "prog2.py")
    Optional:
        python_executable: path to python executable to use (defaults to sys.executable)
    """
    if python_executable is None:
        python_executable = sys.executable

    for script in scripts:
        script_path = _abs(script)

        if not os.path.exists(script_path):
            print(f"[aklauncher] Warning: script not found: {script_path}")
            # still attempt to launch (may fail), but skip if you prefer
            # continue

        # Use CREATE_NEW_CONSOLE to open a new console for the child on Windows
        try:
            proc = subprocess.Popen(
                [python_executable, script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except Exception as e:
            print(f"[aklauncher] Failed to launch {script_path}: {e}")
            continue

        # store process
        _launched.setdefault(script_path, []).append(proc)
        print(f"[aklauncher] Launched: {script_path} (pid={proc.pid})")


def _match_keys(names: List[str]) -> List[str]:
    """
    Given a list of names (could be basenames or full paths), return matching
    absolute script path keys from _launched.
    """
    keys = list(_launched.keys())
    matched = set()

    for name in names:
        name_abs = os.path.abspath(name)
        for k in keys:
            if k == name_abs:
                matched.add(k)
                continue
            # match by basename
            if os.path.basename(k).lower() == name.lower():
                matched.add(k)
                continue
            # partial match
            if name.lower() in k.lower():
                matched.add(k)
    return list(matched)


def unlaunch(*names: str):
    """
    Stop launched processes matching the provided script names (basename or full path).
    Example:
        unlaunch("prog1.py", "C:\\full\\path\\prog2.py")
    If multiple instances of same script were launched, all stored instances are terminated.
    """
    if not names:
        print("[aklauncher] No names supplied to unlaunch()")
        return

    keys = _match_keys(list(names))
    if not keys:
        print("[aklauncher] No matching launched scripts found for:", names)
        return

    for k in keys:
        procs = _launched.get(k, [])
        for p in procs:
            try:
                if p.poll() is None:
                    print(f"[aklauncher] Terminating pid={p.pid} for {k}")
                    p.kill()   # force kill
                    # wait briefly
                    for _ in range(10):
                        if p.poll() is not None:
                            break
                        time.sleep(0.05)
                else:
                    print(f"[aklauncher] Process already exited pid={p.pid} for {k}")
            except Exception as e:
                print(f"[aklauncher] Error stopping pid={getattr(p, 'pid', '?')}: {e}")
        # remove entry
        _launched.pop(k, None)


def unlaunch_all():
    """Terminate all processes launched by this module."""
    keys = list(_launched.keys())
    if not keys:
        print("[aklauncher] No launched scripts.")
        return
    unlaunch(*keys)


# alias
close_all = unlaunch_all


def list_launched():
    """Return a dict snapshot of launched scripts -> list of PIDs."""
    snapshot = {}
    for k, procs in _launched.items():
        snapshot[k] = [p.pid for p in procs if p is not None]
    return snapshot
