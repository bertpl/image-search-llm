import os
from functools import lru_cache

import torch
from transformers import AutoConfig, AutoModel
from transformers.utils.logging import disable_progress_bar, set_verbosity_error

from core.data import EmbeddingModel

from ._tqdm_override import *


def get_hugging_face_model(embedding_model: EmbeddingModel):
    # reduce console clutter upon first load
    set_verbosity_error()
    disable_progress_bar()
    os.environ["TRANSFORMERS_NO_TQDM"] = "1"

    # return appropriate model
    match embedding_model.hugging_face_model_id:
        case "jinaai/jina-embeddings-v4":
            return get_jina_embeddings_v4_model()
        case _:
            raise ValueError(f"Unsupported Hugging Face model ID: {embedding_model.hugging_face_model_id}")


@lru_cache(maxsize=1)
def get_jina_embeddings_v4_model():
    model_id = "jinaai/jina-embeddings-v4"
    if torch.cuda.is_available():
        # CUDA available, we can use flash attention
        model = AutoModel.from_pretrained(
            model_id,
            trust_remote_code=True,
        )
        model.to("cuda")
        return model
    else:
        # CUDA not available, we can't use flash attention,
        # so we fall back to SDPA (scaled dot product attention), which we need to configure
        # in two different places to avoid errors.
        config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
        config._attn_implementation = "sdpa"
        config.text_config._attn_implementation = "sdpa"
        model = AutoModel.from_pretrained(
            model_id,
            trust_remote_code=True,
            config=config,
        )
        model.to("mps" if torch.backends.mps.is_available() else "cpu")
        return model
