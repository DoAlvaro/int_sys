"""Контекст для таблиц действий: видимое, команда, сторона, номер, цикл."""
# noqa: D100


class TAContext:
    def __init__(self):
        self._obs = {}
        self._squad = ""
        self._side = ""
        self._unum = 0
        self._time_cycle = 0

    def set_observation(
        self,
        visible: dict,
        squad: str = "",
        side: str = "",
        unum: int = 0,
        time_cycle: int = 0,
    ):
        self._obs = visible
        self._squad = squad
        self._side = side
        self._unum = unum
        self._time_cycle = time_cycle

    @property
    def time_cycle(self) -> int:
        return self._time_cycle

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

    def list_teammates(self) -> list:
        out = []
        for k, obj in self._obs.items():
            name = obj.get("name", [])
            if not isinstance(name, list) or len(name) < 2:
                continue
            if name[0] == "p" and str(name[1]).strip('"') == self._squad:
                if len(name) >= 3:
                    try:
                        if int(name[2]) == self._unum:
                            continue
                    except (ValueError, IndexError, TypeError):
                        pass
                out.append((k, obj))
        return out

    def teammate_count(self) -> int:
        return len(self.list_teammates())

    def closest_teammate(self):
        lst = self.list_teammates()
        if not lst:
            return None
        return min(lst, key=lambda t: t[1].get("dist", 9999))

    def list_enemies(self) -> list:
        out = []
        for k, obj in self._obs.items():
            name = obj.get("name", [])
            if not isinstance(name, list) or len(name) < 2:
                continue
            if name[0] == "p" and str(name[1]).strip('"') != self._squad:
                out.append((k, obj))
        return out

    def closest_enemy(self):
        lst = self.list_enemies()
        if not lst:
            return None
        return min(lst, key=lambda t: t[1].get("dist", 9999))

    def is_runner(self) -> bool:
        return self._unum % 2 == 1

    def is_passer(self) -> bool:
        return self._unum % 2 == 0

    def is_upper_defender(self) -> bool:
        return self._unum % 2 == 1

    def is_lower_defender(self) -> bool:
        return self._unum % 2 == 0

    def own_goal_key(self) -> str:
        return "gl" if self._side == "l" else "gr"

    def enemy_goal_key(self) -> str:
        return "gr" if self._side == "l" else "gl"

    def own_penalty_center_flag(self) -> str:
        return "fplc" if self._side == "l" else "fprc"

    def own_goal_top_flag(self) -> str:
        return "fglt" if self._side == "l" else "fgrt"

    def own_goal_bottom_flag(self) -> str:
        return "fglb" if self._side == "l" else "fgrb"

    def teammate_is_closer_to_ball(self) -> bool:
        if not self.is_visible("b"):
            return False
        my_d = self.distance_to("b")
        closest = self.closest_teammate()
        if not closest:
            return False
        tm_d = closest[1].get("dist", 9999)
        tm_dir = closest[1].get("dir", 0)
        ball_dir = self.angle_to("b")

        def norm(a):
            while a > 180:
                a -= 360
            while a < -180:
                a += 360
            return a

        if abs(norm(tm_dir - ball_dir)) < 30 and tm_d < my_d:
            return True
        if tm_d + 3 < my_d:
            return True
        return False
