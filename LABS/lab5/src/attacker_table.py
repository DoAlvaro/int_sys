"""Таблица действий для атакующего."""
# noqa: D100


def build_attacker_table() -> dict:
    def search_ball(ctx, s):
        return ("turn", "40")

    def go_ball(ctx, s):
        if not ctx.is_visible("b"):
            return ("turn", "30")
        angle = ctx.angle_to("b")
        dist = ctx.distance_to("b")
        if abs(angle) > 7:
            return ("turn", str(int(angle)))
        if dist > 1.5:
            return ("dash", "80")
        return ("dash", "40")

    def kick(ctx, s):
        goal = ctx.enemy_goal_key()
        if ctx.is_visible(goal):
            return ("kick", f"100 {int(ctx.angle_to(goal))}")
        return ("kick", "40 20")

    return {
        "__start__": "start",
        "start": [
            (lambda ctx, s: not ctx.is_visible("b"), search_ball, "start"),
            (
                lambda ctx, s: ctx.is_visible("b") and ctx.distance_to("b") > 0.7,
                go_ball,
                "start",
            ),
            (
                lambda ctx, s: ctx.is_visible("b") and ctx.distance_to("b") <= 0.7,
                kick,
                "start",
            ),
        ],
    }
