from typing import List


class BinaryQuery:
    def __init__(self, op: str, token_ids: List[str]):
        self.op = op
        self.token_ids = token_ids


