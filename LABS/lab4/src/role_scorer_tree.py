"""Дерево решений для бьющего: угол -> ворота -> ожидание 'go' -> мяч -> гол."""
# noqa: D100


def _dash_power_to_ball(ctx) -> int:
    """Меньше мощность при приближении к мячу, чтобы не откидывать его."""
    d = ctx.distance_to("b")
    if d < 1.2:
        return 25
    if d < 2.0:
        return 40
    if d < 3.5:
        return 55
    if d < 5.0:
        return 70
    return 85


def build_scorer_tree() -> dict:
    tree = {
        "state": {"status": "init", "command": None},
        "root": {
            "exec": lambda ctx, st: _root_step(ctx, st),
            "next": "checkHeardGo",
        },
        "checkHeardGo": {
            "condition": lambda ctx, st: ctx.last_heard_msg == "go",
            "trueCond": "startScoring",
            "falseCond": "checkStatus",
        },
        "checkStatus": {
            "condition": lambda ctx, st: st["status"] == "init",
            "trueCond": "startMoving",
            "falseCond": "checkMoveToFplb",
        },
        "startMoving": {
            "exec": lambda ctx, st: st.__setitem__("status", "move_to_fplb"),
            "next": "checkMoveToFplb",
        },
        "checkMoveToFplb": {
            "condition": lambda ctx, st: st["status"] == "move_to_fplb",
            "trueCond": "atFplb",
            "falseCond": "checkMoveToFgrb",
        },
        "atFplb": {
            "condition": lambda ctx, st: ctx.distance_to(ctx.corner_flag()) < 3,
            "trueCond": "startMoveToFgrb",
            "falseCond": "goToFplb",
        },
        "goToFplb": {
            "condition": lambda ctx, st: ctx.is_visible(ctx.corner_flag()),
            "trueCond": "approachFplb",
            "falseCond": "searchFplb",
        },
        "searchFplb": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "60")),
            "next": "sendCommand",
        },
        "approachFplb": {
            "condition": lambda ctx, st: abs(ctx.angle_to(ctx.corner_flag())) > 5,
            "trueCond": "turnToFplb",
            "falseCond": "dashToFplb",
        },
        "turnToFplb": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to(ctx.corner_flag()))))
            ),
            "next": "sendCommand",
        },
        "dashToFplb": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "80")),
            "next": "sendCommand",
        },
        "startMoveToFgrb": {
            "exec": lambda ctx, st: st.__setitem__("status", "move_to_fgrb"),
            "next": "checkMoveToFgrb",
        },
        "checkMoveToFgrb": {
            "condition": lambda ctx, st: st["status"] == "move_to_fgrb",
            "trueCond": "atFgrb",
            "falseCond": "checkWaitPass",
        },
        "atFgrb": {
            "condition": lambda ctx, st: ctx.distance_to(ctx.goal_corner_flag()) < 3,
            "trueCond": "startWaitPass",
            "falseCond": "goToFgrb",
        },
        "goToFgrb": {
            "condition": lambda ctx, st: ctx.is_visible(ctx.goal_corner_flag()),
            "trueCond": "approachFgrb",
            "falseCond": "searchFgrb",
        },
        "searchFgrb": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "60")),
            "next": "sendCommand",
        },
        "approachFgrb": {
            "condition": lambda ctx, st: abs(ctx.angle_to(ctx.goal_corner_flag())) > 5,
            "trueCond": "turnToFgrb",
            "falseCond": "dashToFgrb",
        },
        "turnToFgrb": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to(ctx.goal_corner_flag()))))
            ),
            "next": "sendCommand",
        },
        "dashToFgrb": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "80")),
            "next": "sendCommand",
        },
        "startWaitPass": {
            "exec": lambda ctx, st: st.__setitem__("status", "wait_pass"),
            "next": "checkWaitPass",
        },
        "checkWaitPass": {
            "condition": lambda ctx, st: st["status"] == "wait_pass",
            "trueCond": "waitForGo",
            "falseCond": "checkScore",
        },
        "waitForGo": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "10")),
            "next": "sendCommand",
        },
        "startScoring": {
            "exec": lambda ctx, st: st.__setitem__("status", "score"),
            "next": "checkScore",
        },
        "checkScore": {
            "condition": lambda ctx, st: st["status"] == "score",
            "trueCond": "atBallScore",
            "falseCond": "waitGoalScorer",
        },
        "atBallScore": {
            "condition": lambda ctx, st: ctx.distance_to("b") < 0.8,
            "trueCond": "kickToGoal",
            "falseCond": "goToBallScore",
        },
        "goToBallScore": {
            "condition": lambda ctx, st: ctx.is_visible("b"),
            "trueCond": "approachBallScore",
            "falseCond": "searchBallScore",
        },
        "searchBallScore": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "45")),
            "next": "sendCommand",
        },
        "approachBallScore": {
            "condition": lambda ctx, st: abs(ctx.angle_to("b")) > 5,
            "trueCond": "turnToBallScore",
            "falseCond": "dashToBallScore",
        },
        "turnToBallScore": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to("b"))))
            ),
            "next": "sendCommand",
        },
        "dashToBallScore": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", str(_dash_power_to_ball(ctx)))),
            "next": "sendCommand",
        },
        "kickToGoal": {
            "condition": lambda ctx, st: ctx.is_visible(ctx.goal_flag()),
            "trueCond": "goalVisibleScore",
            "falseCond": "goalInvisibleScore",
        },
        "goalVisibleScore": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("kick", f"100 {int(ctx.angle_to(ctx.goal_flag()))}")
            ),
            "next": "sendCommand",
        },
        "goalInvisibleScore": {
            "exec": lambda ctx, st: st.__setitem__("command", ("kick", "10 45")),
            "next": "sendCommand",
        },
        "waitGoalScorer": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "10")),
            "next": "sendCommand",
        },
        "sendCommand": {"command": lambda ctx, st: st["command"]},
    }
    return tree


def _root_step(ctx, st):
    st["command"] = None
