"""
Link cherry tree instance to the database
"""
import sqlite3
import os
from time import time
from .cherry_tree_rows import _NodeRow, _ImageRow, _CodeboxRow, _TableRow
from .cherry_tree_node import CherryTreeNode, CherryTreeCodeNode, CherryTreePlainNode
from ctb_writer.assets import *

class CherryTreeLink:
    """
    Cherry Tree link to the database
    ./src/ct/ct_storage_sqlite.cc --> Some implementations of the columns

    TODO:
     - Use INSERT or REPLACE and CREATE TABLE IF NOT EXISTS
    """
    def __init__(self, name):
        self.name = name
        self.con = sqlite3.connect(self.name)
        self.cursor = self.con.cursor()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        """
        Checks that the extension is a valid CherryTree one. On
        empty extensions, it will add '.ctb'

        :raises ValueError: If the extension is not .ctb and not empty
        """
        fname, ext = os.path.splitext(val)

        if ext == "":
            self._name = f"{val}.ctb"

        elif ext != ".ctb":
            raise ValueError(f"Extension {val} is not supported "
                             "for cherry tree document")
        else:
            self._name = val

    def get_nodes(self):
        """
        Recover nodes from the database
        """
        root_nodes = self.recover_root_nodes()
        for root_node in root_nodes:
            self._recover_nodes_recurse(root_node)
        return root_nodes

    def recover_root_nodes(self):
        """
        Recover the root nodes of the document
        """
        root_nodes = []
        rows = self.cursor.execute("""SELECT node_id, father_id, sequence
                                      FROM children
                                      WHERE father_id=0
                                      ORDER BY sequence ASC""")

        for row in rows.fetchall():
            root_nodes.append(self.recover_node(row[0]))
        return root_nodes

    def _recover_nodes_recurse(self, father):
        """
        Recover all the nodes recursively

        :param father: The father node
        :type father: class:`_CherryTreeNodeBase`
        """
        rows = self.cursor.execute("""SELECT node_id, father_id, sequence
                                      FROM children
                                      WHERE father_id=?
                                      ORDER BY sequence ASC""", (father.node_id,))

        for children in rows.fetchall():
            child = self.recover_node(children[0])
            child.father_id = father.node_id
            self._recover_nodes_recurse(child)
            father.append(child)

    def recover_node(self, node_id):
        """
        Recover a node from the table node

        :param node_id: The id of the node to recover
        :type node_id: int
        """
        rows = self.cursor.execute("""SELECT node_id, name, txt, syntax,
                                             tags, is_ro, is_richtxt, has_codebox,
                                             has_table, has_image
                                      FROM node WHERE node_id=?""", (node_id,))
        row = rows.fetchone()
        if row:
            is_richtext = row[_NodeRow.IS_RICHTEXT] & 0x1
            syntax = row[_NodeRow.SYNTAX]
            tags = None
            if row[_NodeRow.TAGS]:
                tags = row[_NodeRow.TAGS].split(" ")

            if is_richtext:
                has_image = row[_NodeRow.HAS_IMAGE]
                has_table = row[_NodeRow.HAS_TABLE]
                has_codebox = row[_NodeRow.HAS_CODEBOX]
                node = CherryTreeNode(row[_NodeRow.NAME])
                node.node_id = row[_NodeRow.NODE_ID]
                if has_image:
                    self._recover_image(node)
                if has_table:
                    self._recover_table(node)
                if has_codebox:
                    self._recover_codebox(node)

            elif syntax == 'plain-text':
                node = CherryTreePlainNode(row[_NodeRow.NAME])
                node.node_id = row[_NodeRow.NODE_ID]

            else:
                node = CherryTreeCodeNode(row[_NodeRow.NAME], syntax=syntax)
                node.node_id = row[_NodeRow.NODE_ID]

            node.set_text(row[_NodeRow.TXT])

            _ColumnConvert.from_ro(node, row[_NodeRow.IS_RO])
            _ColumnConvert.from_richtext(node, row[_NodeRow.IS_RICHTEXT])

            return node
        raise ValueError(f"Node {node_id} not found in database")

    def _recover_codebox(self, node):
        """
        Recover codebox for a given node
        """
        rows = self.cursor.execute("""SELECT node_id, offset, justification, txt, syntax,
                                             width, height, is_width_pix, do_highl_bra, do_show_linenum
                                      FROM codebox WHERE node_id=?""", (node.node_id, ))
        for row in rows.fetchall():
            codebox_db = CherryTreeCodebox(txt=row[_CodeboxRow.TXT],
                                        syntax=row[_CodeboxRow.SYNTAX],
                                        position=row[_CodeboxRow.OFFSET],
                                        justification=row[_CodeboxRow.JUSTIFICATION],
                                        width=row[_CodeboxRow.WIDTH],
                                        height=row[_CodeboxRow.HEIGHT],
                                        is_width_pix=row[_CodeboxRow.IS_WIDTH_PIX],
                                        highlight_brackets=row[_CodeboxRow.HIGHLIGHT_BRACKETS],
                                        show_line_numbers=row[_CodeboxRow.SHOW_LINE_NUMBERS])
            node.codebox.append(codebox_db)

    def _recover_image(self, node):
        """
        Recover image for a given node
        """
        rows = self.cursor.execute("""SELECT node_id, offset, justification, anchor, png
                                      FROM image WHERE node_id=?""", (node.node_id, ))
        for row in rows.fetchall():
            image = CherryTreeImage(position=row[_ImageRow.OFFSET],
                                    data=row[_ImageRow.PNG],
                                    justification=row[_ImageRow.JUSTIFICATION])
            node.images.append(image)

    def _recover_table(self, node):
        """
        Recover the tables for a given node
        """
        rows = self.cursor.execute("""SELECT node_id, offset, justification, txt,
                                             col_min, col_max
                                      FROM grid WHERE node_id=?""", (node.node_id, ))
        for row in rows.fetchall():
            table_to_add = CherryTreeTable.from_xml(row[_TableRow.TXT],
                                                    position=row[_TableRow.OFFSET],
                                                    justification=row[_TableRow.JUSTIFICATION],
                                                    col_min=row[_TableRow.COL_MIN],
                                                    col_max=row[_TableRow.COL_MAX])
            node.tables.append(table_to_add)

    def save(self, nodes):
        """
        Save a node to the database

        :param node: The node to save
        :type node: class:`CherryTreeNode`
        """
        self._save_children_recurse(nodes)
        self._save_node_recurse(nodes)

    def _save_images(self, node):
        """
        Save images of a node
        """
        for image in node.images:
            self.cursor.execute(
                            """INSERT INTO image
                            (node_id, offset, justification, png)
                            VALUES (?, ?, ?, ?)
                            """,
                            (node.node_id, image.position, image.justification, image.data)
                            )

    def _save_codebox(self, node):
        """
        Save codebox of a node
        """
        for codebox in node.codebox:
            self.cursor.execute(
                            """INSERT INTO codebox
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (node.node_id, codebox.position, codebox.justification,
                             codebox.txt, codebox.syntax, codebox.width,
                             codebox.height, codebox.is_width_pix, codebox.highlight_brackets,
                             codebox.show_line_numbers)
                            )

    def _save_table(self, node):
        """
        Save table of a node
        """
        for table in node.tables:
            self.cursor.execute(
                            """INSERT INTO grid
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (node.node_id, table.position, table.justification,
                             table.get_table(), table.col_min, table.col_max)
                            )

    def _save_node_recurse(self, nodes):
        """
        Save the nodes recursively

        :param nodes: The list of nodes to save
        :type nodes: List[class:`CherryTreeNode`]
        """
        for node in nodes:
            if not node.is_last_node:
                self._save_node_recurse(node.children)
            self.cursor.execute(
                            """INSERT INTO node
                            (node_id,
                             name,
                             txt,
                             syntax,
                             tags,
                             is_ro,
                             is_richtxt,
                             has_codebox,
                             has_table,
                             has_image,
                             level,
                             ts_creation,
                             ts_lastsave)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (node.node_id,
                             node.name,
                             node.get_text(),
                             node.syntax,
                             node.get_tags(),
                             _ColumnConvert.to_ro(node),
                             _ColumnConvert.to_richtext(node),
                             node.has_codebox,
                             node.has_table,
                             node.has_image,
                             0,
                             int(time())-2,
                             int(time()))
                            )
            if node.has_image:
                self._save_images(node)

            if node.has_codebox:
                self._save_codebox(node)

            if node.has_table:
                self._save_table(node)

            self.con.commit()

    def _save_children_recurse(self, nodes):
        """
        Save the children of nodes recursively

        :param nodes: The list of nodes to save
        :type nodes: List[class:`CherryTreeNode`]
        """
        for seq, node in enumerate(nodes):
            self.cursor.execute(
                        """INSERT INTO children
                        (node_id, father_id, sequence, master_id)
                        VALUES (?, ?, ?, ?)
                        """,
                        (node.node_id, node.father_id, seq + 1, 0)
                        )
            self.con.commit()
            if not node.is_last_node:
                self._save_children_recurse(node.children)

    def init(self):
        """
        Init the document with the default tables and all
        """
        self.cursor.execute(
            """CREATE TABLE bookmark (
            node_id INTEGER UNIQUE,
            sequence INTEGER
            )
            """)

        self.cursor.execute(
            """CREATE TABLE children (
            node_id INTEGER UNIQUE,
            father_id INTEGER,
            sequence INTEGER,
            master_id INTEGER
            )
            """)

        self.cursor.execute(
            """CREATE TABLE codebox (
            node_id INTEGER,
            offset INTEGER,
            justification TEXT,
            txt TEXT,
            syntax TEXT,
            width INTEGER,
            height INTEGER,
            is_width_pix INTEGER,
            do_highl_bra INTEGER,
            do_show_linenum INTEGER
            )
            """
            )

        self.cursor.execute(
            """CREATE TABLE grid (
            node_id INTEGER,
            offset INTEGER,
            justification TEXT,
            txt TEXT,
            col_min INTEGER,
            col_max INTEGER
            )
            """
            )

        self.cursor.execute(
            """CREATE TABLE image (
            node_id INTEGER,
            offset INTEGER,
            justification TEXT,
            anchor TEXT,
            png BLOB,
            filename TEXT,
            link TEXT,
            time INTEGER
            )
            """)

        self.cursor.execute(
            """CREATE TABLE node (
            node_id INTEGER UNIQUE,
            name TEXT,
            txt TEXT,
            syntax TEXT,
            tags TEXT,
            is_ro INTEGER,
            is_richtxt INTEGER,
            has_codebox INTEGER,
            has_table INTEGER,
            has_image INTEGER,
            level INTEGER,
            ts_creation INTEGER,
            ts_lastsave INTEGER
            )
            """)

class _ColumnConvert:
    """
    This class allows to convert some column to the format expected
    """
    @staticmethod
    def from_ro(node, is_ro):
        """
        Set the values icon and is_ro from is_ro
        """
        node.is_ro = is_ro & 0x1
        node.icon = is_ro >> 1

    @staticmethod
    def from_richtext(node, is_richtext):
        """
        Set the values of the node from is_richtext
        """
        if (is_richtext >> 1) & 0x1:
            node.set_bold_title()

        if (is_richtext >> 2) & 0x1:
            color = hex((is_richtext >> 3) & 0xffffff)[2:]
            color = color.zfill(6)
            node.set_title_color(f"#{color}")

    @staticmethod
    def to_ro(node):
        """
        Extract the information from the node to
        add it as ro
        """
        return node.icon << 1 | node.is_ro

    @staticmethod
    def to_richtext(node):
        """
        Extract the information from the node to
        add it as richtext
        """
        title_style = node.get_title_style()
        is_richtext = node.is_richtext
        is_bold = 1 if title_style.get('bold', False) else 0
        is_foreground = 1 if title_style.get('color', None) is not None else 0
        color_int = 0

        if is_foreground:
            forecolor = title_style.get('color')[1:]
            color_int = int(forecolor, 16) << 3

        return color_int | is_foreground << 2 | is_bold << 1 | is_richtext

