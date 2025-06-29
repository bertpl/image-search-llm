from pathlib import Path

from core.data import SearchData, SearchResult
from core.tag import read_all_metadata


def textual_search(directory: Path, query: str, use_time_location_data: bool) -> list[SearchResult]:
    """
    Search for images in a directory based on a text query. Text queries are treated as a set of individual words,
    each of which contribute to the importance of a search result. The more occurrences of a word in the image's tags +
    description, will increase the score of the image for that query.

    NOTE: This is pure TEXTUAL search, not SEMANTIC search, i.e. words need to appear literally; relationships between
          related words are not considered.

    :param directory: Path to the directory containing images.
    :param query: Text query to search for (comma or space-separated).
    :param use_time_location_data: When false, extracted time & location data is ignored in the search.
    :return: List of SearchResult objects.
    """

    # read all metadata
    all_metadata = read_all_metadata(directory)

    # search through all metadata files in the directory
    results: list[SearchResult] = []  # (score, filename)-tuples
    for metadata in all_metadata:
        score = _get_score(metadata.search_data, query, use_time_location_data)
        if score > 0:
            results.append(SearchResult(filename=metadata.filename, score=score, score_src="txt"))

    # sort results by score in descending order & alphabetically by filename
    results = sorted(results, key=lambda sr: (-sr.score, sr.filename))

    # return
    return results


def _get_score(search_data: SearchData, query: str, use_time_location_data: bool) -> float:
    """
    Calculate an image score for a give query, starting from the image's SearchData.
    :param search_data: SearchData object containing tags and description.
    :param query: Text query to search for.
    :param use_time_location_data: When false, extracted time & location data is ignored in the search.
    :return: Score as a float.
    """

    # init
    if not use_time_location_data:
        search_data = search_data.model_copy(deep=True)
        search_data.time = None
        search_data.location = None
    text_search_string = search_data.text_search_string().lower()  # concatenated string of all info to be text-searched

    # compute # of occurrences of each word in the query
    score = 0.0
    for word in set(query.lower().split()):
        score += text_search_string.count(word)

    return score
