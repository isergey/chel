from typing import Tuple


class Token:
    def __init__(self, value: str, position: Tuple[int, int], order=0):
        self.value = value
        self.position = position
        self.order = order

    def __repr__(self):
        return f'{"{"}value:{self.value},positions:{self.position},order:{self.order}{"}"}'