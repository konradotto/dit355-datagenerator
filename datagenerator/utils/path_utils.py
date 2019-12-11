import pathlib


def get_project_root() -> pathlib.Path:
    """Returns project root folder."""
    return pathlib.Path(__file__).parent.parent.parent


def get_data_path() -> pathlib.Path:
    """Returns the project resource folder data."""
    return get_project_root().joinpath('data')
