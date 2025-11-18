import pytest
from ctb_writer import CherryTreeNodeBuilder
from ctb_writer.beautify import parse
from ctb_writer.beautify.text_parser import Tokenizer

DEFAULT_TEXT = """
[(bold|underline|italic)]bold_underline_italic_text[/]
[[(Escaped)]]

[(size:small|fg:green)]test[/]
""".strip()

XML_BOLD_UNDERLINE_ITALIC = '<node><rich_text weight="heavy" underline="single" style="italic">'
XML_BOLD_UNDERLINE_ITALIC += 'test</rich_text></node>'

XML_SMALL_GREEN = '<node><rich_text foreground="#008000" scale="small">test</rich_text></node>'

def test_parse_text():
    assert parse(DEFAULT_TEXT) == [('bold|underline|italic', 'bold_underline_italic_text'),
                                   ('', '\n'),
                                   ('', '[(Escaped)]'),
                                   ('', '\n\n'),
                                   ('size:small|fg:green', 'test')]

def test_node_parsing():
    node = CherryTreeNodeBuilder("test").texts("[(bold|italic|underline)]test[/]").get_node()
    assert node.is_richtext

    xml_content = "\n".join(node.get_text().split("\n")[1:])
    assert xml_content == XML_BOLD_UNDERLINE_ITALIC

def test_size_and_color():
    node = CherryTreeNodeBuilder("test").texts("[(size:small|fg:green)]test[/]").get_node()

    xml_content = "\n".join(node.get_text().split("\n")[1:])
    assert xml_content == XML_SMALL_GREEN

def test_escaped_char():
    node = CherryTreeNodeBuilder("test").texts("[[(Escaped)]]").get_node()

    xml_content = "\n".join(node.get_text().split("\n")[1:])
    assert xml_content == "<node><rich_text>[(Escaped)]</rich_text></node>"

def test_plaintext():
    node = CherryTreeNodeBuilder("test", type="plain").text("Test").eol().get_node()

    assert node.get_text() == "Test\n"

