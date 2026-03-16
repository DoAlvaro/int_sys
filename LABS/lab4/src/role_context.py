"""Контекст для ролевых деревьев: видимое, сторона, последнее услышанное сообщение."""
# noqa: D100


class RoleContext:
    """Данные для passer/scorer/goalie: обновляются каждый такт, включая last_heard_msg."""

    def __init__(self):
        self._obs = {}
        self._squad = ""
        self._side = ""
        self._unum = 0
        self._pos_x = None
        self._pos_y = None
        self._last_heard = None

    def set_observation(
        self,
        visible: dict,
        squad: str = "",
        side: str = "",
        unum: int = 0,
        pos_x=None,
        pos_y=None,
        last_heard_msg=None,
    ):
        self._obs = visible
        self._squad = squad
        self._side = side
        self._unum = unum
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._last_heard = last_heard_msg

    @property
    def last_heard_msg(self):
        return self._last_heard

    def goal_flag(self) -> str:
        """Флаг ворот для атаки."""
        return "gr" if self._side == "l" else "gl"

    def center_flag(self) -> str:
        """Центральный флаг своей половины."""
        return "fplc" if self._side == "l" else "fprc"

    def corner_flag(self) -> str:
        """Угловой флаг своей половины (верхний)."""
        return "fplb" if self._side == "l" else "fprb"

    def goal_corner_flag(self) -> str:
        """Флаг у чужих ворот (для скорера)."""
        return "fgrb" if self._side == "l" else "fglt"

    def is_visible(self, key: str) -> bool:
        return key in self._obs

    def distance_to(self, key: str) -> float:
        if key in self._obs:
            return self._obs[key].get("dist", 9999)
        return 9999

    def angle_to(self, key: str) -> float:
        if key in self._obs:
            return self._obs[key].get("dir", 0)
        return 0

    def dist_change(self, key: str) -> float:
        if key in self._obs:
            return self._obs[key].get("dist_change", 0)
        return 0

    def list_teammates(self) -> list:
        out = []
        for k, obj in self._obs.items():
            name = obj.get("name", [])
            if not isinstance(name, list) or len(name) < 2:
                continue
            if name[0] == "p" and str(name[1]).strip('"') == self._squad:
                out.append((k, obj))
        return out

    def teammate_count(self) -> int:
        return len(self.list_teammates())

    def closest_teammate(self):
        lst = self.list_teammates()
        if not lst:
            return None
        return min(lst, key=lambda t: t[1].get("dist", 9999))
