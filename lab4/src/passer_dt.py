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
        "atBall": {"condition": lambda mgr, state: mgr.getDistance("b") < 0.85, "trueCond": "startPassing", "falseCond": "goToBall"},
        "goToBall": {"condition": lambda mgr, state: mgr.getVisible("b"), "trueCond": "approachBall", "falseCond": "searchBall"},
        "searchBall": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", "60")), "next": "sendCommand"},
        "approachBall": {"condition": lambda mgr, state: abs(mgr.getAngle("b")) > 4, "trueCond": "turnToBall", "falseCond": "dashToBall"},
        "turnToBall": {"exec": lambda mgr, state: state.__setitem__("command", ("turn", str(int(mgr.getAngle("b"))))), "next": "sendCommand"},
        "dashToBall": {"exec": lambda mgr, state: _dash_to_ball(mgr, state), "next": "sendCommand"},
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


def _dash_to_ball(mgr, state):
    """К мячу быстрее: ближе 1.5 м — 70, иначе 85 (меньше лагов)."""
    d = mgr.getDistance("b")
    power = 70 if d < 1.5 else 85
    state["command"] = ("dash", str(power))


def _pass_exec(mgr, state):
    """Пас как у друга по углу; сила по дистанции, стабильная формула."""
    teammate = mgr.getClosestTeammate()
    if teammate:
        key, obj = teammate
        angle = obj.get("dir", 0)
        dist = obj.get("dist", 0)
        # Формула как у друга (dist*3+30), но макс 72 — чтобы не перелёт
        power = min(72, max(40, int(dist * 2.5 + 28)))
        state["command"] = ("kick", f"{power} {int(angle)}")
        state["status"] = "wait_goal"
        state["say"] = "go"
    else:
        state["command"] = ("kick", "10 45")
