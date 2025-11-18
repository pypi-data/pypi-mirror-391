"""
Class representing a cherry tree node
"""
from copy import copy
from os.path import expanduser
from dataclasses import dataclass
from .beautify import CherryTreeRichtext, color
from .assets import *
import xml.etree.ElementTree as ET

class _CherryTreeNodeBase:
    """
    Base attributes for a cherry tree node
    """
    def __init__(self, name, father_id=0, icon=0, is_ro=0, children=None, tags=None):
        self.node_id = None
        self.name = name
        self.title_style = {"color": None, "bold": False}

        self.is_ro = is_ro
        self.icon = icon

        self.father_id = father_id
        self.children = [] if children is None else children
        self.tags = [] if tags is None else tags

    def append(self, child):
        """Add a children to the list"""
        self.children.append(child)

    def get_all_children_recurse(self):
        """
        return the list of all children of the current node
        recursively, and include the root node as the first element
        """
        all_children = [self]
        for child in self.children:
            all_children.extend(child.get_all_children_recurse())
        return all_children

    def __iter__(self):
        """Iter through all child nodes"""
        for node in self.get_all_children_recurse():
            yield node

    def get_tags(self):
        """
        Return the tags of the node for the db
        """
        if not self.tags:
            return None
        return " ".join(self.tags)

    @color
    def set_title_color(self, color):
        """
        Set the color of the title
        """
        self.title_style["color"] = color

    def set_bold_title(self):
        """
        Set the Node title as bold
        """
        self.title_style["bold"] = True

    def get_title_style(self):
        """
        Used to access the style of the title
        """
        return self.title_style

    @property
    def is_root_node(self):
        """Check if a node is the root node"""
        return self.father_id == 0

    @property
    def is_last_node(self):
        """Check if a node is the last one"""
        return len(self.children) == 0

    def __str__(self):
        return f"{self.__class__.__name__}(node_id={self.node_id},name=\"{self.name}\",icon={self.icon}" +\
               f",father_id={self.father_id},children={len(self.children)})"

