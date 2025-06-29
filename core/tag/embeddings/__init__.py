"""
Functionality for multi-modal (text & image) embedding generation.

Model Documentation:
  Jina ImageEmbeddings v4:
    - https://jina.ai/models/jina-embeddings-v4
    - https://huggingface.co/jinaai/jina-embeddings-v4
    - https://arxiv.org/pdf/2506.18902
"""

from ._compare import SimilarityMetric, compute_similarity
from ._from_image import construct_embedding_from_image
from ._from_search_data import construct_embedding_from_search_data
from ._from_text import construct_embedding_from_text
