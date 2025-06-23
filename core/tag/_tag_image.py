import json

import ollama
from pathlib import Path
import time
from core.data import ImageMetadata, SearchData


# =================================================================================================
#  Main tagging functionality
# =================================================================================================
def tag_image(image_path: Path, metadata_path: Path, model: str):
    """
    Tag single image and save metadata.  'Tag' is used in a broad sense here, meaning that we extract
    all relevant metadata for future search actions, including, tags, description, and potentially other properties
    in the future.
    :param image_path: Path to the image file to be tagged.
    :param metadata_path: Path to the metadata file where the extracted metadata will be saved.
    :param model: Name of the model to use.
    """

    # --- extract search data -----------------------------
    t_start = time.time_ns()
    search_data = SearchData(
        description=_extract_description(image_path, model),
        tags=_extract_tags(image_path, model),
    )
    t_extract = (time.time_ns() - t_start) / 1e9  # elapsed time in  seconds

    # --- construct metadata ------------------------------
    metadata = ImageMetadata(
        filename=str(image_path.parts[-1]),
        model=model,
        t_extract=t_extract,
        search_data=search_data,
    )

    # --- save metadata -----------------------------------
    metadata_path.parent.mkdir(parents=True, exist_ok=True)  # ensure parent directory exists
    with metadata_path.open("w") as metadata_file:
        json.dump(metadata.model_dump(), metadata_file, indent=4)


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
    description: str = response['message']['content']
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
    tags_str: str = response['message']['content']
    tags_str = tags_str.replace('\n', ' ')
    tags_str = tags_str.replace(',', ' ')
    tags = [_clean_tag(t) for t in tags_str.split(' ')] # split and remove trailing/leading whitespace
    tags = [t for t in tags if t]  # remove empty
    tags = sorted(set(tags))    # remove duplicates and sort
    return tags

def _clean_tag(tag: str) -> str:
    """Clean a single tag by stripping leading or trailing special characters and converting to lowercase."""

    # clean up tag
    while True:
        # so we can check if anything changed
        old_tag = tag

        tag = tag.lower()
        for char in [";", ":", ",", "[", "]", "(", ")", "{", "}", "\\", '"', "'"]:
            tag  = tag.replace(char, "")    # remove anywhere
        for char in ". ":
            tag = tag.strip(char)   # only remove when leading or trailing

        # stop if nothing changed
        if old_tag == tag:
            break

    # filter out words with little value
    if tag in ["a", "an", "the", "and", "or", "is", "are", "to", "too", "of", "in", "for", "on", "at", "by", "with", "as", "this", "that", "it", "its", "be", "was", "were", "not"]:
        tag = ""

    # return cleaned tag
    return tag
