"""
Objects available on Cherry Tree such as: table, codebox and images

https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses
"""
import xml.etree.ElementTree as ET
from dataclasses import dataclass

__all__ = ["CherryTreeCodebox",
           "CherryTreeTable",
           "CherryTreeImage"]


### Cherry Tree default fields for object
@dataclass
class _CherryTreePositionalObject:
    position: int

@dataclass
class _CherryTreePositionalObjectDefault:
    justification: str = "left"

@dataclass
class _CherryTreeObject(_CherryTreePositionalObjectDefault, _CherryTreePositionalObject):
    pass

### Cherry Tree codebox
@dataclass
class _CherryTreeCodeboxDefault(_CherryTreeObject):
    width: int = 700
    height: int = 400
    is_width_pix: int = 1 # Size is given in pixels or in percent
    highlight_brackets: int = 1
    show_line_numbers: int = 1

@dataclass
class _CherryTreeCodeboxBase():
    txt: str
    syntax: str

@dataclass
class CherryTreeCodebox(_CherryTreeCodeboxDefault, _CherryTreeCodeboxBase):
    pass

### Cherry Tree table
@dataclass
class _CherryTreeTableBase():
    content: list

@dataclass
class _CherryTreeTableDefault(_CherryTreeObject):
    col_min: int = 250
    col_max: int = 250

@dataclass
class CherryTreeTable(_CherryTreeTableDefault, _CherryTreeTableBase):
    """
    Class for representing a Table in cherry tree

    In ctb:
      <?xml version="1.0" encoding="UTF-8"?>
        <table col_widths="0,0,0">
           <row><cell>a1</cell>
                <cell>aa1</cell>
                <cell>aaa1</cell>
            </row><row>
                <cell>a2</cell>
                <cell>aa2</cell>
                <cell>aaa2</cell>
            </row>
        </table>
    """
    def get_table(self):
        """
        Return the table as xml string
        """
        if not self.content:
            return ""
        num_col = len(self.content[0])
        header_width = "0,"*num_col
        xml = ET.Element("table", attrib={"col_widths": header_width[:-1]})
        for row in self.content:
            new_row = ET.Element("row")
            for cell in row:
                new_cell = ET.Element("cell")
                new_cell.text = cell
                new_row.append(new_cell)
            xml.append(new_row)
        return ET.tostring(xml, encoding="UTF-8", xml_declaration=True)

    @classmethod
    def from_xml(cls, xml_string, position, **kwargs):
        """
        Build a cherry tree table from the xml
        """
        table_xml = ET.fromstring(xml_string)
        content = []
        for row_elem in table_xml.iter("row"):
            row = []
            for cell in row_elem.iter("cell"):
                if cell.text is not None:
                    row.append(cell.text)
                else:
                    row.append("")

            content.append(row)
        return cls(content=content, position=position, **kwargs)

### Cherry Tree image
@dataclass
class _CherryTreeImageBase():
    """Class holding image information"""
    data: bytes

@dataclass
class CherryTreeImage(_CherryTreeObject, _CherryTreeImageBase):
    """Class holding image information"""
    pass
