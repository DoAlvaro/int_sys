"""Контроллер по ролям: passer / scorer / goalie."""
from tree_executor import TreeExecutor
from role_context import RoleContext
from role_passer_tree import build_passer_tree
from role_scorer_tree import build_scorer_tree
from role_goalie_tree import build_goalie_tree


class BehaviorController:
    @property
    def tree_state(self):
        return self._tree.tree_state

    def __init__(self, is_goalie: bool = False, role: str = "passer"):
        self._is_goalie = is_goalie
        self._role = role
        self._ctx = RoleContext()
        if is_goalie:
            graph = build_goalie_tree()
        elif role == "passer":
            graph = build_passer_tree()
        else:
            graph = build_scorer_tree()
        self._tree = TreeExecutor(graph)

    def reset_state(self):
        st = self._tree.tree_state
        if "next" in st:
            st["next"] = 0
            if "sequence" in st and st["sequence"]:
                st["action"] = st["sequence"][0]
        st["command"] = None
        if "status" in st:
            st["status"] = "init"

    def choose_command(
        self,
        visible: dict,
        game_on: bool,
        squad: str = "",
        side: str = "",
        unum: int = 0,
        pos_x=None,
        pos_y=None,
        last_heard_msg=None,
    ) -> tuple[str, str] | None:
        if not game_on:
            return None
        self._ctx.set_observation(
            visible, squad, side, unum, pos_x, pos_y, last_heard_msg
        )
        result = self._tree.run(self._ctx)
        if result and isinstance(result, tuple) and len(result) == 2:
            return result
        return None
