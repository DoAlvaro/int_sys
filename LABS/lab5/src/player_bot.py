"""Агент с таблицей действий: после init создаётся контроллер по role/side/unum."""
import time
from udp_connection import UdpConnection
from field_markers import parts_to_key
from protocol_decoder import ProtocolDecoder
from behavior_controller import BehaviorController


class InitFailedError(Exception):
    pass


class PlayerBot:
    def __init__(self, squad_name: str, role: str, protocol_version: int = 7):
        self._squad = squad_name
        self._version = protocol_version
        self._role = role
        self._side = None
        self._unum = None
        self._channel = UdpConnection()
        self._game_active = False
        self._running = False
        self._seen = {}
        self._controller = None  # создаётся после connect

    def connect_to_server(self):
        goalie_suffix = " (goalie)" if self._role == "goalie" else ""
        cmd = f"(init {self._squad} (version {self._version}){goalie_suffix})"
        self._channel.write(cmd)
        deadline = time.time() + 5
        while time.time() < deadline:
            data = self._channel.read_next()
            if data and self._handle_init(data):
                break
        else:
            self.shutdown()
            raise InitFailedError("Нет ответа инициализации от сервера")
        self._controller = BehaviorController(
            role=self._role,
            squad=self._squad,
            side=self._side,
            unum=self._unum,
        )

    def _handle_init(self, data: str) -> bool:
        parsed = ProtocolDecoder.from_string(data)
        if not parsed or parsed[0] != "init":
            return False
        self._side = parsed[1]
        self._unum = parsed[2]
        return True

    def go_to(self, x: float, y: float):
        self._channel.write(f"(move {x} {y})")

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
            print(f"рефери говорит: {text}")
            if text == "play_on":
                self._game_active = True
            elif text.startswith("kick_off"):
                self._game_active = False
            elif text.startswith("goal_"):
                self._game_active = False
                if self._controller:
                    self._controller.reset_state()

    def _handle_see(self, parsed: list):
        if len(parsed) < 2 or not self._controller:
            return
        time_cycle = int(parsed[1]) if len(parsed) > 1 else 0
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
        decision = self._controller.choose_command(
            self._seen,
            self._game_active,
            squad=self._squad,
            side=self._side or "",
            unum=self._unum or 0,
            time_cycle=time_cycle,
        )
        if decision:
            cmd, params = decision
            self._send_cmd(cmd, params)

    def run(self, start_pos: tuple):
        self.connect_to_server()
        self.go_to(*start_pos)
        self._running = True
        print(
            f"Команда: {self._squad}, номер: {self._unum}, сторона: {self._side}, "
            f"позиция: {start_pos}, роль: {self._role}"
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
        print("Агент остановлен")
