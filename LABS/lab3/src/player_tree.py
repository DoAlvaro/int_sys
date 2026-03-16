"""Дерево решений для полевого игрока: ведущий/ведомый, флаги, мяч."""
# noqa: D100

ACT_FLAG = "flag"
ACT_KICK = "kick"


def build_player_tree(step_list: list[dict]) -> dict:
    tree = {
        "state": {
            "next": 0,
            "sequence": step_list,
            "action": None,
            "command": None,
            "teammate_dist": 9999,
            "teammate_angle": 0,
        },
        "root": {
            "exec": lambda ctx, st: _root_step(ctx, st),
            "next": "checkTeammates",
        },
        "checkTeammates": {
            "condition": lambda ctx, st: ctx.teammate_count() == 0,
            "trueCond": "leaderGoalVisible",
            "falseCond": "followerInit",
        },
        "leaderGoalVisible": {
            "condition": lambda ctx, st: ctx.is_visible(st["action"]["fl"]),
            "trueCond": "leaderRootNext",
            "falseCond": "leaderRotate",
        },
        "leaderRotate": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "90")),
            "next": "sendCommand",
        },
        "leaderRootNext": {
            "condition": lambda ctx, st: st["action"]["act"] == ACT_FLAG,
            "trueCond": "flagSeek",
            "falseCond": "ballSeek",
        },
        "flagSeek": {
            "condition": lambda ctx, st: ctx.distance_to(st["action"]["fl"]) < 3,
            "trueCond": "closeFlag",
            "falseCond": "farGoal",
        },
        "closeFlag": {
            "exec": lambda ctx, st: _next_target(st),
            "next": "leaderRootNext",
        },
        "farGoal": {
            "condition": lambda ctx, st: abs(ctx.angle_to(st["action"]["fl"])) > 4,
            "trueCond": "rotateToGoal",
            "falseCond": "runToGoal",
        },
        "rotateToGoal": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(ctx.angle_to(st["action"]["fl"]))))
            ),
            "next": "sendCommand",
        },
        "runToGoal": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "100")),
            "next": "sendCommand",
        },
        "ballSeek": {
            "condition": lambda ctx, st: ctx.distance_to(st["action"]["fl"]) < 0.7,
            "trueCond": "closeBall",
            "falseCond": "farGoal",
        },
        "closeBall": {
            "condition": lambda ctx, st: ctx.is_visible(st["action"].get("goal", "gr")),
            "trueCond": "ballGoalVisible",
            "falseCond": "ballGoalInvisible",
        },
        "ballGoalVisible": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("kick", f"100 {int(ctx.angle_to(st['action'].get('goal', 'gr')))}")
            ),
            "next": "sendCommand",
        },
        "ballGoalInvisible": {
            "exec": lambda ctx, st: st.__setitem__("command", ("kick", "10 45")),
            "next": "sendCommand",
        },
        "followerInit": {
            "exec": lambda ctx, st: _follower_vars(ctx, st),
            "next": "followerTooClose",
        },
        "followerTooClose": {
            "condition": lambda ctx, st: (
                st["teammate_dist"] < 1 and abs(st["teammate_angle"]) < 40
            ),
            "trueCond": "followerAvoidCollision",
            "falseCond": "followerCheckFar",
        },
        "followerAvoidCollision": {
            "exec": lambda ctx, st: st.__setitem__("command", ("turn", "30")),
            "next": "sendCommand",
        },
        "followerCheckFar": {
            "condition": lambda ctx, st: st["teammate_dist"] > 10,
            "trueCond": "followerFarApproach",
            "falseCond": "followerCheckAngle",
        },
        "followerFarApproach": {
            "condition": lambda ctx, st: abs(st["teammate_angle"]) > 5,
            "trueCond": "followerFarTurn",
            "falseCond": "followerFarDash",
        },
        "followerFarTurn": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(st["teammate_angle"])))
            ),
            "next": "sendCommand",
        },
        "followerFarDash": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "80")),
            "next": "sendCommand",
        },
        "followerCheckAngle": {
            "condition": lambda ctx, st: (
                st["teammate_angle"] > 40 or st["teammate_angle"] < 25
            ),
            "trueCond": "followerAdjustAngle",
            "falseCond": "followerCheckDist",
        },
        "followerAdjustAngle": {
            "exec": lambda ctx, st: st.__setitem__(
                "command", ("turn", str(int(st["teammate_angle"] - 30)))
            ),
            "next": "sendCommand",
        },
        "followerCheckDist": {
            "condition": lambda ctx, st: st["teammate_dist"] < 7,
            "trueCond": "followerSlowDash",
            "falseCond": "followerMediumDash",
        },
        "followerSlowDash": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "20")),
            "next": "sendCommand",
        },
        "followerMediumDash": {
            "exec": lambda ctx, st: st.__setitem__("command", ("dash", "40")),
            "next": "sendCommand",
        },
        "sendCommand": {
            "command": lambda ctx, st: st["command"],
        },
    }
    return tree


def _root_step(ctx, st):
    if st["next"] >= len(st["sequence"]):
        st["next"] = 0
    st["action"] = st["sequence"][st["next"]]
    st["command"] = None


def _next_target(st):
    st["next"] += 1
    if st["next"] >= len(st["sequence"]):
        st["next"] = 0
    st["action"] = st["sequence"][st["next"]]


def _follower_vars(ctx, st):
    closest = ctx.closest_teammate()
    if closest:
        _, obj = closest
        st["teammate_dist"] = obj.get("dist", 9999)
        st["teammate_angle"] = obj.get("dir", 0)
    else:
        st["teammate_dist"] = 9999
        st["teammate_angle"] = 0
    st["command"] = None
