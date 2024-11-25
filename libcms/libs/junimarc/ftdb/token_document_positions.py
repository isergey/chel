from collections import defaultdict
from typing import Dict, List, Tuple


class TokenDocumentPositions:
    def __init__(self):
        self.__positions: Dict[int, Dict[int, List[Tuple[int, int]]]] = defaultdict(lambda: defaultdict(list))

    def add_token_positions(self, token_id, document_id: int, positions: List[Tuple[int, int]]):
        for position in positions:
            begin, end = position
            self.add_token_position(
                token_id=token_id,
                document_id=document_id,
                begin=begin,
                end=end
            )

    def add_token_position(self, token_id, document_id: int, begin: int, end: int):
        self.__positions[token_id][document_id].append((begin, end))


    def get_token_positions(self, token_id: int, document_id:int) -> List[Tuple[int, int]]:
        token_documents = self.__positions.get(token_id)
        if token_documents is None:
            return []

        positions = token_documents.get(document_id)

        return positions