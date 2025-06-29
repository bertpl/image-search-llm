from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel

from ._embeddings import ImageEmbeddings


# =================================================================================================
#  SearchableItem
# =================================================================================================
class SearchableItem(ABC):
    """Pydantic base model that also allows us to search it."""

    @abstractmethod
    def text_search_string(self) -> str:
        """Return a string that can be used for keyword searching."""
        raise NotImplementedError()


# =================================================================================================
#  SearchableItem implementations
# =================================================================================================
class TimeInfo(BaseModel, SearchableItem):
    dt: datetime

    def text_search_string(self) -> str:
        """Return a string that can be used for keyword searching, including textual weekday and month."""
        return self.dt.strftime("%A %Y-%m-%d %H:%M:%S %B")


class LocationInfo(BaseModel, SearchableItem):
    lat: float
    lon: float
    country: str | None = None
    state: str | None = None
    county: str | None = None
    postcode: str | None = None
    city: str | None = None
    village: str | None = None
    suburb: str | None = None
    hamlet: str | None = None
    street: str | None = None
    name: str | None = None

    def text_search_string(self) -> str:
        return (
            f"{self.country or ''} {self.state or ''} {self.county or ''} {self.postcode or ''} {self.city or ''} "
            + f"{self.village or ''} {self.suburb or ''} {self.hamlet or ''} {self.street or ''} {self.name or ''}".strip()
        )

    def textual_description(self) -> str:
        """
        Return a textual description of the location.
        Combines all available location information into a single string.
        """
        parts = [
            self.name,
            self.street,
            self.hamlet,
            self.suburb,
            self.postcode,
            self.village,
            self.city,
            self.county,
            self.state,
            self.country,
        ]
        return ", ".join(part for part in parts if part).strip()


# =================================================================================================
#  Where everything comes together
# =================================================================================================
class SearchData(BaseModel, SearchableItem):
    """
    All data extracted from an image that is relevant for searching.
    """

    description: str = ""
    tags: list[str] = []
    time: TimeInfo | None = None
    location: LocationInfo | None = None

    def text_search_string(self) -> str:
        """
        Return a string that can be used for keyword searching.
        Combines description, tags, and location into a single search string.
        """
        s = f"{self.description} {' '.join(self.tags)}"
        if self.time:
            s += f" {self.time.text_search_string()}"
        if self.location:
            s += f" {self.location.text_search_string()}"
        return s

    def textual_description(self) -> str:
        """
        Return a textual description of the search data, including time and location.
        """
        desc = ""

        # first put time & location, since this is info that is not visible in the image itself,
        # so we want to put this information first, to weight more on any embeddings
        if self.time and self.location:
            desc += f"Image taken at {self.location.textual_description()} on {self.time.text_search_string()}.\n"
        elif self.location:
            desc += f"Image taken at {self.location.textual_description()}.\n"
        elif self.time:
            desc += f"Image taken on {self.time.text_search_string()}.\n"

        # then put description & tags
        if self.description:
            desc += f"Image description: {self.description}.\n"
        if self.tags:
            desc += f"\nKeywords: {', '.join(self.tags)}.\n"
        return desc.strip("\n").strip()


class ImageMetadata(BaseModel):
    """
    Metadata for an image file, containing all context that is relevant for searching + other info.
    """

    filename: str  # filename of the image  (excluding path)
    model: str  # Multi-Modal used to extract search data
    t_extract: float  # time taken to extract search data
    search_data: SearchData  # data relevant for searching
    embeddings: ImageEmbeddings | None = None  # embeddings used for similarity search (i.e. semantic search)
