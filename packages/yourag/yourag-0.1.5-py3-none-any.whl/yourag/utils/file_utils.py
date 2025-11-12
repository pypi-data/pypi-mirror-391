from pathlib import Path


def get_root_project():
    """
    Returns the root directory of the project.

    :return Path: Path object representing the root project directory.
    """
    return Path(__file__).resolve().parent.parent.parent
