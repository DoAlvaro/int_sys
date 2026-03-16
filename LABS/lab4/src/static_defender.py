"""Статичный защитник (teamB): занимает позицию, dash 0 / turn 0 в play_on."""
import time
import argparse
import sys
from udp_connection import UdpConnection
from protocol_decoder import ProtocolDecoder


class StaticDefenderAgent:
    """Защитник: init, move к позиции, в play_on — dash 0."""

    def __init__(self, squad_name: str, target_x: float, target_y: float, protocol_version: int = 7):
        self._squad = squad_name
        self._version = protocol_version
        self._target_x = target_x
        self._target_y = target_y
        self._channel = UdpConnection()
        self._running = False
        self._unum = None
        self._side = None
        self._game_active = False

    def connect(self):
        cmd = f"(init {self._squad} (version {self._version}))"
        self._channel.write(cmd)
        deadline = time.time() + 5
        while time.time() < deadline:
            data = self._channel.read_next()
            if data and self._handle_init(data):
                return
        self.shutdown()
        raise RuntimeError("Нет ответа инициализации от сервера")

    def _handle_init(self, data: str) -> bool:
        parsed = ProtocolDecoder.from_string(data)
        if not parsed or parsed[0] != "init":
            return False
        self._side = parsed[1]
        self._unum = parsed[2]
        return True

    def go_to(self, x: float, y: float):
        self._channel.write(f"(move {x} {y})")

    def dash(self, power: float):
        self._channel.write(f"(dash {power})")

    def run(self):
        self.connect()
        self.go_to(self._target_x, self._target_y)
        print(f"Защитник {self._squad} #{self._unum}: цель ({self._target_x}, {self._target_y})")
        self._running = True
        while self._running:
            data = self._channel.read_next()
            if not data:
                continue
            parsed = ProtocolDecoder.from_string(data)
            if not parsed:
                continue
            if parsed[0] == "see":
                if self._game_active:
                    self.dash(0)
            elif parsed[0] == "hear" and len(parsed) >= 4 and parsed[2] == "referee":
                msg = str(parsed[3])
                if msg.startswith("play_on"):
                    self._game_active = True
                    self.go_to(self._target_x, self._target_y)
                    print("play_on — защитник на позиции")
                elif msg.startswith("goal_") or msg.startswith("kick_off"):
                    self._game_active = False
                    self.go_to(self._target_x, self._target_y)
                    print(f"Защитник возврат на позицию ({self._target_x}, {self._target_y})")

    def shutdown(self):
        self._running = False
        try:
            self._channel.write("(bye)")
            self._channel.close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Lab4 — статичный защитник")
    parser.add_argument("--team", type=str, default="teamB")
    parser.add_argument("--x", type=float, default=47.0)
    parser.add_argument("--y", type=float, default=6.0)
    args = parser.parse_args()
    agent = StaticDefenderAgent(squad_name=args.team, target_x=args.x, target_y=args.y)
    try:
        agent.run()
    except KeyboardInterrupt:
        agent.shutdown()
    except Exception as e:
        print(e)
        agent.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
