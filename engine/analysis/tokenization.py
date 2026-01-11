import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    token_id: str
    surface: str
    start: int
    end: int


TOKEN_RE = re.compile(r"\S+")


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(text):
        token_id = f"t{len(tokens) + 1}"
        tokens.append(Token(token_id, match.group(0), match.start(), match.end()))
    return tokens


def tokens_to_payload(tokens: list[Token]) -> list[dict]:
    return [
        {
            "token_id": token.token_id,
            "surface": token.surface,
            "span": {"start": token.start, "end": token.end},
        }
        for token in tokens
    ]
