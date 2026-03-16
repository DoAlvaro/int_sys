"""Контроллер по таблице действий: goalie / attacker / defender."""
from action_table import ActionTable
from ta_context import TAContext
from attacker_table import build_attacker_table
from defender_table import build_defender_table
from goalie_table import build_goalie_table


class BehaviorController:
    def __init__(self, role: str, squad: str, side: str, unum: int):
        self._ctx = TAContext()
        if role == "goalie":
            table = build_goalie_table()
        elif role == "attacker":
            table = build_attacker_table()
        else:
            table = build_defender_table()
        self._table = ActionTable(table)

    def reset_state(self):
        self._table.reset_state()

    def choose_command(
        self,
        visible: dict,
        game_on: bool,
        squad: str = "",
        side: str = "",
        unum: int = 0,
        time_cycle: int = 0,
    ) -> tuple[str, str] | None:
        if not game_on:
            return None
        self._ctx.set_observation(visible, squad, side, unum, time_cycle)
        return self._table.next_step(self._ctx)
