from pathlib import Path
from ._read_all_metadata import read_all_metadata
from dataclasses import dataclass


def show_stats(image_directory: Path):

    # read all metadata
    all_metadata = read_all_metadata(image_directory)

    # extract stats
    n_files = len(all_metadata)
    models = sorted({metadata.model for metadata in all_metadata})
    n_unique_tags = len({tag for metadata in all_metadata for tag in metadata.search_data.tags})
    n_tags_per_img = sum(len(metadata.search_data.tags) for metadata in all_metadata) / n_files if n_files > 0 else 0
    n_desc_chars_per_img = sum(len(metadata.search_data.description) for metadata in all_metadata) / n_files if n_files > 0 else 0
    t_extract = sum(metadata.t_extract for metadata in all_metadata) / n_files if n_files > 0 else 0

    # show stats
    print(f"  files          : {n_files:_}")
    if n_files:
        print(f"  model(s)       : {', '.join(models) if models else 'NA'}")
        print(f"  descriptions   : {n_desc_chars_per_img:7.2f} chars/img")
        print(f"  tags           : {n_tags_per_img:7.2f}  tags/img    [{n_unique_tags:_} unique]")
        print(f"  extraction     : {t_extract:7.2f}   sec/img")
