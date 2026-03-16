"""Таблица действий для защитника."""
# noqa: D100


def build_defender_table() -> dict:
    TRUE = lambda ctx, s: True

    def norm_angle(angle):
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    def ball_not_visible(ctx, s):
        return not ctx.is_visible("b")

    def ball_visible(ctx, s):
        return ctx.is_visible("b")

    def ball_kickable(ctx, s):
        return ctx.is_visible("b") and ctx.distance_to("b") <= 1

    def ball_very_dangerous(ctx, s):
        return ctx.is_visible("b") and ctx.distance_to("b") <= 10

    def ball_dangerous(ctx, s):
        return ctx.is_visible("b") and ctx.distance_to("b") <= 20

    def ball_safe(ctx, s):
        return ctx.is_visible("b") and ctx.distance_to("b") > 20

    def can_see_own_goal(ctx, s):
        return ctx.is_visible(ctx.own_goal_key())

    def near_own_goal(ctx, s):
        goal = ctx.own_goal_key()
        if not ctx.is_visible(goal):
            return False
        return 5 <= ctx.distance_to(goal) <= 18

    def too_far_from_goal(ctx, s):
        goal = ctx.own_goal_key()
        if not ctx.is_visible(goal):
            return True
        return ctx.distance_to(goal) > 25

    def too_close_to_goal(ctx, s):
        goal = ctx.own_goal_key()
        return ctx.is_visible(goal) and ctx.distance_to(goal) < 4

    def teammate_too_close(ctx, s):
        c = ctx.closest_teammate()
        return c is not None and c[1].get("dist", 9999) < 5

    def i_am_closer_to_ball(ctx, s):
        return not ctx.teammate_is_closer_to_ball()

    def teammate_closer_to_ball(ctx, s):
        return ctx.teammate_is_closer_to_ball()

    def ball_dangerous_and_i_closer(ctx, s):
        return ball_dangerous(ctx, s) and i_am_closer_to_ball(ctx, s)

    def ball_dangerous_and_teammate_closer(ctx, s):
        return ball_dangerous(ctx, s) and teammate_closer_to_ball(ctx, s)

    def ball_very_dangerous_and_i_closer(ctx, s):
        return ball_very_dangerous(ctx, s) and i_am_closer_to_ball(ctx, s)

    def ball_very_dangerous_and_teammate_closer(ctx, s):
        return ball_very_dangerous(ctx, s) and teammate_closer_to_ball(ctx, s)

    def search_spin(ctx, s):
        return ("turn", "50")

    def scan_for_ball(ctx, s):
        s["scan_count"] = s.get("scan_count", 0) + 1
        return ("turn", "40")

    def watch_ball(ctx, s):
        s["scan_count"] = 0
        if not ctx.is_visible("b"):
            return ("turn", "40")
        angle = ctx.angle_to("b")
        dist = ctx.distance_to("b")
        if abs(angle) > 5:
            return ("turn", str(int(angle)))
        if dist > 25:
            return ("dash", "15")
        return ("turn", "2")

    def go_to_goal_area(ctx, s):
        goal = ctx.own_goal_key()
        if not ctx.is_visible(goal):
            return ("turn", "50")
        angle = ctx.angle_to(goal)
        dist = ctx.distance_to(goal)
        if dist > 18:
            if abs(angle) > 10:
                return ("turn", str(int(angle)))
            return ("dash", "100")
        if dist > 12:
            if abs(angle) > 10:
                return ("turn", str(int(angle)))
            return ("dash", "70")
        if dist > 5:
            zone = -12 if ctx.is_upper_defender() else 12
            return ("turn", str(zone))
        away = norm_angle(angle + 180)
        if abs(away) < 30:
            return ("dash", "40")
        return ("turn", str(int(away)))

    def move_away_from_teammate(ctx, s):
        c = ctx.closest_teammate()
        if c:
            away = norm_angle(c[1].get("dir", 0) + 180)
            if abs(away) < 30:
                return ("dash", "50")
            return ("turn", str(int(away)))
        off = -20 if ctx.is_upper_defender() else 20
        return ("turn", str(off))

    def intercept_ball(ctx, s):
        if not ctx.is_visible("b"):
            return ("turn", "30")
        angle = ctx.angle_to("b")
        dist = ctx.distance_to("b")
        if abs(angle) > 10:
            return ("turn", str(int(angle)))
        if dist > 5:
            return ("dash", "100")
        if dist > 2:
            return ("dash", "80")
        return ("dash", "60")

    def clear_ball(ctx, s):
        enemy_goal = ctx.enemy_goal_key()
        own_goal = ctx.own_goal_key()
        if ctx.is_visible(enemy_goal):
            return ("kick", f"100 {int(ctx.angle_to(enemy_goal))}")
        c = ctx.closest_teammate()
        if c:
            angle = int(c[1].get("dir", 0))
            dist = c[1].get("dist", 10)
            power = min(100, int(dist * 5) + 30)
            return ("kick", f"{power} {angle}")
        if ctx.is_visible(own_goal):
            away = norm_angle(ctx.angle_to(own_goal) + 180)
            return ("kick", f"100 {int(away)}")
        return ("kick", "100 0")

    def hold_and_watch(ctx, s):
        if ctx.is_visible("b"):
            angle = ctx.angle_to("b")
            if abs(angle) > 8:
                return ("turn", str(int(angle)))
            if ctx.distance_to("b") > 15:
                return ("dash", "30")
            return ("turn", "2")
        return ("turn", "25")

    return {
        "__start__": "find_goal",
        "find_goal": [
            (ball_kickable, clear_ball, "find_goal"),
            (can_see_own_goal, go_to_goal_area, "go_to_position"),
            (TRUE, search_spin, "find_goal"),
        ],
        "go_to_position": [
            (ball_kickable, clear_ball, "go_to_position"),
            (ball_very_dangerous, intercept_ball, "intercept"),
            (near_own_goal, watch_ball, "on_position"),
            (teammate_too_close, move_away_from_teammate, "go_to_position"),
            (TRUE, go_to_goal_area, "go_to_position"),
        ],
        "on_position": [
            (ball_kickable, clear_ball, "on_position"),
            (ball_very_dangerous_and_i_closer, intercept_ball, "intercept"),
            (ball_very_dangerous_and_teammate_closer, intercept_ball, "intercept"),
            (ball_dangerous_and_i_closer, intercept_ball, "intercept"),
            (ball_dangerous_and_teammate_closer, hold_and_watch, "cover"),
            (ball_safe, watch_ball, "on_position"),
            (ball_visible, watch_ball, "on_position"),
            (ball_not_visible, scan_for_ball, "search_ball_on_position"),
            (TRUE, scan_for_ball, "search_ball_on_position"),
        ],
        "search_ball_on_position": [
            (ball_kickable, clear_ball, "on_position"),
            (ball_very_dangerous, intercept_ball, "intercept"),
            (ball_dangerous_and_i_closer, intercept_ball, "intercept"),
            (ball_visible, watch_ball, "on_position"),
            (lambda ctx, s: s.get("scan_count", 0) > 9, search_spin, "check_position"),
            (TRUE, scan_for_ball, "search_ball_on_position"),
        ],
        "check_position": [
            (ball_kickable, clear_ball, "check_position"),
            (ball_very_dangerous, intercept_ball, "intercept"),
            (ball_visible, watch_ball, "on_position"),
            (too_far_from_goal, search_spin, "find_goal"),
            (teammate_too_close, move_away_from_teammate, "on_position"),
            (too_close_to_goal, lambda ctx, s: ("dash", "30"), "on_position"),
            (TRUE, scan_for_ball, "search_ball_on_position"),
        ],
        "intercept": [
            (ball_kickable, clear_ball, "return_to_position"),
            (
                lambda ctx, s: ball_visible(ctx, s) and ctx.distance_to("b") > 30,
                watch_ball,
                "return_to_position",
            ),
            (
                lambda ctx, s: too_far_from_goal(ctx, s) and not ball_very_dangerous(ctx, s),
                search_spin,
                "return_to_position",
            ),
            (
                lambda ctx, s: teammate_too_close(ctx, s) and teammate_closer_to_ball(ctx, s),
                hold_and_watch,
                "cover",
            ),
            (ball_visible, intercept_ball, "intercept"),
            (TRUE, scan_for_ball, "intercept"),
        ],
        "cover": [
            (ball_kickable, clear_ball, "return_to_position"),
            (
                lambda ctx, s: ball_very_dangerous(ctx, s) and i_am_closer_to_ball(ctx, s),
                intercept_ball,
                "intercept",
            ),
            (
                lambda ctx, s: not ball_dangerous(ctx, s),
                watch_ball,
                "return_to_position",
            ),
            (teammate_too_close, move_away_from_teammate, "cover"),
            (TRUE, hold_and_watch, "cover"),
        ],
        "return_to_position": [
            (ball_kickable, clear_ball, "return_to_position"),
            (ball_very_dangerous, intercept_ball, "intercept"),
            (near_own_goal, watch_ball, "on_position"),
            (can_see_own_goal, go_to_goal_area, "return_to_position"),
            (TRUE, search_spin, "find_goal"),
        ],
    }
