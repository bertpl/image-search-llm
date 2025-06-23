from pydantic import BaseModel


class SearchData(BaseModel):
    """
    All data extracted from an image that is relevant for searching.
    """
    description: str = ""
    tags: list[str] = []


class ImageMetadata(BaseModel):
    """
    Metadata for an image file, containing all context that is relevant for searching + other info.
    """
    filename: str   # filename of the image  (excluding path)
    model: str  # Multi-Modal used to extract search data
    t_extract: float    # time taken to extract search data
    search_data: SearchData # data relevant for searching


