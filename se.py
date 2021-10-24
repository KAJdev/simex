from __future__ import annotations
from typing import Iterable, List, Optional, Union

"""
Simple Expressions: A shitty regex engine

Characters:
    *       Any character (stops at the first instance of the proceding character or end of string)
    ?       Optional proceding character

Escape with backslash
"""

def compile(expression: str) -> Compiled:
    """Compile a simple expression to be matched against strings"""
    e = Compiled(expression)
    e.tokenize()
    return e

def findall(expression: Union[Compiled,str], string: str) -> List[str]:
    """Find all matches of expression in string"""
    if isinstance(expression, str):
        expression = compile(expression)
    return expression.findall(string)

def _peek(iter: Iterable, index: int) -> Optional[any]:
    """Peek at the specified index"""
    if index < len(iter):
        return iter[index]
    return None

def _advance(ls: List[any]) -> Optional[any]:
    """Advance the list by one element in FIFO order"""
    try:
        return ls.pop(0)
    except IndexError:
        return None

def _advance_peek(ls: List[any]) -> Optional[any]:
    """Peek the list by one element in FIFO order"""
    try:
        return ls[0]
    except IndexError:
        return None

class Compiled():
    """A compiled simple expression"""
    def __init__(self, expression: str) -> None:
        self.expression = expression

    def tokenize(self) -> None:
        """Tokenize the expression"""
        self.tokens = []
        for i,char in enumerate(self.expression):
            if char == "*":
                self.tokens.append(Token(_peek(self.expression, i+1), TokenType.ANY))
            elif char == "?":
                self.tokens.append(Token(_peek(self.expression, i+1), TokenType.OPTIONAL))
            elif char == "\\":
                self.tokens.append(Token(_peek(self.expression, i+1), TokenType.ESCAPE))
            else:
                self.tokens.append(Token(char, TokenType.CHAR))

    def __repr__(self) -> str:
        return f"<Compiled {self.expression} {self.flags}>"

    def __str__(self) -> str:
        return f"{self.expression} {self.flags}"

    def __eq__(self, other: Compiled) -> bool:
        return (self.expression, self.flags) == (other.expression, other.flags)

    def __hash__(self) -> int:
        return hash((self.expression, self.flags))

    def findall(self, string: str) -> List[str]:
        """Find all matches of expression in string"""
        
        string = list(string)
        matches = []

        while len(string) > 0:
            tokens = self.tokens.copy()
            match = []

            while len(tokens) > 0:
                token = _advance(tokens)
                char = _advance(string)

                if token is None:
                    break
                if char is None and token.type != TokenType.OPTIONAL:
                    match = []
                    break

                value = token.match(tokens, string, char)
                if value is None:
                    match = []
                    break
                match.extend(value)
            
            if len(match) > 0:
                matches.append(''.join(match))

        return matches

        
class Token():
    """A token in a simple expression"""
    def __init__(self, value: str, type: TokenType) -> None:
        self.value = value
        self.type = type

    def __repr__(self) -> str:
        return f"<Token {self.value} {self.type}>"

    def __str__(self) -> str:
        return f"{self.value} {self.type}"

    def __eq__(self, other: Token) -> bool:
        return (self.value, self.type) == (other.value, other.type)

    def __hash__(self) -> int:
        return hash((self.value, self.type))

    def match(
        self,
        tokens: List[Token],
        chars: List[str],
        char: str
    ) -> Optional[List[str]]:
        """Match the token against the characters"""

        match = []
        if self.type == TokenType.ESCAPE:
            _advance(tokens)
            if self.value == char:
                match.append(char)
            else:
                return None
        elif self.type == TokenType.OPTIONAL:
            token = _advance(tokens)

            value = token.match(tokens, chars, char)
            if value is not None:
                match.extend(value)
            else:
                _advance(tokens)
        elif self.type == TokenType.ANY:
            match.append(char)
            if char != self.value:
                while self.value != (peek := _advance_peek(chars)) and peek is not None:
                    match.append(peek)
                    char = _advance(chars)
            else:
                _advance(tokens)
        elif self.type == TokenType.CHAR:
            if self.value == char:
                match.append(char)
            else:
                return None

        return match

class TokenType:
    """Types of tokens"""
    CHAR = 0
    ANY = 1
    OPTIONAL = 2
    ESCAPE = 3
