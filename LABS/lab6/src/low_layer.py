"""Нижний уровень: разбор see в структуру (мяч, ворота, флаги, тиммейты)."""
import math
from layer_controller import LayerController
from field_markers import FLAG_COORDS


def _closest_flag_key(visible: dict):
    flags = {k: v for k, v in visible.items() if k.startswith("f")}
    if not flags:
        return None, None
    closest = min(flags.items(), key=lambda x: x[1]["dist"])
    return closest[0], closest[1]["dist"]


class LowLayer(LayerController):
    def __init__(self, squad: str, side: str, role: str):
        super().__init__()
        self.team = squad
        self.side = side
        self.role = role
        self.player_number = 0
        self.role_key = ""

    def process(self, input_data):
        visible = input_data.get("visible", {})
        result = {
            "visible": visible,
            "play_on": input_data.get("play_on", False),
            "last_heard": input_data.get("last_heard_msg"),
            "referee_msg": input_data.get("referee_msg"),
            "team": self.team,
            "side": self.side,
            "player_number": self.player_number,
            "role": self.role,
            "role_key": self.role_key,
            "ball": None,
            "can_kick": False,
            "goal_own": None,
            "goal_opp": None,
            "flags": {},
            "teammates": [],
            "opponents": [],
            "teammate_near_ball": False,
            "i_am_closest_to_ball": True,
            "pass_to_me": False,
            "best_pass_target": None,
            "memory": self.memory,
            "teammates_closer_to_ball": 0,
            "my_ball_dist": 9999,
        }
        if "b" in visible:
            result["ball"] = visible["b"]
            result["my_ball_dist"] = visible["b"].get("dist", 9999)
            if visible["b"].get("dist", 9999) < 0.7:
                result["can_kick"] = True
        goal_own_key = "gl" if self.side == "l" else "gr"
        goal_opp_key = "gr" if self.side == "l" else "gl"
        if goal_own_key in visible:
            result["goal_own"] = visible[goal_own_key]
        if goal_opp_key in visible:
            result["goal_opp"] = visible[goal_opp_key]
        result["min_flag"] = _closest_flag_key(visible)[0]
        for key, obj in visible.items():
            if key in FLAG_COORDS:
                result["flags"][key] = obj
        for key, obj in visible.items():
            name = obj.get("name", [])
            if not isinstance(name, list) or len(name) < 2:
                continue
            if name[0] == "p":
                team_name = str(name[1]).strip('"')
                if team_name == self.team:
                    result["teammates"].append(obj)
                else:
                    result["opponents"].append(obj)
        self._ball_proximity(result)
        self._best_pass_target(result)
        if input_data.get("last_heard_msg") == "pass":
            result["pass_to_me"] = True
        return result

    def _ball_proximity(self, result):
        ball = result["ball"]
        if not ball:
            return
        my_d = ball.get("dist", 9999)
        ball_dir = ball.get("dir", 0)
        closer = 0
        for t in result["teammates"]:
            td = t.get("dist", 9999)
            tdir = t.get("dir", 0)
            angle_rad = math.radians(abs(ball_dir - tdir))
            t_to_ball_sq = my_d**2 + td**2 - 2 * my_d * td * math.cos(angle_rad)
            t_to_ball = math.sqrt(max(0, t_to_ball_sq))
            if t_to_ball < 1.5:
                result["teammate_near_ball"] = True
                result["i_am_closest_to_ball"] = False
                closer += 1
                continue
            if t_to_ball < my_d - 1.5:
                result["i_am_closest_to_ball"] = False
                closer += 1
        result["teammates_closer_to_ball"] = closer

    def _best_pass_target(self, result):
        teammates = result["teammates"]
        if not teammates:
            return
        goal_opp = result["goal_opp"]
        goal_own = result["goal_own"]
        opponents = result["opponents"]
        best = None
        best_score = -9999
        for t in teammates:
            td = t.get("dist", 9999)
            tdir = t.get("dir", 0)
            if td > 35 or td < 3:
                continue
            if goal_own:
                own_dir = goal_own.get("dir", 0)
                diff = abs(tdir - own_dir)
                if diff > 180:
                    diff = 360 - diff
                if diff < 60:
                    continue
            score = 50 - abs(td - 15)
            if goal_opp:
                gdir = goal_opp.get("dir", 0)
                d = abs(tdir - gdir)
                if d > 180:
                    d = 360 - d
                if d < 40:
                    score += 30
                elif d < 70:
                    score += 10
            for opp in opponents:
                od = opp.get("dist", 9999)
                oa = opp.get("dir", 0)
                if od < td and abs(oa - tdir) < 15:
                    score -= 40
            if score > best_score:
                best_score = score
                best = t
        if best and best_score > 0:
            result["best_pass_target"] = best

    def merge(self, own_result, upper_result):
        if upper_result and isinstance(upper_result, dict):
            if "command" in upper_result:
                return upper_result
            if "new_action" in upper_result:
                own_result["new_action"] = upper_result["new_action"]
        if upper_result and isinstance(upper_result, tuple):
            return upper_result
        if isinstance(own_result, dict) and "cmd" in own_result:
            return own_result["cmd"]
        return None
