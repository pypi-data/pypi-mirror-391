"""
Class that allow to build a node given the parameters wanted
"""
from os.path import expanduser
from .icons import get_icon
from .beautify import parse
from .cherry_tree_node import CherryTreeNode, CherryTreeCodeNode, CherryTreePlainNode
import xml.etree.ElementTree as ET

class CherryTreeNodeBuilder:
    """
    Builder for a cherry tree node
    """
    def __init__(self, name, type="rich", syntax=None, color=None, bold=False):
        if type == "rich":
            self.node = CherryTreeNode(name)
        elif type == "plain":
            self.node = CherryTreePlainNode(name)

        elif type == "code":
            if syntax == None:
                raise ValueError(f"Code node cannot be initialized without a syntax")
            self.node = CherryTreeCodeNode(name, syntax)
        else:
            raise ValueError(f"Unknow node type {type!r}, choose between: 'rich', 'plain' and 'code'")

        if bold:
            self.node.set_bold_title()

        if color:
            self.node.set_title_color(color)

    def icon(self, name):
        """
        Add Icon to the given node
        """
        self.node.icon = get_icon(name)
        return self

    def eol(self):
        """
        Add Line feed at the end
        """
        return self.text("\n")

    def text(self, text, style={}):
        """
        Add the Text to a node
        """
        if self.node.is_richtext:
            self.node.add_text(text, attrib=style)
        else:
            self.node.add_text(text)
        return self

    def texts(self, texts):
        """
        Add multiple texts to a node
        If texts is a string, it will be automatically parsed
        """
        if self.node.is_richtext:
            if isinstance(texts, str):
                texts = parse(texts)
            self.node.add_texts(texts)
        else:
            raise ValueError("Cannot add multiple texts to a node which is not richtext")
        return self

    def image(self, filename, position=-1, justification="left"):
        """
        Insert an image in the node, at the given position, default position is
        "-1" that refers to the end of text

        :param filename: The path to the images to insert
        :type filename: str

        :param position: The position of the images in the text
        :type position: int (default: -1)
        """
        self.node.add_image(filename, position=position, justification=justification)
        return self

    def codebox(self, text, syntax, **kwargs):
        """
        Add a codebox to the given node

        :param text: The content of the codebox
        :type text: str

        :param syntax: The syntax to use for coloring code
        :type syntax: str
        """
        self.node.add_codebox(text, syntax.lower(), **kwargs)
        return self

    def table(self, content, **kwargs):
        """
        Add a table to the node
        """
        self.node.add_table(content, **kwargs)
        return self

    def set_read_only(self):
        """
        Set the node as read only
        """
        self.node.is_ro = 1
        return self

    def get_node(self):
        """
        Return the associated node
        """
        return self.node
