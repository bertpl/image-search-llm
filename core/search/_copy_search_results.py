from pathlib import Path
import datetime
import json


def copy_search_results(image_path: Path, query: str, search_data: list[tuple[str, float]]) -> None:
    """
    Copy all images found in the search result to a dedicated subfolder, together with some metadata.

    :param image_path: (Path) Path to the image files.
    :param query:  (str) Search query used to find the images.
    :param search_data: list of (filename, score) tuples representing the search results.
    """

    # --- folder prep -------------------------------------
    now = datetime.datetime.now()
    results_path = image_path / ("search_" + now.strftime("%Y%m%d_%H%M%S"))
    results_path.mkdir(parents=True, exist_ok=True)

    # --- copy --------------------------------------------
    for filename, _ in search_data:
        src = image_path / filename
        if src.exists():
            dst = results_path / filename
            dst.write_bytes(src.read_bytes())

    # --- write metadata ----------------------------------
    metadata = {
        "query": query,
        "timestamp": now.isoformat(),
        "results_count": len(search_data),
        "results": [{"filename": filename, "score": score} for filename, score in search_data],
    }
    with (results_path / "metadata.json").open("w") as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

