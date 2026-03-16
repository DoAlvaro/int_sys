"""Вычисление позиций по расстояниям до флагов (триангуляция)."""
import math
from field_markers import FLAG_COORDS

BOUND_X = 55
BOUND_Y = 35


class PositionCalculator:
    """Класс для расчёта координат по наблюдениям за флагами и объектами."""

    @staticmethod
    def position_from_two_flags(
        key1: str, dist1: float, key2: str, dist2: float
    ):
        """Позиция по расстояниям до двух флагов. Возвращает список решений или None."""
        x1, y1 = FLAG_COORDS[key1]
        x2, y2 = FLAG_COORDS[key2]
        candidates = PositionCalculator._intersect_circles(x1, y1, dist1, x2, y2, dist2)
        if not candidates:
            return None
        in_bounds = [
            (cx, cy)
            for cx, cy in candidates
            if -BOUND_X <= cx <= BOUND_X and -BOUND_Y <= cy <= BOUND_Y
        ]
        return in_bounds if in_bounds else candidates

    @staticmethod
    def _intersect_circles(xa, ya, ra, xb, yb, rb):
        """Точки пересечения двух окружностей. Возвращает список пар (x, y)."""
        out = []
        eps = 1e-9
        if abs(xb - xa) < eps and abs(yb - ya) < eps:
            return []
        if abs(xb - xa) < eps:
            y = (yb**2 - ya**2 + ra**2 - rb**2) / (2 * (yb - ya))
            det = ra**2 - (y - ya) ** 2
            if det < 0:
                return []
            det = max(det, 0)
            sq = math.sqrt(det)
            out.append((xa + sq, y))
            out.append((xa - sq, y))
            return out
        if abs(yb - ya) < eps:
            x = (xb**2 - xa**2 + ra**2 - rb**2) / (2 * (xb - xa))
            det = ra**2 - (x - xa) ** 2
            if det < 0:
                return []
            det = max(det, 0)
            sq = math.sqrt(det)
            out.append((x, ya + sq))
            out.append((x, ya - sq))
            return out
        alpha = (ya - yb) / (xb - xa)
        beta = (yb**2 - ya**2 + xb**2 - xa**2 + ra**2 - rb**2) / (2 * (xb - xa))
        a2 = alpha**2 + 1
        b2 = -2 * (alpha * (xa - beta) + ya)
        c2 = (xa - beta) ** 2 + ya**2 - ra**2
        disc = b2**2 - 4 * a2 * c2
        if disc < 0:
            return []
        sq_d = math.sqrt(disc)
        y1 = (-b2 + sq_d) / (2 * a2)
        y2 = (-b2 - sq_d) / (2 * a2)
        x1 = alpha * y1 + beta
        x2 = alpha * y2 + beta
        out.append((x1, y1))
        if abs(y1 - y2) > eps or abs(x1 - x2) > eps:
            out.append((x2, y2))
        return out

    @staticmethod
    def position_from_three_flags(
        key1: str, d1: float, key2: str, d2: float, key3: str, d3: float
    ):
        """Одна позиция по трём флагам (однозначное решение)."""
        x1, y1 = FLAG_COORDS[key1]
        x2, y2 = FLAG_COORDS[key2]
        x3, y3 = FLAG_COORDS[key3]
        eps = 1e-9
        if abs(x2 - x1) < eps or abs(x3 - x1) < eps:
            return PositionCalculator.position_from_two_flags(key1, d1, key2, d2)
        a1 = (y1 - y2) / (x2 - x1)
        b1 = (y2**2 - y1**2 + x2**2 - x1**2 + d1**2 - d2**2) / (2 * (x2 - x1))
        a2 = (y1 - y3) / (x3 - x1)
        b2 = (y3**2 - y1**2 + x3**2 - x1**2 + d1**2 - d3**2) / (2 * (x3 - x1))
        if abs(a2 - a1) < eps:
            return PositionCalculator.position_from_two_flags(key1, d1, key2, d2)
        y = (b1 - b2) / (a2 - a1)
        x = a1 * y + b1
        return (x, y)

    @staticmethod
    def position_of_object(
        px, py, flag_key, flag_d, flag_angle, obj_d, obj_angle
    ):
        """Позиция объекта по позиции игрока, одному флагу-ориентиру и наблюдению за объектом."""
        eps = 1e-9
        xf, yf = FLAG_COORDS[flag_key]
        angle_delta = abs(flag_angle - obj_angle)
        angle_rad = math.radians(angle_delta)
        d_sq = flag_d**2 + obj_d**2 - 2 * flag_d * obj_d * math.cos(angle_rad)
        if d_sq < 0:
            d_sq = 0
        d_obj_flag = math.sqrt(d_sq)
        if d_obj_flag < eps:
            return (xf, yf)
        candidates = PositionCalculator._intersect_circles(
            px, py, obj_d, xf, yf, d_obj_flag
        )
        if not candidates:
            return None
        valid = [
            (sx, sy)
            for sx, sy in candidates
            if -BOUND_X <= sx <= BOUND_X and -BOUND_Y <= sy <= BOUND_Y
        ]
        if not valid:
            valid = candidates
        return valid[0]
