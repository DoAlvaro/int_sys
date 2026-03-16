"""Верхний уровень вратаря: ловля, выбивание, возврат к воротам."""
from layer_controller import LayerController


class HighLayerGoalie(LayerController):
    def __init__(self, side: str):
        super().__init__()
        self.side = side
        self.last = None
        self.step_without_home = 0
        self.ball_caught = False

    def _home_flag(self):
        return "gl" if self.side == "l" else "gr"

    def _dist_to_home(self, data):
        flags = data.get("flags", {})
        hf = self._home_flag()
        if hf in flags:
            return flags[hf].get("dist", None)
        goal_own = data.get("goal_own")
        if goal_own:
            return goal_own.get("dist", None)
        return None

    def process(self, input_data):
        if self.ball_caught:
            self.ball_caught = False
            self.last = "kick_after_catch"
            return self._kick_away(input_data)
        dist_home = self._dist_to_home(input_data)
        if not dist_home:
            self.step_without_home += 1
        ball = input_data.get("ball")
        if self.step_without_home > 63:
            if (not ball or ball.get("dist_change", 1) <= 0) or self.step_without_home > 99:
                self.step_without_home = 0
                self.last = "return"
                return {"new_action": "return_home"}
        if input_data.get("can_kick"):
            if ball and ball.get("dist", 9999) < 2.0:
                self.last = "catch"
                self.ball_caught = True
                return ("catch", str(int(ball.get("dir", 0))))
            self.last = "kick"
            return self._kick_away(input_data)
        if ball:
            ball_dist = ball.get("dist", 9999)
            ball_angle = ball.get("dir", 0)
            teammate_near = input_data.get("teammate_near_ball", False)
            if ball_dist < 2.0:
                self.last = "catch"
                self.ball_caught = True
                return ("catch", str(int(ball_angle)))
            if ball_dist > 15:
                if self.last == "return_":
                    if abs(ball_angle) > 5:
                        return ("turn", str(int(ball_angle)))
                    return None
                self.last = "return_"
                return {"new_action": "return_home"}
            if not teammate_near:
                self.last = "defend"
                return {"new_action": "go_to_ball"}
            if dist_home and dist_home > 6:
                self.last = "return"
                return {"new_action": "return_home"}
            if abs(ball_angle) > 5:
                return ("turn", str(int(ball_angle)))
            return None
        if dist_home and dist_home > 4:
            self.last = "return"
            return {"new_action": "return_home"}
        return None

    def _kick_away(self, data):
        best = data.get("best_pass_target")
        goal_opp = data.get("goal_opp")
        goal_own = data.get("goal_own")
        if best and not self._toward_own(best.get("dir", 0), goal_own):
            dist = best.get("dist", 10)
            return {"command": ("kick", f"{min(100, int(dist * 5 + 30))} {int(best.get('dir', 0))}"), "say": "pass"}
        if goal_opp:
            return ("kick", f"100 {int(goal_opp.get('dir', 0))}")
        if goal_own:
            return ("kick", f"100 {int(self._opposite(goal_own.get('dir', 0)))}")
        return ("kick", "100 0")

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
