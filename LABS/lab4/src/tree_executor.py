"""Исполнение дерева решений (как в lab3)."""
# noqa: D100


class TreeExecutor:
    def __init__(self, graph: dict):
        self._graph = graph

    @property
    def tree_state(self):
        return self._graph["state"]

    def run(self, ctx) -> tuple | None:
        return self._traverse(ctx, "root")

    def _traverse(self, ctx, node_name: str):
        node = self._graph[node_name]
        if "exec" in node:
            node["exec"](ctx, self.tree_state)
            return self._traverse(ctx, node["next"])
        if "condition" in node:
            if node["condition"](ctx, self.tree_state):
                return self._traverse(ctx, node["trueCond"])
            return self._traverse(ctx, node["falseCond"])
        if "command" in node:
            return node["command"](ctx, self.tree_state)
        raise ValueError(f"Узел {node_name} не содержит exec/condition/command")
