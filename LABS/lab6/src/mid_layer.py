"""Средний уровень: действия go_to_flag, scan_field, go_to_ball, return_home, receive_pass, watch_ball."""
from layer_controller import LayerController


class MidLayer(LayerController):
    def __init__(self, home_flag: str, role: str, side: str):
        super().__init__()
        self.home_flag = home_flag
        self.role = role
        self.side = side
        self.action = "go_to_flag"
        self.target_flag = home_flag
        self.scan_steps = 0
        self.return_steps = 0

    def process(self, input_data):
        result = dict(input_data)
        result["cmd"] = None
        result["mid_action"] = self.action
        result["at_home"] = self._at_home(input_data)
        if input_data.get("pass_to_me") and self.action != "receive_pass":
            self.action = "receive_pass"
            self.return_steps = 0
        if self.action == "go_to_flag":
            result["cmd"] = self._go_to_flag(input_data)
        elif self.action == "scan_field":
            result["cmd"] = self._scan_field(input_data)
        elif self.action == "go_to_ball":
            result["cmd"] = self._go_to_ball(input_data)
        elif self.action == "return_home":
            result["cmd"] = self._return_home(input_data)
        elif self.action == "receive_pass":
            result["cmd"] = self._receive_pass(input_data)
        elif self.action == "watch_ball":
            result["cmd"] = self._watch_ball(input_data)
        result["memory"].update(self.memory)
        return result

    def merge(self, own_result, upper_result):
        if upper_result and isinstance(upper_result, dict):
            if "command" in upper_result:
                return upper_result
            if "new_action" in upper_result:
                na = upper_result["new_action"]
                if isinstance(na, dict):
                    name = na.get("action", "go_to_flag")
                    if "flag" in na:
                        self.target_flag = na["flag"]
                    self._switch(name)
                else:
                    self._switch(na)
                return self.process(own_result).get("cmd")
        if upper_result and isinstance(upper_result, tuple):
            return upper_result
        return own_result.get("cmd")

    def _switch(self, new_action):
        if new_action == "return_home":
            self.target_flag = self.home_flag
            self.return_steps = 0
        self.action = new_action

    def _at_home(self, data):
        flags = data.get("flags", {})
        if self.home_flag in flags:
            return flags[self.home_flag].get("dist", 9999) < 3
        return False

    def _return_home(self, data):
        flags = data.get("flags", {})
        if self.home_flag in flags:
            obj = flags[self.home_flag]
            dist = obj.get("dist", 9999)
            angle = obj.get("dir", 0)
            if dist < 3:
                self.action = "watch_ball"
                self.return_steps = 0
                return self._watch_ball(data)
            if abs(angle) > 10:
                return ("turn", str(int(angle)))
            return ("dash", str(min(100, int(dist * 4 + 40))))
        self.return_steps += 1
        if self.return_steps > 12:
            self.return_steps = 0
            return ("dash", "30")
        return ("turn", "60")

    def _go_to_flag(self, data):
        flags = data.get("flags", {})
        if self.target_flag in flags:
            obj = flags[self.target_flag]
            dist = obj.get("dist", 9999)
            angle = obj.get("dir", 0)
            if dist < 3:
                self.action = "scan_field"
                return ("turn", "60")
            if abs(angle) > 10:
                return ("turn", str(int(angle)))
            return ("dash", str(min(100, int(dist * 2 + 30))))
        return ("turn", "60")

    def _scan_field(self, data):
        if data.get("ball"):
            return None
        return ("turn", "60")

    def _go_to_ball(self, data):
        ball = data.get("ball")
        if not ball:
            return ("turn", "60")
        angle = ball.get("dir", 0)
        dist = ball.get("dist", 9999)
        if dist < 0.7:
            return None
        if abs(angle) > 5:
            return ("turn", str(int(angle)))
        return ("dash", str(min(100, int(dist * 8 + 50))))

    def _receive_pass(self, data):
        ball = data.get("ball")
        if not ball:
            return ("turn", "40")
        angle = ball.get("dir", 0)
        dist = ball.get("dist", 9999)
        if dist < 0.7:
            self.action = "scan_field"
            return None
        if abs(angle) > 5:
            return ("turn", str(int(angle)))
        return ("dash", str(min(100, int(dist * 10 + 50))))

    def _watch_ball(self, data):
        ball = data.get("ball")
        if not ball:
            return ("turn", "40")
        angle = ball.get("dir", 0)
        if abs(angle) > 5:
            return ("turn", str(int(angle)))
        return None
