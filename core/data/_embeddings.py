"""
Data representation for embeddings, with convenient (de)serialization methods and containing sufficient metadata,
so we know how we obtained the embeddings and to know how to interpret them.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, field_serializer, field_validator


# =================================================================================================
#  Enum
# =================================================================================================
class EmbeddingModel(StrEnum):
    JINA_EMBEDDINGS_V4_128 = "jinaai/jina-embeddings-v4|128"
    JINA_EMBEDDINGS_V4_512 = "jinaai/jina-embeddings-v4|512"
    JINA_EMBEDDINGS_V4_2048 = "jinaai/jina-embeddings-v4|2048"

    @property
    def hugging_face_model_id(self) -> str:
        """
        Returns the Hugging Face model ID for this embedding model.
        """
        return self.value.split("|")[0]

    @property
    def embedding_size(self) -> int:
        """
        Returns the size of the embedding vector for this model.
        """
        return int(self.value.split("|")[1])

    @classmethod
    def from_embedding_size(cls, n: int) -> EmbeddingModel:
        if n == 128:
            return cls.JINA_EMBEDDINGS_V4_128
        elif n == 512:
            return cls.JINA_EMBEDDINGS_V4_512
        elif n == 2048:
            return cls.JINA_EMBEDDINGS_V4_2048
        else:
            raise ValueError(f"Unsupported embedding size: {n}")


# =================================================================================================
#  Embedding / ImageEmbeddings
# =================================================================================================
class ImageEmbeddings(BaseModel):
    """Embeddings for an image + its extracted text, used for similarity search."""

    img: Embedding  # embedding based purely on the image
    txt: Embedding  # embedding based on the text extracted in various ways (i.e. the SearchData object)


class Embedding(BaseModel):
    model: EmbeddingModel
    values: list[float]

    @property
    def n(self) -> int:
        """
        Returns the number of dimensions of the embedding.
        """
        return len(self.values)

    @field_serializer("values")
    def serialize_values(self, value: list[float], _info) -> str:
        """
        Custom serialization for the values field, to avoid long embeddings
        exploding into a huge number of lines when saved as multi-line JSON.
        """
        return ",".join(map(str, value))

    @field_validator("values", mode="before")
    def validate_values(cls, value: list[float] | str) -> list[float]:
        if isinstance(value, str):
            # deserialize from string format
            try:
                return [float(v) for v in value.split(",")]
            except Exception as e:
                raise ValueError(f"Error parsing values string {value}: {e}")
        else:
            return value
