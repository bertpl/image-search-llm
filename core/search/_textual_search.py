from pathlib import Path

from core.data import SearchData
from core.tag import read_all_metadata


def textual_search(directory: Path, query: str) -> list[tuple[str, float]]:
    """
    Search for images in a directory based on a text query. Text queries are treated as a set of individual words,
    each of which contribute to the importance of a search result. The more occurrences of a word in the image's tags +
    description, will increase the score of the image for that query.

    NOTE: This is pure TEXTUAL search, not SEMANTIC search, i.e. words need to appear literally; relationships between
          related words are not considered.

    :param directory: Path to the directory containing images.
    :param query: Text query to search for (comma or space-separated).
    :return: List of image paths that match the query.
    """

    # read all metadata
    all_metadata = read_all_metadata(directory)

    # search through all metadata files in the directory
    results: list[tuple[float, str]] = []
    for metadata in all_metadata:
        score = _get_score(metadata.search_data, query)
        if score > 0:
            results.append((score, metadata.filename))

    # sort results by score in descending order & alphabetically by filename
    results = sorted(results, key=lambda x: (-x[0], x[1]))

    # return
    return [(filename, score) for score, filename in results]


def _get_score(search_data: SearchData, query: str) -> float:
    """
    Calculate an image score for a give query, starting from the image's SearchData.
    :param search_data: SearchData object containing tags and description.
    :param query: Text query to search for.
    :return: Score as a float.
    """

    # init
    score = 0.0
    for word in set(query.lower().split()):
        score += search_data.tags.count(word) + search_data.description.lower().count(word)

    return score




