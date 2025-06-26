from pydantic import BaseModel
from abc import ABC, abstractmethod
from datetime import datetime


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
    town: str | None = None
    suburb: str | None = None
    street: str | None = None

    def text_search_string(self) -> str:
        return f"{self.country or ''} {self.state or ''} {self.county or ''} {self.postcode or ''} {self.city or ''} {self.town or ''} {self.suburb or ''} {self.street or ''}".strip()


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

class ImageMetadata(BaseModel):
    """
    Metadata for an image file, containing all context that is relevant for searching + other info.
    """
    filename: str   # filename of the image  (excluding path)
    model: str  # Multi-Modal used to extract search data
    t_extract: float    # time taken to extract search data
    search_data: SearchData # data relevant for searching


