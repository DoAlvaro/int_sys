"""Точка входа lab2: планировщик действий + агент."""
import argparse
import sys
from action_planner import ActionPlanner
from player_bot import PlayerBot, InitFailedError


class LabRunner:
    @staticmethod
    def run_app():
        parser = argparse.ArgumentParser(description="Lab2 — агент с контроллером")
        parser.add_argument("--team", type=str, default="teamA")
        parser.add_argument("--x", type=int, default=-15)
        parser.add_argument("--y", type=int, default=0)
        parser.add_argument("--goalie", action="store_true")
        args = parser.parse_args()
        steps = [
            {"act": "flag", "fl": "frb"},
            {"act": "kick", "fl": "b", "goal": "gr"},
        ]
        planner = ActionPlanner(steps)
        bot = PlayerBot(squad_name=args.team, planner=planner, is_goalie=args.goalie)
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
