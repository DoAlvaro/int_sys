"""Базовый класс уровня иерархии: process -> вызов верхнего -> merge."""
# noqa: D100


class LayerController:
    """Один уровень: process(input) -> результат, при наличии верхнего — execute(upper) и merge."""

    def __init__(self):
        self.memory = {}

    def execute(self, input_data, upper_controllers):
        result = self.process(input_data)
        if upper_controllers:
            next_ctrl = upper_controllers[0]
            rest = upper_controllers[1:]
            upper_result = next_ctrl.execute(result, rest)
            return self.merge(result, upper_result)
        return self.finalize(result)

    def process(self, input_data):
        return input_data

    def merge(self, own_result, upper_result):
        if upper_result:
            return upper_result
        return own_result

    def finalize(self, result):
        return result
