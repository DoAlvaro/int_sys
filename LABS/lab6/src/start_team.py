"""Запуск полной команды (7 игроков) в отдельных процессах."""
import subprocess
import sys
import time
import argparse

ROLES = [
    "goalie",
    "defender_top", "defender_center", "defender_bottom",
    "forward_top", "forward_center", "forward_bottom",
]


def start_team(team_name: str, side: str):
    processes = []
    for role in ROLES:
        cmd = [
            sys.executable, "main.py",
            "--team", team_name,
            "--role", role,
            "--side", side,
        ]
        print(f"Запуск: {' '.join(cmd)}")
        p = subprocess.Popen(cmd, cwd="src" if "src" not in sys.executable else ".")
        processes.append(p)
        time.sleep(0.15)
    return processes


def main():
    parser = argparse.ArgumentParser(description="Запуск команды (7 игроков)")
    parser.add_argument("--team", type=str, default="teamA")
    parser.add_argument("--side", type=str, default="l", choices=["l", "r"])
    args = parser.parse_args()
    processes = start_team(args.team, args.side)
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nОстановка...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("Остановлено")


if __name__ == "__main__":
    main()
