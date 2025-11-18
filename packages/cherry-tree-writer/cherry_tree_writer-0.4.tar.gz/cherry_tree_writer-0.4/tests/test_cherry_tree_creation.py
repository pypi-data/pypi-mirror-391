from ctb_writer import CherryTree, CherryTreeNodeBuilder

COMPLEX_TEXT = """\
[(fg:sun|bold)]Welcome[/] on my cutsom node ! 🍥

[(underline|fg:salmon)]Take your notes:[/]
  - Install [(underline|fg:sun)]cherry_tree_writer[/]
  - Read the [(bold)]README.md[/] file
  - Create your first [(bg:mediumspringgreen)]document[/]

You can use this [(bold)]library[/] like this:

"""

CODEBOX = """\
from ctb_writer import CherryTree, CherryTreeNodeBuilder

document = CherryTree()
document.add_child("Root node", icon="add", text="This is the root node 🍕")
document.save("/tmp/test.ctb")
"""

def test_create_complex_cherry_tree():
    document = CherryTree()

    root_id = document.add_child("Root node", icon="add", text="This is the root node 🍕")

    richtext_builder = CherryTreeNodeBuilder("Rich node").icon("execute")
    richnode = richtext_builder.texts(COMPLEX_TEXT).codebox(CODEBOX, "python", height=1).eol().get_node()

    document.add_child(richnode, icon="execute", parent_id=root_id)

    plainnode = CherryTreeNodeBuilder("Plain node", type="plain").icon("json").text("test").eol().get_node()
    document.add_child(plainnode, parent_id=root_id)

    codenode = CherryTreeNodeBuilder("Code node", type="code", syntax="python").icon("python").text(CODEBOX).eol().get_node()
    document.add_child(codenode, parent_id=root_id)

def test_entities_order():
    node = CherryTreeNodeBuilder("Rich node").table([["Test"]]).eol().codebox(CODEBOX, "python", position=0).eol().get_node()
    assert len(node.entities) == 2
    assert node.entities[1] == node.tables[0]
    assert node.entities[0] == node.codebox[0]

