"""Таблица действий для вратаря."""
# noqa: D100


def build_goalie_table() -> dict:
    def update_timers(*keys):
        def fn(ctx, s):
            for k in keys:
                s[k] = ctx.time_cycle
        return fn

    def check_timer(timer_name, max_delta):
        def fn(ctx, s):
            return (ctx.time_cycle - s.get(timer_name, 0)) > max_delta
        return fn

    def goalie_not_at_goal_but_sees_it(ctx, s):
        goal = ctx.own_goal_key()
        return ctx.is_visible(goal) and ctx.distance_to(goal) > 3

    def move_to_own_goal(ctx, s):
        goal = ctx.own_goal_key()
        angle = ctx.angle_to(goal)
        dist = ctx.distance_to(goal)
        if abs(angle) > 7:
            return ("turn", str(int(angle)))
        if dist > 6:
            return ("dash", "100")
        if dist > 3.5:
            return ("dash", "70")
        return None

    def move_to_ball(ctx, s):
        s["last_find_ball"] = ctx.time_cycle
        angle = ctx.angle_to("b")
        dist = ctx.distance_to("b")
        if abs(angle) > 7:
            return ("turn", str(int(angle)))
        if dist > 2:
            return ("dash", "100")
        return ("dash", "80")

    def kick_ball_from_goal(ctx, s):
        def norm(a):
            while a > 180:
                a -= 360
            while a < -180:
                a += 360
            return a

        enemy_goal = ctx.enemy_goal_key()
        own_goal = ctx.own_goal_key()
        if ctx.is_visible(enemy_goal):
            return ("kick", f"100 {int(ctx.angle_to(enemy_goal))}")
        if ctx.is_visible(own_goal):
            away = norm(ctx.angle_to(own_goal) + 180)
            return ("kick", f"100 {int(away)}")
        return ("kick", "100 0")

    return {
        "__start__": "search_goal",
        "search_goal": [
            (
                lambda ctx, s: ctx.is_visible(ctx.own_goal_key()),
                update_timers("last_find_ball"),
                "move_to_own_goal",
            ),
            (lambda ctx, s: True, lambda ctx, s: ("turn", "90"), "search_goal"),
        ],
        "move_to_own_goal": [
            (
                check_timer("last_find_ball", 30),
                update_timers("last_find_ball"),
                "determine_distance_to_ball",
            ),
            (
                goalie_not_at_goal_but_sees_it,
                move_to_own_goal,
                "move_to_own_goal",
            ),
            (
                lambda ctx, s: True,
                lambda ctx, s: ("turn", str(int(ctx.angle_to("b")))),
                "at_goal",
            ),
        ],
        "determine_distance_to_ball": [
            (
                lambda ctx, s: not ctx.is_visible("b"),
                lambda ctx, s: ("turn", "90"),
                "determine_distance_to_ball",
            ),
            (
                lambda ctx, s: ctx.distance_to("b") <= 10,
                update_timers("last_find_ball"),
                "move_to_ball_and_kick",
            ),
            (
                check_timer("last_find_ball", 4),
                update_timers("last_find_ball"),
                "search_goal",
            ),
        ],
        "move_to_ball_and_kick": [
            (
                check_timer("last_find_ball", 5),
                update_timers("last_find_ball"),
                "search_goal",
            ),
            (
                lambda ctx, s: not ctx.is_visible("b"),
                lambda ctx, s: ("turn", "90"),
                "move_to_ball_and_kick",
            ),
            (
                lambda ctx, s: ctx.distance_to("b") > 1,
                move_to_ball,
                "move_to_ball_and_kick",
            ),
            (
                lambda ctx, s: ctx.distance_to("b") <= 1,
                kick_ball_from_goal,
                "search_goal",
            ),
        ],
        "at_goal": [
            (
                lambda ctx, s: not ctx.is_visible("b"),
                lambda ctx, s: ("turn", "90"),
                "at_goal",
            ),
            (
                lambda ctx, s: ctx.distance_to("b") > 15,
                lambda ctx, s: ("turn", str(int(ctx.angle_to("b")))),
                "at_goal",
            ),
            (lambda ctx, s: True, update_timers("last_find_ball"), "move_to_ball_and_kick"),
        ],
    }
