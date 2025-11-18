"""
This module allow to parse a text and format it then

source: https://docs.python.org/3/library/re.html
"""
import re
from typing import NamedTuple

class Token(NamedTuple):
    """
    Class representing a token in a text
    """
    type: str
    value: str
    column: int

class Tokenizer:
    """
    Tokenizer for a text

    Usage:

        >>> Tokenizer.tokenize("Hey I am [(bold|underline|color:#546456)]Styles TEXT[/]")
    """
    token_specification = [
        ("ESCAPE", r"\[\[.*?\]\]"), # Escape a tag with [[(escaped)]] -> [(escaped)]
        ("START", r"\[\(.+?\)\]"), # Start tag like: [(bold|underline)]
        ("END", r"\[/\]"), # End tag such as: [/]
    ]

    @classmethod
    def tokenize(cls, text):
        """
        Tokenize the text
        """
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in cls.token_specification)
        for mo in re.finditer(tok_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start()
            yield Token(kind, value, column)



if __name__ == "__main__":
    test = """[(bold|underline)]bold_underlined_text[/]

    what is [[(nothing)]]

    Am i [(underline)]Underlined[/]

    [[(Test)]][(italic)]Italic[/]
    END !
    """

    for token in Tokenizer.tokenize(test):
        print(token)