class CherryTreeNode(_CherryTreeNodeBase):
    """
    Class holding node data for a richtext node
    """
    syntax = 'custom-colors'
    is_richtext = 1

    def __init__(self, name, father_id=0, icon=0, is_ro=0, children=None, tags=None):
        super().__init__(name, father_id, icon, is_ro, children, tags)

        self.xml = ET.fromstring(self.get_base_xml())
        self.images = []
        self.codebox = []
        self.tables = []

    @staticmethod
    def get_base_xml():
        return '<?xml version="1.0" encoding="UTF-8"?>\n<node/>'

    @property
    def entities(self):
        """
        Return the positionable entities (table, codebox and images)
        ordered by position
        """
        return sorted(self.images + self.codebox + self.tables,
                      key=lambda elt: elt.position)

    def extend(self, children):
        """Add a list of children to the current Node"""
        if not isinstance(children, list):
            raise ValueError("extend method expect a list as parameter")
        self.children.extend(children)

    def add_text(self, text, attrib={}):
        """
        Add rich text to the node

        :param text: The text to add to the node
        :type text: str
        """
        richtext = CherryTreeRichtext.from_attributes(text, attrib).get_xml()
        self.xml.append(richtext)

    def add_texts(self, texts):
        """
        Add multiple texts

        :param texts: The texts and style to add
        :type texts: List[Tuple[str, str]]

        example:
            [("bold|underline", "test")]            
        """
        for style, text in texts:
            richtext = CherryTreeRichtext.from_style(text, style).get_xml()
            self.xml.append(richtext)

    def replace(self, replace, replacement, style={}):
        """
        Replace a text, and can also change its style
        """
        for i in reversed(range(len(self.xml))):
            element = self.xml[i]
            if replace in element.text:
                new_elements = []
                parts = element.text.split(replace)

                for index, text_part in enumerate(parts):
                    new_style = style
                    if not new_style:
                        new_style = element.attrib
                    side_element_custom = CherryTreeRichtext.from_attributes(replacement, new_style).get_xml()

                    if text_part != "":
                        side_element = copy(element)
                        side_element.text = text_part
                        new_elements.append(side_element)
                    if index < len(parts)-1:
                        new_elements.append(side_element_custom)

                for new_element in reversed(new_elements):
                    self.xml.insert(i, new_element)
                self.xml.remove(element)

    def add_image(self, image_name, position=-1, justification="left"):
        """
        Add an image to the text

        :param image_name: The name of the image to add
        :type image_name: str

        :param position: The position of the images in the text
        :type position: int (default: -1)
        """
        image = None
        with open(expanduser(image_name), "rb") as file_image:
            image = file_image.read()

        if not image:
            return

        if position < 0:
            # In this case, append the image at the end of the text
            position = self._get_text_length()

        self.images.append(CherryTreeImage(image, position=position, justification=justification))

    def add_codebox(self, text, syntax, position=-1, **kwargs):
        """
        Add a codebox to the text with the syntax given

        :param text: The content of the codebox
        :type text: str

        :param syntax: The syntax to use for the code
        :type syntax: str
        """
        if position < 0:
            # In this case, append the codebox at the end of the text
            position = self._get_text_length()

        self.codebox.append(CherryTreeCodebox(text, syntax, position=position, **kwargs))

    def add_table(self, content, position=-1, **kwargs):
        """
        Add a table to the node

        :param content: The table content
        :type content: List[List]
        """
        if position < 0:
            # In this case, append the table at the end of the text
            position = self._get_text_length()
        self.tables.append(CherryTreeTable(content, position=position, **kwargs))

    def _get_text_length(self):
        """
        Recover the length of the text inside the xml
        """
        length = 0
        for text in self.xml.itertext():
            length += len(text)
        return length  

    @property
    def has_image(self):
        """
        Check if a node contains images or not

        :rtype: int
        """
        return 0 if len(self.images) == 0 else 1

    @property
    def has_codebox(self):
        """
        Check whether or not the node has codebox
        """
        return 0 if len(self.codebox) == 0 else 1

    @property
    def has_table(self):
        """
        Check whether or not the node has codebox
        """
        return 0 if len(self.tables) == 0 else 1

    def get_text(self):
        """Return the xml contained in the node which is xml on richtext"""
        if self.xml is None:
            return self.get_base_xml()
        return ET.tostring(self.xml, encoding="UTF-8", xml_declaration=True).decode("UTF-8")

    def set_text(self, text):
        """
        Set the text of the node as XML
        """
        self.xml = ET.fromstring(text)

class _CherryTreeTextNode(_CherryTreeNodeBase):
    """
    Class representing a node that contains only text
    """
    is_richtext = 0
    has_image = 0
    has_codebox = 0
    has_table = 0

    def __init__(self, name, txt="", father_id=0, icon=0, is_ro=0, children=None, tags=None):
        super().__init__(name, father_id, icon, is_ro, children, tags)
        self.txt = txt

    def get_text(self):
        """
        Get the text content
        """
        return self.txt

    def add_text(self, txt):
        """
        Add text to the node
        """
        self.txt += txt

    def set_text(self, text):
        """
        Set the text of the node to text
        """
        self.txt = text

class CherryTreeCodeNode(_CherryTreeTextNode):
    """
    Class holding node data for a code node
    """
    def __init__(self, name, syntax, txt="", father_id=0, icon=0, is_ro=0, children=None, tags=None):
        super().__init__(name, txt, father_id, icon, is_ro, children, tags)
        self.syntax = syntax

class CherryTreePlainNode(_CherryTreeTextNode):
    """
    Class holding node data for a richtext node
    """
    syntax = "plain-text"

    def __init__(self, name, txt="", father_id=0, icon=0, is_ro=0, children=None, tags=None):
        super().__init__(name, txt, father_id, icon, is_ro, children, tags)

