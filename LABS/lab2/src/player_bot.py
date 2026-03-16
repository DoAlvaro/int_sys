"""Агент-игрок с планировщиком действий: see/hear, позиции, команды по плану."""
import time
from udp_connection import UdpConnection
from field_markers import FLAG_COORDS, parts_to_key
from protocol_decoder import ProtocolDecoder
from position_calculator import PositionCalculator
from action_planner import ActionPlanner


class InitFailedError(Exception):
    pass


class PlayerBot:
    def __init__(self, squad_name: str, planner: ActionPlanner, protocol_version: int = 7, is_goalie: bool = False):
        self._squad = squad_name
        self._version = protocol_version
        self._is_goalie = is_goalie
        self._side = None
        self._unum = None
        self._play_mode = None
        self._channel = UdpConnection()
        self._game_active = False
        self._running = False
        self._pos_x = None
        self._pos_y = None
        self._seen = {}
        self._planner = planner

    def connect_to_server(self):
        goalie_suffix = " (goalie)" if self._is_goalie else ""
        cmd = f"(init {self._squad} (version {self._version}){goalie_suffix})"
        self._channel.write(cmd)
        deadline = time.time() + 5
        while time.time() < deadline:
            data = self._channel.read_next()
            if data and self._handle_init(data):
                return
        self.shutdown()
        raise InitFailedError("Нет ответа инициализации от сервера")

    def _handle_init(self, data: str) -> bool:
        parsed = ProtocolDecoder.from_string(data)
        if not parsed or parsed[0] != "init":
            return False
        self._side = parsed[1]
        self._unum = parsed[2]
        self._play_mode = parsed[3] if len(parsed) > 3 else None
        return True

    def go_to(self, x: float, y: float):
        self._channel.write(f"(move {x} {y})")

    def rotate_body(self, moment: float):
        self._channel.write(f"(turn {moment})")

    def dash(self, power: float):
        self._channel.write(f"(dash {power})")

    def kick(self, power: float, direction: float):
        self._channel.write(f"(kick {power} {direction})")

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
        text = parsed[3] if len(parsed) > 3 else ""
        if sender != "referee":
            return
        text_str = str(text)
        print(f"рефери говорит: {text_str}")
        if text_str == "play_on":
            self._game_active = True
        elif text_str.startswith("kick_off"):
            self._game_active = False
        elif text_str.startswith("goal_"):
            self._game_active = False
            self._planner.reset_to_start()

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
        self._estimate_self_position()
        self._estimate_others_positions()
        decision = self._planner.choose_command(self._seen, self._game_active)
        if decision:
            cmd, params = decision
            self._send_cmd(cmd, params)

    def _estimate_self_position(self):
        flag_obs = [(k, o["dist"]) for k, o in self._seen.items() if k in FLAG_COORDS]
        if len(flag_obs) < 2:
            return
        k1, d1 = flag_obs[0]
        k2, d2 = flag_obs[1]
        if len(flag_obs) >= 3:
            k3, d3 = flag_obs[2]
            pos = PositionCalculator.position_from_three_flags(k1, d1, k2, d2, k3, d3)
            if pos is None:
                pos = PositionCalculator.position_from_two_flags(k1, d1, k2, d2)
        else:
            pos = PositionCalculator.position_from_two_flags(k1, d1, k2, d2)
        if pos is None:
            return
        if isinstance(pos, list) and len(pos) >= 1:
            pos = pos[0]
        if pos:
            self._pos_x, self._pos_y = pos
            print(f"Позиция игрока x={self._pos_x:.2f}, y={self._pos_y:.2f}")

    def _estimate_others_positions(self):
        if self._pos_x is None or self._pos_y is None:
            return
        ref = None
        for key, obj in self._seen.items():
            if key in FLAG_COORDS and "dir" in obj:
                ref = (key, obj["dist"], obj["dir"])
                break
        if ref is None:
            return
        fk, fd, fa = ref
        for key, obj in self._seen.items():
            if key in FLAG_COORDS or "dir" not in obj:
                continue
            pos = PositionCalculator.position_of_object(
                self._pos_x, self._pos_y, fk, fd, fa, obj["dist"], obj["dir"]
            )
            if pos:
                obj["computed_x"] = pos[0]
                obj["computed_y"] = pos[1]
                name_parts = obj.get("name", [])
                if name_parts and name_parts[0] == "p":
                    team = name_parts[1] if len(name_parts) > 1 else "?"
                    num = name_parts[2] if len(name_parts) > 2 else "?"
                    print(f"Игрок {team}#{num}: x={pos[0]:.2f}, y={pos[1]:.2f}")
                elif name_parts and name_parts[0] == "b":
                    print(f"Мяч: x={pos[0]:.2f}, y={pos[1]:.2f}")

    def run(self, start_pos: tuple):
        self.connect_to_server()
        self.go_to(*start_pos)
        self._running = True
        print(f"Команда: {self._squad}, номер: {self._unum}, сторона: {self._side}, начальная позиция: {start_pos}")
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
        print("Агент остановлен")
