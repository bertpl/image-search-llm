import time
from pathlib import Path
from typing import Literal

import ollama

from core.data import EmbeddingModel, ImageEmbeddings, ImageMetadata, SearchData

from .embeddings import (
    construct_embedding_from_image,
    construct_embedding_from_search_data,
)
from .exif import extract_time_and_location


# =================================================================================================
#  Main tagging functionality
# =================================================================================================
def tag_image(
    image_path: Path,
    metadata_path: Path,
    model: str,
    geolookup: Literal["off", "offline", "online"],
    embedding_size: int,
):
    """
    Tag single image and save metadata.  'Tag' is used in a broad sense here, meaning that we extract
    all relevant metadata for future search actions, including, tags, description, and potentially other properties
    in the future.
    :param image_path: Path to the image file to be tagged.
    :param metadata_path: Path to the metadata file where the extracted metadata will be saved.
    :param model: Name of the model to use.
    :param geolookup: How to resolve GPS coordinates into address/city info.
                       - off: do not resolve GPS coordinates
                       - offline: use offline reverse geocoding (requires reverse_geocode package)
                       - online: use online reverse geocoding using Nominatim (requires internet connection)
    :param embedding_size: Size of the embeddings to be extracted.  0 means no embeddings are extracted.
    """

    # --- extract search data -----------------------------
    t_start = time.time_ns()
    time_info, location_info = extract_time_and_location(image_path, geolookup)  # extract time & location from EXIF
    search_data = SearchData(
        description=_extract_description(image_path, model),
        tags=_extract_tags(image_path, model),
        time=time_info,
        location=location_info,
    )
    t_extract = (time.time_ns() - t_start) / 1e9  # elapsed time in  seconds

    # --- construct embeddings ----------------------------
    if embedding_size > 0:
        embedding_model = EmbeddingModel.from_embedding_size(embedding_size)
        embeddings = ImageEmbeddings(
            img=construct_embedding_from_image(image_path, embedding_model),
            txt=construct_embedding_from_search_data(search_data, embedding_model),
        )
    else:
        embeddings = None

    # --- construct metadata ------------------------------
    metadata = ImageMetadata(
        filename=str(image_path.parts[-1]),
        model=model,
        t_extract=t_extract,
        search_data=search_data,
        embeddings=embeddings,
    )

    # --- save metadata -----------------------------------
    metadata_path.parent.mkdir(parents=True, exist_ok=True)  # ensure parent directory exists
    with metadata_path.open("w") as metadata_file:
        json_str = metadata.model_dump_json(indent=4)
        metadata_file.write(json_str)


# =================================================================================================
#  Extract DESCRIPTION
# =================================================================================================
def _extract_description(image_path: Path, model: str) -> str:
    """Extract description from an image."""

    # trigger multi-modal LLM
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Describe the image in at least 50 words.  Focus on factual elements and make sure to include all text you see in the image as well.",
                "images": [str(image_path.absolute())],
            }
        ],
    )

    # clean up and return
    description: str = response["message"]["content"]
    description = _clean_description(description)
    return description


def _clean_description(description: str) -> str:
    description = description.replace("\n", " ").strip()
    return description


# =================================================================================================
#  Extract TAGS
# =================================================================================================
def _extract_tags(image_path: Path, model: str) -> list[str]:
    """Extract tags from an image."""

    # trigger multi-modal LLM
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Describe what you see in this image by providing individual single-word tags.  Provide at least 10 tags as a comma-separated list.",
                "images": [str(image_path.absolute())],
            }
        ],
    )

    # clean up and return
    tags_str: str = response["message"]["content"]
    tags_str = tags_str.replace("\n", " ")
    tags_str = tags_str.replace(",", " ")
    tags = [_clean_tag(t) for t in tags_str.split(" ")]  # split and remove trailing/leading whitespace
    tags = [t for t in tags if t]  # remove empty
    tags = sorted(set(tags))  # remove duplicates and sort
    return tags


def _clean_tag(tag: str) -> str:
    """Clean a single tag by stripping leading or trailing special characters and converting to lowercase."""

    # clean up tag
    while True:
        # so we can check if anything changed
        old_tag = tag

        tag = tag.lower()
        for char in [";", ":", ",", "[", "]", "(", ")", "{", "}", "\\", '"', "'"]:
            tag = tag.replace(char, "")  # remove anywhere
        for char in ". ":
            tag = tag.strip(char)  # only remove when leading or trailing

        # stop if nothing changed
        if old_tag == tag:
            break

    # filter out words with little value
    if tag in [
        "a",
        "an",
        "the",
        "and",
        "or",
        "is",
        "are",
        "to",
        "too",
        "of",
        "in",
        "for",
        "on",
        "at",
        "by",
        "with",
        "as",
        "this",
        "that",
        "it",
        "its",
        "be",
        "was",
        "were",
        "not",
    ]:
        tag = ""

    # return cleaned tag
    return tag
