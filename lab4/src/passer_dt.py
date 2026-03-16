def create_passer_tree():
    tree = {
        "state": {"status": "init", "command": None},
        "root": {"exec": lambda mgr, state: _root_exec(mgr, state), "next": "checkStatus"},
        "checkStatus": {"condition": lambda mgr, state: state["status"] == "init", "trueCond": "startMoving", "falseCond": "checkMoveToFplc"},
        "startMoving": {"exec": lambda mgr, state: state.__setitem__("status", "move_to_fplc"), "next": "checkMoveToFplc"},
        "checkMoveToFplc": {"condition": lambda mgr, state: state["status"] == "move_to_fplc", "trueCond": "atFplc", "falseCond": "checkMoveToBall"},
        "atFplc": {"condition": lambda mgr, state: mgr.getDistance(mgr.getCenterFlag()) < 3, "trueCond": "startMoveToBall", "falseCond": "goToFplc"},
        "goToFplc": {"condition": lambda mgr, state: mgr.getVisible(mgr.getCenterFlag()), "trueCond": "approachFplc", "falseCond": "searchFplc"},
        "searchFplc": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", "60")), "next": "sendCommand"},
        "approachFplc": {"condition": lambda mgr, state: abs(mgr.getAngle(mgr.getCenterFlag())) > 5, "trueCond": "turnToFplc", "falseCond": "dashToFplc"},
        "turnToFplc": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", str(int(mgr.getAngle(mgr.getCenterFlag()))))), "next": "sendCommand"},
        "dashToFplc": {"exec": lambda mgr, state: state.__setitem__("command", ("dash", "80")), "next": "sendCommand"},
        "startMoveToBall": {"exec": lambda mgr, state: state.__setitem__("status", "move_to_ball"), "next": "checkMoveToBall"},
        "checkMoveToBall": {"condition": lambda mgr, state: state["status"] == "move_to_ball", "trueCond": "atBall", "falseCond": "checkPassing"},
        "atBall": {"condition": lambda mgr, state: mgr.getDistance("b") < 0.7, "trueCond": "startPassing", "falseCond": "goToBall"},
        "goToBall": {"condition": lambda mgr, state: mgr.getVisible("b"), "trueCond": "approachBall", "falseCond": "searchBall"},
        "searchBall": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", "60")), "next": "sendCommand"},
        "approachBall": {"condition": lambda mgr, state: abs(mgr.getAngle("b")) > 5, "trueCond": "turnToBall", "falseCond": "dashToBall"},
        "turnToBall": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", str(int(mgr.getAngle("b"))))), "next": "sendCommand"},
        "dashToBall": {"exec": lambda mgr, state: state.__setitem__("command", ("dash", "100")), "next": "sendCommand"},
        "startPassing": {"exec": lambda mgr, state: state.__setitem__("status", "passing"), "next": "checkPassing"},
        "checkPassing": {"condition": lambda mgr, state: state["status"] == "passing", "trueCond": "findScorer", "falseCond": "waitGoal"},
        "findScorer": {"condition": lambda mgr, state: mgr.getTeammateCount() > 0, "trueCond": "passToScorer", "falseCond": "rotateWithBall"},
        "rotateWithBall": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", "60")), "next": "sendCommand"},
        "passToScorer": {"exec": lambda mgr, state: _pass_exec(mgr, state), "next": "sendCommand"},
        "waitGoal": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", "10")), "next": "sendCommand"},
        "sendCommand": {"command": lambda mgr, state: state["command"]},
    }
    return tree


def _root_exec(mgr, state):
    state["command"] = None


def _pass_exec(mgr, state):
    """Как у друга: сильный удар в сторону напарника (угол и дистанция из see)."""
    teammate = mgr.getClosestTeammate()
    if teammate:
        key, obj = teammate
        angle = obj.get("dir", 0)
        dist = obj.get("dist", 0)
        state["command"] = ("kick", f"{int(dist * 3 + 30)} {int(angle)}")
        state["status"] = "wait_goal"
        state["say"] = "go"
    else:
        state["command"] = ("kick", "10 45")
