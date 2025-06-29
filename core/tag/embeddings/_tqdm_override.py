"""
Ugly hack to make sure transformers tqdm progress bar is never shown.  Otherwise, at every call to encode_image
or encode_text of the JINA embeddings model, a progress bar is shown which unnecessarily clutters the console.
"""

import tqdm

_orig_tqdm = tqdm.tqdm


def my_tqdm(iterable, *args, **kwargs):
    # Override tqdm to do nothing
    if ("Encoding images..." in kwargs.get("desc", "")) or ("Encoding texts..." in kwargs.get("desc", "")):
        return iterable  # no tqdm, just return the iterable as is
    else:
        # For all other cases, return a regular tqdm instance
        return _orig_tqdm(iterable, *args, **kwargs)


tqdm.tqdm = my_tqdm
