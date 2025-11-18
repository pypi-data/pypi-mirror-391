"""
Gather some assets of the cherry tree doc
"""
import warnings
from .node_icon import icons

def get_icon(icon_name):
	"""
	Return the icon associated to a string

	:param icon_name: The name of the icon
	:type icon_name: Union[str, int]

	:return: The value of the icon for cherry tree
	"""
	prefix_icon = "ct_"
	if isinstance(icon_name, int):
		value = icon_name
	else:
		if not icon_name.startswith(prefix_icon):
			icon_name = prefix_icon + icon_name
		value = icons.get(icon_name)
		if not value:
			warnings.warn(f"Icon {icon_name} not found, refers to:\n"
						  "python3 -m ctb_writer.icons",
						  )
			value = 0

	return value
