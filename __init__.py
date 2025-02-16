import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent))
print(sys.path)

try:
    from src.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

    __all__ = ["NODE_DISPLAY_NAME_MAPPINGS", "NODE_CLASS_MAPPINGS"]
except ImportError as e:
    print(
        f"Could not import from {sys.path=}: \n"
        f"from src.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS"
    )
    raise e
