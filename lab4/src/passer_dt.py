import math


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
    """
    Пас «на ход»: считаем глобальные координаты напарника, точку встречи (между нами и им),
    бьём в эту точку — мяч и игрок 2 должны пересечься.
    """
    teammate = mgr.getClosestTeammate()
    if not teammate:
        state["command"] = ("kick", "10 45")
        return
    key, obj = teammate
    angle_deg = obj.get("dir", 0)
    dist_teammate = obj.get("dist", 0)
    px, py = mgr.x, mgr.y
    if px is None or py is None:
        state["command"] = ("kick", f"{min(70, int(dist_teammate * 1.5 + 25))} {int(angle_deg)}")
        state["status"] = "wait_goal"
        state["say"] = "go"
        return
    body = mgr.body_angle_rad if mgr.body_angle_rad is not None else 0
    angle_rad = math.radians(angle_deg)
    # Глобальная позиция напарника
    tx = px + dist_teammate * math.cos(body + angle_rad)
    ty = py + dist_teammate * math.sin(body + angle_rad)
    # Точка встречи: между пасующим и напарником (55% пути), чтобы мяч приземлился «на ход»
    k_meet = 0.55
    mx = px + k_meet * (tx - px)
    my = py + k_meet * (ty - py)
    d_meet = math.hypot(mx - px, my - py)
    # Угол удара в глобальных координатах, затем относительно тела
    kick_angle_global = math.atan2(my - py, mx - px)
    kick_angle_body_deg = math.degrees(kick_angle_global - body)
    # Нормализуем в [-180, 180]
    while kick_angle_body_deg > 180:
        kick_angle_body_deg -= 360
    while kick_angle_body_deg < -180:
        kick_angle_body_deg += 360
    power = min(90, max(35, int(d_meet * 2.1 + 15)))
    state["command"] = ("kick", f"{power} {int(kick_angle_body_deg)}")
    state["status"] = "wait_goal"
    state["say"] = "go"
