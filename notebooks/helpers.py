import shutil
from functools import cache
from os import getcwd
from pathlib import Path


# =================================================================================================
#  Folders
# =================================================================================================
@cache
def get_project_folder() -> Path:
    """Get top-level folder of the project."""
    path = Path(getcwd())
    while not (path / "pyproject.toml").exists():
        path = path.parent
        if path == path.parent:
            raise FileNotFoundError("Project folder not found.")
    return path


@cache
def get_data_folder() -> Path:
    """Get the path to the MAIN data folder."""
    folder = get_project_folder() / "_data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@cache
def get_images_folder() -> Path:
    """Get the path to test images."""
    folder = get_data_folder() / "images"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@cache
def get_figures_folder() -> Path:
    """Get the path where to save figures to."""
    folder = get_data_folder() / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


# =================================================================================================
#  Metadata switching
# =================================================================================================
def enable_metadata(embedding_size: int):
    """Copy metadata-llava7b-jina<n> -> metadata, such that embeddings with the requested size will be used."""
    dst_path = get_images_folder() / "metadata"
    src_path = get_images_folder() / f"metadata-llava7b-jina{embedding_size}"

    # delete and recreate target folder
    if dst_path.exists():
        shutil.rmtree(dst_path)
    dst_path.mkdir(exist_ok=True, parents=True)

    # copy file by file
    for src_file in src_path.glob("*"):
        dst_file = dst_path / src_file.name
        shutil.copy(src_file, dst_file)
