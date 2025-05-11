# views.py
from django.db.models.manager import BaseManager
from .models import Track
def build_tree(tracks: BaseManager["Track"]) -> list[dict]:
    """
    Takes a list of Track objects and returns a hierarchical folder structure.
    Omits the first two parts of the path (e.g., '/home/') and builds the tree from there.
    """
    tree = []
    path_parts_dict = {}

    for track in tracks:
        # Split the path into parts
        path_parts = track.file_path.split("/")

        # Omit the first two parts (e.g., '/' and 'home')
        relevant_path = path_parts[2:]

        # Build the full path string for display
        display_path = "/".join(relevant_path)

        # Current level in the tree
        current_level = path_parts_dict

        # Iterate through each part of the path
        for part in relevant_path:
            if part not in current_level:
                # Create a new node
                current_level[part] = {"name": part, "children": {}}
            # Move to the next level
            current_level = current_level[part]["children"]

    # Convert the dictionary to a list of nodes for the template
    return [
        {"name": key, "children": value["children"], "is_folder": True}
        for key, value in path_parts_dict.items()
    ]


def build_node(node, level=0):
    """
    Recursively builds the tree structure for the template.
    """
    return {
            "name": node["name"],
            "children": [
                build_node(child, level + 1) for child in node["children"].values()
            ],
            "level": level,
            "is_folder": node.get("is_folder", False),
        }
