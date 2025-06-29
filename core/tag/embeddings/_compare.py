from enum import StrEnum

import numpy as np

from core.data import Embedding


class SimilarityMetric(StrEnum):
    """
    Enum for similarity metrics.
    """

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"


def compute_similarity(e1: Embedding, e2: Embedding, metric: SimilarityMetric = SimilarityMetric.COSINE) -> float:
    if not are_embeddings_comparable(e1, e2):
        raise ValueError("ImageEmbeddings are not comparable: different models or dimensions.")

    e1_arr = np.array(e1.values)
    e2_arr = np.array(e2.values)
    match metric:
        case SimilarityMetric.COSINE:
            return compute_cosine_similarity(e1_arr, e2_arr)
        case SimilarityMetric.EUCLIDEAN:
            return compute_euclidean_distance(e1_arr, e2_arr)
        case _:
            raise ValueError(f"Unsupported similarity metric: {metric}")


def compute_cosine_similarity(e1: np.ndarray, e2: np.ndarray) -> float:
    e1_norm = e1 / np.linalg.norm(e1)
    e2_norm = e2 / np.linalg.norm(e2)
    return float(np.dot(e1_norm, e2_norm))


def compute_euclidean_distance(e1: np.ndarray, e2: np.ndarray) -> float:
    return float(np.linalg.norm(e1 - e2))


def are_embeddings_comparable(e1: Embedding, e2: Embedding) -> bool:
    """
    Check if two embeddings are comparable based on their model and dimensions.

    Args:
        e1 (Embedding): The first embedding to compare.
        e2 (Embedding): The second embedding to compare.

    Returns:
        bool: True if the embeddings are comparable, False otherwise.
    """
    return (e1.model == e2.model) and (e1.n == e2.n)
