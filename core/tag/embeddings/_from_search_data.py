from core.data import Embedding, EmbeddingModel, SearchData

from ._from_text import construct_embedding_from_text


def construct_embedding_from_search_data(search_data: SearchData, embedding_model: EmbeddingModel) -> Embedding:
    """
    Construct an embedding from a SearchData object using the specified embedding model.

    :param search_data: SearchData object containing the data to be embedded.
    :param embedding_model: EmbeddingModel to use for constructing the embedding.
    :return: An Embedding object containing the embeddings representing the SearchData.
    """

    text = search_data.textual_description()
    return construct_embedding_from_text(text, embedding_model, is_query=False)
