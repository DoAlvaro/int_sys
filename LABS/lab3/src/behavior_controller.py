"""Контроллер поведения: дерево решений + контекст восприятия."""
from tree_executor import TreeExecutor
from perception_context import PerceptionContext
from player_tree import build_player_tree
from goalie_tree import build_goalie_tree


class BehaviorController:
    """Выбор команды по дереву решений (игрок или вратарь)."""

    def __init__(self, step_list: list[dict] | None = None, is_goalie: bool = False):
        self._is_goalie = is_goalie
        self._ctx = PerceptionContext()
        if is_goalie:
            graph = build_goalie_tree()
        else:
            graph = build_player_tree(step_list or [])
        self._tree = TreeExecutor(graph)

    def reset_state(self):
        """Сброс состояния дерева после гола."""
        st = self._tree.tree_state
        if "next" in st:
            st["next"] = 0
            if "sequence" in st:
                st["action"] = st["sequence"][0]
        st["command"] = None

    def choose_command(
        self,
        visible: dict,
        game_on: bool,
        squad: str = "",
        side: str = "",
        unum: int = 0,
        pos_x=None,
        pos_y=None,
    ) -> tuple[str, str] | None:
        if not game_on:
            return None
        self._ctx.set_observation(visible, squad, side, unum, pos_x, pos_y)
        result = self._tree.run(self._ctx)
        if result and isinstance(result, tuple) and len(result) == 2:
            return result
        return None
