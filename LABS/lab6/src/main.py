"""Точка входа lab6: команда с ролями (goalie, defender_*, forward_*)."""
import argparse
import sys
from low_layer import LowLayer
from mid_layer import MidLayer
from high_layer_goalie import HighLayerGoalie
from high_layer_defender import HighLayerDefender
from high_layer_forward import HighLayerForward
from player_bot import PlayerBot, InitFailedError

ROLE_CONFIG = {
    "l": {
        "goalie": {"home_flag": "gl", "start_pos": (-50, 0)},
        "defender_top": {"home_flag": "fplt", "start_pos": (-36, -20)},
        "defender_center": {"home_flag": "fplc", "start_pos": (-36, 0)},
        "defender_bottom": {"home_flag": "fplb", "start_pos": (-36, 20)},
        "forward_top": {"home_flag": "fct", "attack_flag": "fprt", "start_pos": (-5, -20)},
        "forward_center": {"home_flag": "fc", "attack_flag": "fprc", "start_pos": (-10, 0)},
        "forward_bottom": {"home_flag": "fcb", "attack_flag": "fprb", "start_pos": (-5, 20)},
    },
    "r": {
        "goalie": {"home_flag": "gr", "start_pos": (-50, 0)},
        "defender_top": {"home_flag": "fprt", "start_pos": (-36, 20)},
        "defender_center": {"home_flag": "fprc", "start_pos": (-36, 0)},
        "defender_bottom": {"home_flag": "fprb", "start_pos": (-36, -20)},
        "forward_top": {"home_flag": "fct", "attack_flag": "fplt", "start_pos": (-5, 20)},
        "forward_center": {"home_flag": "fc", "attack_flag": "fplc", "start_pos": (-10, 0)},
        "forward_bottom": {"home_flag": "fcb", "attack_flag": "fplb", "start_pos": (-5, -20)},
    },
}


def create_agent(team: str, role_key: str, side_hint: str = "l"):
    config = ROLE_CONFIG[side_hint][role_key]
    home_flag = config["home_flag"]
    start_pos = config["start_pos"]
    is_goalie = role_key == "goalie"
    base_role = "goalie" if role_key == "goalie" else ("defender" if role_key.startswith("defender") else "forward")
    low = LowLayer(squad=team, side=side_hint, role=base_role)
    mid = MidLayer(home_flag=home_flag, role=base_role, side=side_hint)
    if base_role == "goalie":
        high = HighLayerGoalie(side=side_hint)
    elif base_role == "defender":
        high = HighLayerDefender(side=side_hint, home_flag=home_flag)
    else:
        attack_flag = config.get("attack_flag", "fc")
        high = HighLayerForward(side=side_hint, home_flag=home_flag, attack_flag=attack_flag)
        high.role_key = role_key
    agent = PlayerBot(
        squad_name=team,
        controllers=[low, mid, high],
        is_goalie=is_goalie,
        role=role_key,
        home_flag=home_flag,
    )
    return agent, start_pos


def main():
    parser = argparse.ArgumentParser(description="Lab6 — командная игра")
    parser.add_argument("--team", type=str, default="teamA")
    parser.add_argument(
        "--role",
        type=str,
        default="forward_center",
        choices=[
            "goalie",
            "defender_top", "defender_center", "defender_bottom",
            "forward_top", "forward_center", "forward_bottom",
        ],
    )
    parser.add_argument("--side", type=str, default="l", choices=["l", "r"])
    args = parser.parse_args()
    agent, start_pos = create_agent(args.team, args.role, args.side)
    try:
        agent.run(start_pos=start_pos)
    except KeyboardInterrupt:
        agent.shutdown()
    except (InitFailedError, Exception) as e:
        print(e)
        agent.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
