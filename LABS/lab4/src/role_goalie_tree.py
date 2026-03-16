"""Дерево решений для вратаря (как в lab3)."""
# noqa: D100
from role_context import RoleContext


def build_goalie_tree() -> dict:
    tree = {
        "state": {"command": None, "ball_dist": 9999, "ball_angle": 0},
        "root": {
            "exec": lambda ctx, st: st.__setitem__("command", None),
            "next": "checkBallVisible",
        },
        "checkBallVisible": {
            "condition": lambda ctx, st: ctx.is_visible("b"),
            "trueCond": "updateBallInfo",
            "falseCond": "goToGoal",
        },
        "updateBallInfo": {
            "exec": lambda ctx, st: _refresh_ball(ctx, st),
            "next": "checkBallClose",
        },
        "checkBallClose": {
            "condition": lambda ctx, st: st["ball_dist"] < 20,
            "trueCond": "ballCloseLogic",
            "falseCond": "goToGoal",
        },
        "ballCloseLogic": {
            "condition": lambda ctx, st: st["ball_dist"] < 1.5,
            "trueCond": "checkDistChange",
            "falseCond": "checkBallKickable",
        },
        "checkDistChange": {
            "condition": lambda ctx, st: st["ball_dist_change"] < 2,
            "trueCond": "checkBallKickable",
            "falseCond": "tryCatch",
        },
        "tryCatch": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("catch", str(int(st["ball_angle"])))
            ),
            "next": "sendCommand",
        },
        "checkBallKickable": {
            "condition": lambda ctx, st: st["ball_dist"] < 0.7,
            "trueCond": "kickBall",
            "falseCond": "approachBall",
        },
        "kickBall": {
            "condition": lambda ctx, st: ctx.is_visible("gl"),
            "trueCond": "kickToGl",
            "falseCond": "kickToFltOrFlb",
        },
        "kickToGl": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("kick", f"100 {int(ctx.angle_to('gl'))}")
            ),
            "next": "sendCommand",
        },
        "kickToFltOrFlb": {
            "condition": lambda ctx, st: ctx.is_visible("flt"),
            "trueCond": "kickToFlt",
            "falseCond": "kickToFlbOrWeak",
        },
        "kickToFlt": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("kick", f"80 {int(ctx.angle_to('flt'))}")
            ),
            "next": "sendCommand",
        },
        "kickToFlbOrWeak": {
            "condition": lambda ctx, st: ctx.is_visible("flb"),
            "trueCond": "kickToFlb",
            "falseCond": "kickWeak",
        },
        "kickToFlb": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("kick", f"80 {int(ctx.angle_to('flb'))}")
            ),
            "next": "sendCommand",
        },
        "kickWeak": {
            "exec": lambda ctx, st: st.__setitem__("command", ("kick", "30 90")),
            "next": "sendCommand",
        },
        "approachBall": {
            "condition": lambda ctx, st: abs(st["ball_angle"]) > 5,
            "trueCond": "turnToBall",
            "falseCond": "dashToBall",
        },
        "turnToBall": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(st["ball_angle"])))
            ),
            "next": "sendCommand",
        },
        "dashToBall": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "100")),
            "next": "sendCommand",
        },
        "goToGoal": {
            "condition": lambda ctx, st: ctx.is_visible("gr"),
            "trueCond": "checkGoalDist",
            "falseCond": "searchGoal",
        },
        "searchGoal": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "60")),
            "next": "sendCommand",
        },
        "checkGoalDist": {
            "condition": lambda ctx, st: ctx.distance_to("gr") > 5,
            "trueCond": "moveToGoal",
            "falseCond": "positionInGoal",
        },
        "moveToGoal": {
            "condition": lambda ctx, st: abs(ctx.angle_to("gr")) > 5,
            "trueCond": "turnToGoal",
            "falseCond": "dashToGoal",
        },
        "turnToGoal": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to("gr"))))
            ),
            "next": "sendCommand",
        },
        "dashToGoal": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "80")),
            "next": "sendCommand",
        },
        "positionInGoal": {
            "condition": lambda ctx, st: _should_adjust(ctx),
            "trueCond": "adjustPosition",
            "falseCond": "faceBall",
        },
        "adjustPosition": {
            "exec": lambda ctx, st: _do_adjust(ctx, st),
            "next": "sendCommand",
        },
        "faceBall": {
            "condition": lambda ctx, st: ctx.is_visible("b"),
            "trueCond": "faceBallCheck",
            "falseCond": "faceBallSearch",
        },
        "faceBallCheck": {
            "condition": lambda ctx, st: abs(ctx.angle_to("b")) > 5,
            "trueCond": "turnFaceBall",
            "falseCond": "standStill",
        },
        "turnFaceBall": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to("b"))))
            ),
            "next": "sendCommand",
        },
        "faceBallSearch": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "30")),
            "next": "sendCommand",
        },
        "standStill": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "1")),
            "next": "sendCommand",
        },
        "sendCommand": {"command": lambda ctx, st: st["command"]},
    }
    return tree


def _refresh_ball(ctx: RoleContext, st):
    st["ball_dist"] = ctx.distance_to("b")
    st["ball_dist_change"] = ctx.dist_change("b")
    st["ball_angle"] = ctx.angle_to("b")


def _should_adjust(ctx: RoleContext) -> bool:
    if ctx.is_visible("fprc"):
        d = ctx.distance_to("fprc")
        if d < 10 or d > 18:
            return True
        if abs(ctx.angle_to("fprc")) > 30:
            return True
    return False


def _do_adjust(ctx: RoleContext, st):
    if ctx.is_visible("fprc"):
        d = ctx.distance_to("fprc")
        angle = ctx.angle_to("fprc")
        if d > 18:
            if ctx.is_visible("gr") and abs(ctx.angle_to("gr")) > 5:
                st["command"] = ("turn", str(int(ctx.angle_to("gr"))))
            else:
                st["command"] = ("dash", "50")
        elif d < 10:
            st["command"] = ("dash", "-30")
        elif abs(angle) > 30:
            st["command"] = ("turn", str(int(angle / 2)))
        else:
            st["command"] = ("turn", "1")
    else:
        st["command"] = ("turn", "30")
