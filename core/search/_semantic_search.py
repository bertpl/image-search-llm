from pathlib import Path

from core.data import Embedding, EmbeddingModel, ImageEmbeddings, SearchResult
from core.tag import read_all_metadata
from core.tag.embeddings import compute_similarity, construct_embedding_from_text


def semantic_search(directory: Path, query: str, min_score: float) -> list[SearchResult]:
    """
    Search for images in a directory based on a text query.  Search is performed by computing similarity scores
    between embeddings:
      - query (text) embedding
      - image (image) embedding & image metadata (text) embedding
    This will result in 2 similarity scores per image: query-vs-image and query-vs-metadata.  Based on these scores,
    the images are ranked and all results with score >= min_score are returned.

    :param directory: Path to the directory containing images.
    :param query: Text query to search for (comma or space-separated).
    :param min_score: Minimum score to be included as a result.
    :return: List of SearchResult objects that match the query.
    """

    # --- read all metadata -------------------------------
    all_metadata = read_all_metadata(directory)

    # --- compute query embedding -------------------------

    # determine all embedding models used in the metadata
    all_embedding_models = set()
    for metadata in all_metadata:
        if metadata.embeddings is not None:
            all_embedding_models.add(metadata.embeddings.txt.model)
            all_embedding_models.add(metadata.embeddings.img.model)

    # compute embeddings for the query for all encountered models (usually just one)
    query_embeddings_dict = {
        embedding_model: construct_embedding_from_text(query, embedding_model, is_query=True)
        for embedding_model in all_embedding_models
    }

    # check if any embeddings were found
    if not query_embeddings_dict:
        print("No embeddings found in metadata of images in this folder.")
        return []

    # --- compute scores for each image -------------------
    results: list[SearchResult] = []  # (filename, score)-tuples
    for metadata in all_metadata:
        score, score_src = _compute_image_score(
            img_embeddings=metadata.embeddings, query_embeddings=query_embeddings_dict
        )
        if score >= min_score:
            results.append(SearchResult(filename=metadata.filename, score=score, score_src=score_src))

    # --- sort & return -----------------------------------
    results = sorted(results, key=lambda sr: (-sr.score, sr.filename))
    return results


def _compute_image_score(
    img_embeddings: ImageEmbeddings,
    query_embeddings: dict[EmbeddingModel, Embedding],
) -> tuple[float, str]:
    """
    Compute the score for an image based on its embeddings and the query embeddings + returns string indicating which
    embeddings was closest.
    :param img_embeddings: ImageEmbeddings of the image.
    :param query_embeddings: Dictionary of query embeddings keyed by embedding model.
    :return: Overall similarity score.
    """
    img_score = (compute_similarity(img_embeddings.img, query_embeddings[img_embeddings.img.model]), "img")
    txt_score = (compute_similarity(img_embeddings.txt, query_embeddings[img_embeddings.txt.model]), "txt")

    return max(img_score, txt_score)
