"""Точка входа: разбор аргументов, создание агента, запуск цикла."""
import argparse
import sys

from player_bot import PlayerBot, InitFailedError


class LabRunner:
    """Запуск лабораторного агента с параметрами из командной строки."""

    @staticmethod
    def run_app():
        parser = argparse.ArgumentParser(description="Lab1 — агент RoboCup 2D")
        parser.add_argument("--team", type=str, default="teamA")
        parser.add_argument("--x", type=int, default=-15)
        parser.add_argument("--y", type=int, default=0)
        parser.add_argument("--rotation", type=float, default=10.0)
        parser.add_argument("--goalie", action="store_true")
        args = parser.parse_args()
        turn_speed = args.rotation or 0.0
        bot = PlayerBot(squad_name=args.team, is_goalie=args.goalie)
        try:
            bot.run(start_pos=(args.x, args.y), rotation_angel=turn_speed)
        except KeyboardInterrupt:
            bot.shutdown()
        except InitFailedError as e:
            print(e)
            bot.shutdown()
            sys.exit(1)
        except Exception as e:
            print(e)
            bot.shutdown()
            sys.exit(1)


if __name__ == "__main__":
    LabRunner.run_app()
