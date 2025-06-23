from collections import defaultdict
from pathlib import Path
from ._read_all_metadata import read_all_metadata


def show_tags(image_directory: Path, n: int = 10):

    # read all metadata
    all_metadata = read_all_metadata(image_directory)

    # count tags
    tag_count = defaultdict(int)
    for metadata in all_metadata:
        for tag in metadata.search_data.tags:
            tag_count[tag] += 1

    # sort tags & show
    sorted_tags = sorted(tag_count.items(), key=lambda x: (-x[1], x[0]))
    sorted_tags = sorted_tags[:n]
    if sorted_tags:
        max_tag_len = max(len(tag) for tag, _ in sorted_tags)
        for i, (tag, count) in enumerate(sorted_tags, start=1):
            tag = tag.ljust(min(10, max_tag_len))
            print(f" {i:>3}. {tag}   {count:>3} image(s)")
    else:
        print("No tags found.")
