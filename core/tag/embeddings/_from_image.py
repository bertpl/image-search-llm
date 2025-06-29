from pathlib import Path

from core.data import Embedding, EmbeddingModel

from ._hugging_face import get_hugging_face_model


def construct_embedding_from_image(image_path: Path, embedding_model: EmbeddingModel) -> Embedding:
    """
    Constructs an embedding from a given image (path) using the specified embedding model.
    """
    # get model and embedding size
    hf_model = get_hugging_face_model(embedding_model)
    n = embedding_model.embedding_size

    # construct embedding with dimension 'n'
    return Embedding(
        model=embedding_model,
        values=list(hf_model.encode_image(str(image_path.absolute()), truncate_dim=n, task="retrieval")),
    )
