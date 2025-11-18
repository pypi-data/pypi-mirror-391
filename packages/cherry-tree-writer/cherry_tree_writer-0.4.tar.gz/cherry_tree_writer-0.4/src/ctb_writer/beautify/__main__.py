import sys
from .text import parse

example = """
Test [(bold|underline)]bold_text[/]

what is [[(nothing)]]

[(underline)]test[[(nope)]][/]

Am i [(underline)]Underlined[/]

[(italic)]Italic[/]
END !
"""

if len(sys.argv) != 2:
	print("Usage: parse <text_to_parse>\n")
	print(parse(example))

else:
	to_parse = sys.argv[1]
	print(parse(to_parse))
