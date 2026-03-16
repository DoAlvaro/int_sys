"""Точка входа lab5: таблицы действий (goalie / attacker / defender)."""
import argparse
import sys
from player_bot import PlayerBot, InitFailedError


class LabRunner:
    @staticmethod
    def run_app():
        parser = argparse.ArgumentParser(description="Lab5 — таблицы действий")
        parser.add_argument("--team", type=str, default="teamA")
        parser.add_argument("--x", type=int, default=-15)
        parser.add_argument("--y", type=int, default=0)
        parser.add_argument(
            "--role",
            type=str,
            choices=["goalie", "attacker", "defender"],
            required=True,
        )
        args = parser.parse_args()
        bot = PlayerBot(squad_name=args.team, role=args.role)
        try:
            bot.run(start_pos=(args.x, args.y))
        except KeyboardInterrupt:
            bot.shutdown()
        except (InitFailedError, Exception) as e:
            print(e)
            bot.shutdown()
            sys.exit(1)


if __name__ == "__main__":
    LabRunner.run_app()
