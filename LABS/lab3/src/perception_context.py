"""Контекст восприятия: видимые объекты, команда, позиция, тиммейты."""
# noqa: D100


class PerceptionContext:
    """Данные для дерева решений: обновляются каждый такт."""

    def __init__(self):
        self._obs = {}
        self._squad = ""
        self._side = ""
        self._unum = 0
        self._pos_x = None
        self._pos_y = None

    def set_observation(
        self,
        visible: dict,
        squad: str = "",
        side: str = "",
        unum: int = 0,
        pos_x=None,
        pos_y=None,
    ):
        self._obs = visible
        self._squad = squad
        self._side = side
        self._unum = unum
        self._pos_x = pos_x
        self._pos_y = pos_y

    def is_visible(self, key: str) -> bool:
        return key in self._obs

    def distance_to(self, key: str) -> float:
        if key in self._obs:
            return self._obs[key].get("dist", 9999)
        return 9999

    def dist_change(self, key: str) -> float:
        if key in self._obs:
            return self._obs[key].get("dist_change", 0)
        return 0

    def angle_to(self, key: str) -> float:
        if key in self._obs:
            return self._obs[key].get("dir", 0)
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
