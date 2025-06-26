"""
Functionality for reverse geocoding, i.e., converting GPS coordinates into human-readable addresses or locations.
"""
import json

from core.data import LocationInfo
import reverse_geocode
from geopy.geocoders import Nominatim
from geopy.location import Location

def reverse_geocode_offline(lat: float, lon: float) -> LocationInfo:
    """
    Resolve GPS coordinates into country, state, and city using offline reverse geocoding.
    """
    try:

        # reverse geocoding using reverse-geocode package, using local built-in dataset
        location_dict = reverse_geocode.get((lat, lon)) or dict()

        # extract fields in robust way
        country = location_dict.get("country", "")
        state = location_dict.get("state", "")
        city = location_dict.get("city", "")

        # return as LocationInfo
        return LocationInfo(
            lat=lat,
            lon=lon,
            country=country,
            state=state,
            city=city
        )
    except Exception as e:
        # return as LocationInfo with just lat/lon if offline geocoding fails
        return LocationInfo(lat=lat, lon=lon)


def reverse_geocode_online(lat: float, lon: float) -> LocationInfo:
    """
    Resolve GPS coordinates into country, state, and city using Nominatim online reverse geocoding.
    https://geopy.readthedocs.io/en/stable/index.html?highlight=user_agent#nominatim
    """
    try:
        geolocator = Nominatim(user_agent=_get_nominatim_user_agent())
        location: Location = geolocator.reverse(f"{lat:10.5f}, {lon:10.5f}")
        if location:
            address = location.raw.get("address",dict())
            country = address.get("country", "")
            state = address.get("state", "")
            county = address.get("county", "")
            postcode = address.get("postcode", "")
            city = address.get("village", "") or address.get("city", "")
            town = address.get("town", "") or address.get("hamlet", "")
            suburb = address.get("suburb", "")
            street = address.get("road", "")
            return LocationInfo(
                lat=lat,
                lon=lon,
                country=country,
                state=state,
                county=county,
                postcode=postcode,
                city=city,
                town=town,
                suburb=suburb,
                street=street,
            )
        else:
            return LocationInfo(lat=lat, lon=lon)
    except Exception as e:
        return LocationInfo(lat=lat, lon=lon)  # Fallback to just lat/lon if online geocoding fails


def _get_nominatim_user_agent() -> str:
    """
    Returns a user agent string for Nominatim.
    This is required by the Nominatim geocoder to identify the application making the request.
    Encapsulated in a function, so we could extend this in the future to add e.g. a user-specific postfix.
    """
    return "image_search_llm_app/1.0"