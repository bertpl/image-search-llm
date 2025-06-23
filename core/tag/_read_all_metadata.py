import json
from pathlib import Path

from core.data import ImageMetadata


def read_all_metadata(image_directory: Path) -> list[ImageMetadata]:
    """
    Reads all metadata files in the specified directory and returns a list of metadata objects.

    Args:
        image_directory (Path): The directory containing the metadata files.

    Returns:
        list[dict]: A list of metadata dictionaries.
    """
    # determine all potential metadata files
    files = list((image_directory / "metadata").glob("*.json"))

    # try to read one by one and put in a list
    metadata_list = []
    for file in files:
        metadata = read_metadata(file)
        if metadata:
            metadata_list.append(metadata)

    # return
    return metadata_list


def read_metadata(metadata_path: Path) -> ImageMetadata | None:
    """
    Load image metadata from a JSON file.
    :param metadata_path: Path to the metadata JSON file.
    :return: ImageMetadata object if the file exists and is valid, otherwise None.
    """
    if not metadata_path.exists():
        return None
    else:
        try:
            # load and deserialize metadata
            with open(metadata_path, "r") as f:
                data = json.load(f)
            return ImageMetadata.model_validate(data)
        except Exception as e:
            print(f"Error reading metadata for {metadata_path}: {e}")
            return None

