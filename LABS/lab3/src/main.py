"""Точка входа lab3: дерево решений (игрок/вратарь)."""
import argparse
import json
import sys
from behavior_controller import BehaviorController
from player_bot import PlayerBot, InitFailedError


class LabRunner:
    @staticmethod
    def run_app():
        parser = argparse.ArgumentParser(description="Lab3 — дерево решений")
        parser.add_argument("--team", type=str, default="teamA")
        parser.add_argument("--x", type=int, default=-15)
        parser.add_argument("--y", type=int, default=0)
        parser.add_argument("--goalie", action="store_true")
        parser.add_argument("--actions", type=str)
        args = parser.parse_args()
        step_list = json.loads(args.actions) if args.actions else []
        controller = BehaviorController(step_list, is_goalie=args.goalie)
        bot = PlayerBot(squad_name=args.team, controller=controller, is_goalie=args.goalie)
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
