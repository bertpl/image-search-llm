from core.data import Embedding, EmbeddingModel

from ._hugging_face import get_hugging_face_model


def construct_embedding_from_text(text: str, embedding_model: EmbeddingModel, is_query: bool) -> Embedding:
    """
    Constructs an embedding from a given text using the specified embedding model.
    """

    # get model and embedding size
    hf_model = get_hugging_face_model(embedding_model)
    n = embedding_model.embedding_size

    # construct embedding with dimension 'n'
    return Embedding(
        model=embedding_model,
        values=list(
            hf_model.encode_text(
                text,
                truncate_dim=n,
                task="retrieval",
                prompt_name="query" if is_query else "passage",
            )
        ),
    )
