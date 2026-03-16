"""Верхний уровень нападающего: пас, приём, позиция поддержки, удар по воротам."""
from layer_controller import LayerController

SUPPORT_FLAGS = {
    "forward_top": {"l": "frt10", "r": "flt10"},
    "forward_center": {"l": "fprc", "r": "fplc"},
    "forward_bottom": {"l": "frb10", "r": "flb10"},
}


class HighLayerForward(LayerController):
    def __init__(self, side: str, home_flag: str, attack_flag: str):
        super().__init__()
        self.side = side
        self.home_flag = home_flag
        self.attack_flag = attack_flag
        self.last = None
        self.role_key = ""

    def process(self, input_data):
        if not self.role_key:
            self.role_key = input_data.get("role_key", "")
        if input_data.get("can_kick"):
            return self._kick_decision(input_data)
        if input_data.get("pass_to_me"):
            self.last = "receive"
            return {"new_action": "receive_pass"}
        ball = input_data.get("ball")
        if ball:
            ball_dist = ball.get("dist", 9999)
            i_am_closest = input_data.get("i_am_closest_to_ball", True)
            teammate_near = input_data.get("teammate_near_ball", False)
            teammates_closer = input_data.get("teammates_closer_to_ball", 0)
            if teammate_near and not i_am_closest:
                return self._go_support(input_data, ball)
            if teammates_closer >= 2:
                return self._go_support(input_data, ball)
            if teammates_closer >= 1 and ball_dist > 15:
                return self._go_support(input_data, ball)
            if i_am_closest and ball_dist < 50:
                self.last = "go_ball"
                return {"new_action": "go_to_ball"}
            if ball_dist > 30:
                return self._go_support(input_data, ball)
            if ball_dist < 40:
                self.last = "go_ball"
                return {"new_action": "go_to_ball"}
        if self.last in ("go_ball", "kick", "receive", "dribble"):
            self.last = None
            return {"new_action": {"action": "go_to_flag", "flag": self.attack_flag}}
        if len(input_data.get("teammates", [])) > 2:
            self.last = "return_home"
            return {"new_action": "return_home"}
        return ("turn", "60")

    def _go_support(self, input_data, ball):
        ball_angle = ball.get("dir", 0) if ball else 0
        support_flag = SUPPORT_FLAGS.get(self.role_key, {}).get(self.side, self.attack_flag)
        if self.last != "support":
            self.last = "support"
            return {"new_action": {"action": "go_to_flag", "flag": support_flag}}
        if abs(ball_angle) > 10:
            return ("turn", str(int(ball_angle)))
        return None

    def _kick_decision(self, data):
        goal_opp = data.get("goal_opp")
        goal_own = data.get("goal_own")
        best = data.get("best_pass_target")
        if goal_opp:
            goal_dist = goal_opp.get("dist", 9999)
            goal_angle = goal_opp.get("dir", 0)
            if goal_dist < 30:
                self.last = "kick"
                return ("kick", f"{min(100, int(60 + goal_dist))} {int(goal_angle)}")
            if best:
                t_dir = best.get("dir", 0)
                t_dist = best.get("dist", 10)
                if not self._toward_own(t_dir, goal_own):
                    t_goal_diff = abs(t_dir - goal_angle)
                    if t_goal_diff > 180:
                        t_goal_diff = 360 - t_goal_diff
                    if t_goal_diff < 50 and t_dist < 30:
                        self.last = "kick"
                        return {"command": ("kick", f"{min(100, int(t_dist * 4 + 25))} {int(t_dir)}"), "say": "pass"}
            self.last = "kick"
            return ("kick", f"{min(100, int(40 + goal_dist))} {int(goal_angle)}")
        if best and not self._toward_own(best.get("dir", 0), goal_own):
            self.last = "kick"
            return {"command": ("kick", f"{min(100, int(best.get('dist', 10) * 4 + 25))} {int(best.get('dir', 0))}"), "say": "pass"}
        if goal_own:
            self.last = "kick"
            return ("kick", f"40 {int(self._opposite(goal_own.get('dir', 0)))}")
        min_flag = data.get("min_flag")
        if min_flag and str(min_flag)[-1].isdigit():
            return ("kick", "20 -180")
        return ("kick", "20 40")

    def _toward_own(self, kick_angle, goal_own):
        if not goal_own:
            return False
        d = abs(kick_angle - goal_own.get("dir", 0))
        if d > 180:
            d = 360 - d
        return d < 60

    def _opposite(self, angle):
        o = angle + 180
        if o > 180:
            o -= 360
        if o < -180:
            o += 360
        return o
