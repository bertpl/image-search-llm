import sys
from pathlib import Path
from typing import Literal

from tqdm import tqdm

from core.config import SUPPORTED_IMAGE_EXTENSIONS
from core.models import ensure_model_exists

from ._tag_image import tag_image


def tag_all_images(
    images_path: Path,
    model: str,
    geolookup: Literal["off", "offline", "online"],
    embedding_size: int,
    overwrite: bool,
):
    # ensure model exists
    ensure_model_exists(model)

    # collect all image files
    images = []
    for extension in SUPPORTED_IMAGE_EXTENSIONS:
        images += list(images_path.glob(f"*{extension}"))
    images = sorted(images)

    # tag one by one
    for image in tqdm(
        images,
        desc=f"Tagging {len(images):_} image(s)... ",
        file=sys.stdout,
        total=len(images),
    ):
        image_path = Path(image)
        metadata_path = image_path.parent / "metadata" / f"{image_path.parts[-1]}.json"
        if overwrite or not metadata_path.exists():
            tag_image(image_path, metadata_path, model, geolookup, embedding_size)
