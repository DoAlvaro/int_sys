"""Исполнение таблицы действий: условия -> действие -> переход."""
# noqa: D100


class ActionTable:
    """Один шаг: проверка условий по порядку, первое True — выполнить действие и перейти."""

    def __init__(self, table: dict):
        self._table = table
        self._current = table["__start__"]
        self._state = {}

    def reset_state(self):
        self._current = self._table["__start__"]
        self._state = {}

    def next_step(self, ctx) -> tuple | None:
        node = self._table.get(self._current)
        if node is None:
            raise ValueError(f"Node {self._current} not found")
        for cond, action, nxt in node:
            if cond(ctx, self._state):
                result = action(ctx, self._state)
                self._current = nxt
                return result
        return None
