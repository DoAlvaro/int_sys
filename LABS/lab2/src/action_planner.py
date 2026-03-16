"""Планировщик действий: последовательность шагов (флаг/удар) и выбор команды за такт."""
# noqa: D100


class ActionPlanner:
    """Очередь действий (идти к флагу, бить по воротам). Решение — одна команда за такт."""

    def __init__(self, step_list: list[dict] | None = None):
        self._steps = step_list or []
        self._idx = 0

    @property
    def current_step(self) -> dict | None:
        """Текущее действие в списке или None."""
        if not self._steps or self._idx >= len(self._steps):
            return None
        return self._steps[self._idx]

    def advance(self):
        """Перейти к следующему действию (по кругу)."""
        self._idx += 1
        if self._idx >= len(self._steps):
            self._idx = 0
        print(f"переход к действию {self._idx}: {self.current_step}")

    def reset_to_start(self):
        """Сброс на первое действие (например после гола)."""
        self._idx = 0
        print(f"Сброс контроллера. Текущее действие: {self.current_step}")

    def choose_command(self, visible: dict, game_on: bool) -> tuple[str, str] | None:
        """Выдать команду (cmd, params) или None, если не играем."""
        if not game_on:
            return None
        step = self.current_step
        if step is None:
            return None
        kind = step.get("act", "")
        if kind == "flag":
            return self._cmd_go_to_flag(step, visible)
        if kind == "kick":
            return self._cmd_kick(step, visible)
        return None

    def _cmd_go_to_flag(self, step: dict, visible: dict) -> tuple[str, str]:
        """Двигаться к флагу: turn или dash."""
        target_key = step.get("fl", "")
        if target_key not in visible:
            return ("turn", "60")
        obs = visible[target_key]
        d = obs["dist"]
        angle = obs["dir"]
        if d < 3.0:
            self.advance()
            return None
        if abs(angle) > 10:
            return ("turn", str(int(angle)))
        return ("dash", "100")

    def _cmd_kick(self, step: dict, visible: dict) -> tuple[str, str]:
        """Подойти к мячу и ударить в ворота."""
        ball_key = step.get("fl", "b")
        goal_key = step.get("goal", "gr")
        if ball_key not in visible:
            return ("turn", "60")
        ball = visible[ball_key]
        bd = ball["dist"]
        ba = ball["dir"]
        if bd > 0.7:
            if abs(ba) > 10:
                return ("turn", str(int(ba)))
            return ("dash", "100")
        if goal_key in visible:
            goal = visible[goal_key]
            return ("kick", f"100 {int(goal['dir'])}")
        return ("kick", "10 45")
