"""Дерево решений для пасующего: центр -> мяч -> пас напарнику."""
# noqa: D100


def build_passer_tree() -> dict:
    tree = {
        "state": {"status": "init", "command": None},
        "root": {
            "exec": lambda ctx, st: _root_step(ctx, st),
            "next": "checkStatus",
        },
        "checkStatus": {
            "condition": lambda ctx, st: st["status"] == "init",
            "trueCond": "startMoving",
            "falseCond": "checkMoveToFplc",
        },
        "startMoving": {
            "exec": lambda ctx, st: st.__setitem__("status", "move_to_fplc"),
            "next": "checkMoveToFplc",
        },
        "checkMoveToFplc": {
            "condition": lambda ctx, st: st["status"] == "move_to_fplc",
            "trueCond": "atFplc",
            "falseCond": "checkMoveToBall",
        },
        "atFplc": {
            "condition": lambda ctx, st: ctx.distance_to(ctx.center_flag()) < 3,
            "trueCond": "startMoveToBall",
            "falseCond": "goToFplc",
        },
        "goToFplc": {
            "condition": lambda ctx, st: ctx.is_visible(ctx.center_flag()),
            "trueCond": "approachFplc",
            "falseCond": "searchFplc",
        },
        "searchFplc": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "60")),
            "next": "sendCommand",
        },
        "approachFplc": {
            "condition": lambda ctx, st: abs(ctx.angle_to(ctx.center_flag())) > 5,
            "trueCond": "turnToFplc",
            "falseCond": "dashToFplc",
        },
        "turnToFplc": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to(ctx.center_flag()))))
            ),
            "next": "sendCommand",
        },
        "dashToFplc": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "80")),
            "next": "sendCommand",
        },
        "startMoveToBall": {
            "exec": lambda ctx, st: st.__setitem__("status", "move_to_ball"),
            "next": "checkMoveToBall",
        },
        "checkMoveToBall": {
            "condition": lambda ctx, st: st["status"] == "move_to_ball",
            "trueCond": "atBall",
            "falseCond": "checkPassing",
        },
        "atBall": {
            "condition": lambda ctx, st: ctx.distance_to("b") < 0.7,
            "trueCond": "startPassing",
            "falseCond": "goToBall",
        },
        "goToBall": {
            "condition": lambda ctx, st: ctx.is_visible("b"),
            "trueCond": "approachBall",
            "falseCond": "searchBall",
        },
        "searchBall": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "60")),
            "next": "sendCommand",
        },
        "approachBall": {
            "condition": lambda ctx, st: abs(ctx.angle_to("b")) > 5,
            "trueCond": "turnToBall",
            "falseCond": "dashToBall",
        },
        "turnToBall": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to("b"))))
            ),
            "next": "sendCommand",
        },
        "dashToBall": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "100")),
            "next": "sendCommand",
        },
        "startPassing": {
            "exec": lambda ctx, st: st.__setitem__("status", "passing"),
            "next": "checkPassing",
        },
        "checkPassing": {
            "condition": lambda ctx, st: st["status"] == "passing",
            "trueCond": "findScorer",
            "falseCond": "waitGoal",
        },
        "findScorer": {
            "condition": lambda ctx, st: ctx.teammate_count() > 0,
            "trueCond": "passToScorer",
            "falseCond": "rotateWithBall",
        },
        "rotateWithBall": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "60")),
            "next": "sendCommand",
        },
        "passToScorer": {
            "exec": lambda ctx, st: _pass_step(ctx, st),
            "next": "sendCommand",
        },
        "waitGoal": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "10")),
            "next": "sendCommand",
        },
        "sendCommand": {"command": lambda ctx, st: st["command"]},
    }
    return tree


def _root_step(ctx, st):
    st["command"] = None


def _pass_step(ctx, st):
    mate = ctx.closest_teammate()
    if mate:
        key, obj = mate
        angle = obj.get("dir", 0)
        dist = obj.get("dist", 0)
        st["command"] = ("kick", f"{int(dist * 3 + 30)} {int(angle)}")
        st["status"] = "wait_goal"
        st["say"] = "go"
    else:
        st["command"] = ("kick", "10 45")
