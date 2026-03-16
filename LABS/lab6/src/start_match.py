"""Запуск матча: teamA (side l) и teamB (side r)."""
import subprocess
import sys
import time


def main():
    # Запуск из корня lab6: python3 src/start_match.py
    p_a = subprocess.Popen([
        sys.executable, "src/start_team.py",
        "--team", "teamA",
        "--side", "l",
    ])
    time.sleep(3)
    p_b = subprocess.Popen([
        sys.executable, "src/start_team.py",
        "--team", "teamB",
        "--side", "r",
    ])
    try:
        p_a.wait()
        p_b.wait()
    except KeyboardInterrupt:
        p_a.terminate()
        p_b.terminate()
        p_a.wait()
        p_b.wait()


if __name__ == "__main__":
    main()
