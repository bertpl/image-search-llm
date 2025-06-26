"""
This is the main file of the image search application.  We provide a CLI using the click library.

Run python image_search.py --help to see the available commands.
"""
from pathlib import Path
from typing import Literal

import click

import core
from core.config import DEFAULT_LLM_MODEL_TEXT_IMAGE


# -------------------------------------------------------------------------
#  CLI entrypoint
# -------------------------------------------------------------------------
@click.group()
def cli():
    """
    Command-line tool for tagging & searching collections of images, using Multi-Modal LLMs.
    """
    pass


# -------------------------------------------------------------------------
#  Individual commands
# -------------------------------------------------------------------------
@cli.command()
def list_models():
    """
    List all available models in the Ollama environment.
    """
    model_names = core.get_model_names()
    print(f"Locally available models:")
    for model in model_names:
        print(f" - {model}")


@cli.command()
@click.option('--directory', required=True, help='Path with images to be tagged.')
@click.option('--model', default=DEFAULT_LLM_MODEL_TEXT_IMAGE ,required=False, help='Model to be used.')
@click.option('--geolookup', type=click.Choice(["off", "offline", "online"]), default="offline" ,required=False, help='Way of resolving GPS coordinates into address/city info.')
@click.option('--overwrite', default=False ,required=False, help='If True, will overwrite previously generated tags.')
def tag(directory: str, model: str, geolookup: Literal["off", "offline", "online"], overwrite: bool):
    """Tag all images in a directory, putting extracted tags/metadata in the metadata subfolder."""
    print(f"Tagging all images in directory '{directory}' using model '{model}'...")
    core.tag_all_images(Path(directory), model, geolookup, overwrite)
    print("Done.")


@cli.command()
@click.option('--directory', required=True, help='Path to the directory containing tagged images.')
def show_stats(directory: str):
    """
    Show statistics about the tagged images in the given directory.
    :param directory: Path to the directory containing tagged images.
    """
    print(f"Showing stats for directory: {directory}")
    core.show_stats(Path(directory))


@cli.command()
@click.option('--directory', required=True, help='Path to the directory containing tagged images.')
@click.option('--n', default=10, help='Number of top tags to display (default: 10).')
def show_tags(directory: str, n: int):
    """
    Show the most common tags in the given directory.
    :param directory: Path to the directory containing images.
    :param n: Number of top tags to display.
    """
    print(f"Showing {n} most common tags in directory: {directory}")
    core.show_tags(Path(directory), n)


@cli.command()
@click.option('--directory', required=True, help='Path to the directory containing tagged images.')
@click.option('--query', required=True, help='Search query (comma- or space-delimited words).')
def textual_search(directory: str, query: str):
    """
    Search for images in a directory based on a text query.  Text queries are treated as a set of individual words,
    each of which contribute to the importance of a search result.  The more occurrences of a word in the image's tags +
    description, will increase the score of the image for that query.
    :param directory: Path to the directory containing images.
    :param query: Text query to search for (comma or space-separated).
    """

    # --- execute search ----------------------------------
    print(f"Searching for '{query}' in directory: {directory}")
    results = core.textual_search(Path(directory), query)

    # --- show results ------------------------------------
    print(f"Found {len(results)} images:")
    max_file_len = max(len(filename) for filename, _ in results) if results else 0
    for filename, score in results:
        filename = filename.ljust(max_file_len + 3)
        print(f"  {filename}  {score}")

    # --- copy results ------------------------------------
    core.copy_search_results(Path(directory), query, results)


# -------------------------------------------------------------------------
#  Python entrypoint
# -------------------------------------------------------------------------
if __name__ == '__main__':
    cli()