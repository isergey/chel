from typing import List
from .token import Token

def tokenize(text: str) -> List[Token]:
    order = 0
    tokens: List[Token] = []
    token_started = False
    begin = 0
    current_token = []
    for i, c in enumerate(text):
        if c.isalnum():
            if not token_started:
                token_started = True
                begin = i
            current_token.append(c)
        else:
            token_started = False
            if current_token:
                tokens.append(Token(
                    value=''.join(current_token),
                    position=(begin, i - 1),
                    order=order
                ))
                order += 1
                current_token = []
    return tokens