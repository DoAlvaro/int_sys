"""Агент с иерархией контроллеров: low -> mid -> high."""
import time
from udp_connection import UdpConnection
from field_markers import parts_to_key
from protocol_decoder import ProtocolDecoder


class InitFailedError(Exception):
    pass


class PlayerBot:
    def __init__(
        self,
        squad_name: str,
        controllers: list,
        protocol_version: int = 7,
        is_goalie: bool = False,
        role: str = "forward",
        home_flag: str = "fc",
    ):
        self._squad = squad_name
        self._version = protocol_version
        self._is_goalie = is_goalie
        self._role = role
        self._home_flag = home_flag
        self._side = None
        self._unum = None
        self._channel = UdpConnection()
        self._game_active = False
        self._running = False
        self._seen = {}
        self._controllers = controllers
        self._start_pos = (-15, 0)
        self._last_heard_msg = None
        self._referee_msg = None

    def connect_to_server(self):
        goalie_suffix = " (goalie)" if self._is_goalie else ""
        cmd = f"(init {self._squad} (version {self._version}){goalie_suffix})"
        self._channel.write(cmd)
        deadline = time.time() + 5
        while time.time() < deadline:
            data = self._channel.read_next()
            if data and self._handle_init(data):
                break
        else:
            self.shutdown()
            raise InitFailedError("Нет ответа init от сервера")

    def _handle_init(self, data: str) -> bool:
        parsed = ProtocolDecoder.from_string(data)
        if not parsed or parsed[0] != "init":
            return False
        self._side = parsed[1]
        self._unum = parsed[2]
        self._sync_controllers()
        return True

    def _sync_controllers(self):
        if not self._controllers:
            return
        low = self._controllers[0]
        low.side = self._side
        low.team = self._squad
        low.player_number = self._unum
        low.role_key = self._role
        for ctrl in self._controllers:
            if hasattr(ctrl, "side"):
                ctrl.side = self._side

    def go_to(self, x: float, y: float):
        self._channel.write(f"(move {x} {y})")

    def say(self, msg: str):
        self._channel.write(f"(say {msg})")

    def _send_cmd(self, cmd: str, params: str):
        self._channel.write(f"({cmd} {params})")

    def handle_message(self, msg: str):
        parsed = ProtocolDecoder.from_string(msg)
        if not parsed:
            return
        kind = parsed[0]
        if kind == "see":
            self._handle_see(parsed)
        elif kind == "hear":
            self._handle_hear(parsed)

    def _handle_hear(self, parsed: list):
        if len(parsed) < 4:
            return
        sender = parsed[2]
        text = str(parsed[3]) if len(parsed) > 3 else ""
        if sender == "referee":
            self._referee_msg = text
            if text == "play_on":
                self._game_active = True
            elif text.startswith("kick_off"):
                self._game_active = False
            elif text.startswith("goal_"):
                self._game_active = False
                self.go_to(*self._start_pos)
                if len(self._controllers) > 1:
                    mid = self._controllers[1]
                    mid.action = "go_to_flag"
                    mid.target_flag = mid.home_flag
                if len(self._controllers) > 2:
                    high = self._controllers[2]
                    if hasattr(high, "ball_caught"):
                        high.ball_caught = False
        else:
            self._last_heard_msg = text

    def _handle_see(self, parsed: list):
        if len(parsed) < 2:
            return
        self._seen = {}
        for i in range(2, len(parsed)):
            obj_info = parsed[i]
            if not isinstance(obj_info, list) or len(obj_info) < 2:
                continue
            name_raw = obj_info[0]
            params = obj_info[1:]
            if not isinstance(name_raw, list):
                continue
            key = parts_to_key(name_raw)
            entry = {"name": name_raw, "dist": float(params[0])}
            if len(params) >= 2:
                entry["dir"] = float(params[1])
            if len(params) >= 3:
                entry["dist_change"] = float(params[2])
            if len(params) >= 4:
                entry["dir_change"] = float(params[3])
            if len(params) >= 5:
                entry["body_facing_dir"] = float(params[4])
            if len(params) >= 6:
                entry["head_facing_dir"] = float(params[5])
            self._seen[key] = entry
        if not self._game_active:
            self._last_heard_msg = None
            return
        input_data = {
            "visible": self._seen,
            "play_on": self._game_active,
            "last_heard_msg": self._last_heard_msg,
            "referee_msg": self._referee_msg,
        }
        low = self._controllers[0]
        upper = self._controllers[1:]
        result = low.execute(input_data, upper)
        if result and isinstance(result, tuple) and len(result) == 2:
            cmd, params = result
            self._send_cmd(cmd, params)
        elif result and isinstance(result, dict):
            if "command" in result:
                ct = result["command"]
                if ct and isinstance(ct, tuple) and len(ct) == 2:
                    self._send_cmd(ct[0], ct[1])
            if result.get("say"):
                self.say(result["say"])
        self._last_heard_msg = None
        self._referee_msg = None

    def run(self, start_pos: tuple):
        self._start_pos = start_pos
        self.connect_to_server()
        self.go_to(*start_pos)
        self._running = True
        print(
            f"[{self._squad}] #{self._unum} side={self._side} role={self._role} "
            f"home_flag={self._home_flag} pos={start_pos} goalie={self._is_goalie}"
        )
        while self._running:
            data = self._channel.read_next()
            if data:
                self.handle_message(data)

    def shutdown(self):
        self._running = False
        try:
            self._channel.write("(bye)")
            self._channel.close()
        except Exception:
            pass
        print(f"Агент {self._role}#{self._unum} остановлен")
