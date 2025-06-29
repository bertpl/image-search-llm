import datetime
import json
from pathlib import Path

from core.data import SearchResult


def copy_search_results(image_path: Path, query: str, search_results: list[SearchResult]) -> None:
    """
    Copy all images found in the search result to a dedicated subfolder, together with some metadata.

    :param image_path: (Path) Path to the image files.
    :param query:  (str) Search query used to find the images.
    :param search_results: list of SearchResult objects representing the search results.
    """

    # --- folder prep -------------------------------------
    now = datetime.datetime.now()
    results_path = image_path / ("search_" + now.strftime("%Y%m%d_%H%M%S"))
    results_path.mkdir(parents=True, exist_ok=True)

    # --- determine target file names ---------------------
    # all_files = [(filename, f"{i:0>6}_{filename}", score) for i, result in enumerate(search_results, start=1)]

    # --- copy --------------------------------------------
    metadata = {
        "query": query,
        "timestamp": now.isoformat(),
        "results_count": len(search_results),
        "results": [],
    }

    for i, result in enumerate(search_results, start=1):
        src_filename = result.filename
        dst_filename = f"{i:0>6}_{src_filename}"
        src = image_path / result.filename
        if src.exists():
            dst = results_path / dst_filename
            dst.write_bytes(src.read_bytes())

        metadata["results"].append(
            dict(orig_filename=src_filename, filename=dst_filename, score=result.score, score_src=result.score_src)
        )

    # --- write metadata ----------------------------------
    with (results_path / "metadata.json").open("w") as metadata_file:
        json.dump(metadata, metadata_file, indent=4)
