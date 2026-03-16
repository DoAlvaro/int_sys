"""Точка входа lab4: passer / scorer / goalie."""
import argparse
import sys
from behavior_controller import BehaviorController
from player_bot import PlayerBot, InitFailedError


class LabRunner:
    @staticmethod
    def run_app():
        parser = argparse.ArgumentParser(description="Lab4 — координация (passer/scorer)")
        parser.add_argument("--team", type=str, default="teamA")
        parser.add_argument("--x", type=int, default=-15)
        parser.add_argument("--y", type=int, default=0)
        parser.add_argument("--goalie", action="store_true")
        parser.add_argument("--role", type=str, choices=["passer", "scorer"], default="passer")
        args = parser.parse_args()
        controller = BehaviorController(is_goalie=args.goalie, role=args.role)
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
