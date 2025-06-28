"""
Functionality for reverse geocoding, i.e., converting GPS coordinates into human-readable addresses or locations.
"""

import reverse_geocode
from geopy.geocoders import Nominatim
from geopy.location import Location

from core.data import LocationInfo


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
        return LocationInfo(lat=lat, lon=lon, country=country, state=state, city=city)
    except Exception:
        # return as LocationInfo with just lat/lon if offline geocoding fails
        return LocationInfo(lat=lat, lon=lon)


def reverse_geocode_online(lat: float, lon: float) -> LocationInfo:
    """
    Resolve GPS coordinates into country, state, and city using Nominatim online reverse geocoding.
    https://geopy.readthedocs.io/en/stable/index.html?highlight=user_agent#nominatim
    https://nominatim.org/release-docs/develop/api/Output/#addressdetails
    """
    try:
        geolocator = Nominatim(user_agent=_get_nominatim_user_agent())
        location: Location = geolocator.reverse(f"{lat:10.5f}, {lon:10.5f}")
        if location:
            address = location.raw.get("address", dict())
            country = get_address_field(address, "country").replace("/", ", ")
            state = get_address_field(address, "state")
            county = get_address_field(address, "county")
            postcode = get_address_field(address, "postcode")
            city = get_address_field(address, ["municipality", "city", "town"])
            village = get_address_field(address, ["village"])
            suburb = get_address_field(
                address,
                ["suburb", "subdivision", "borough", "district", "city_district"],
            )
            hamlet = get_address_field(address, ["hamlet", "croft", "isolated_dwelling"])
            street = get_address_field(address, "road")
            name = get_address_field(
                address,
                [
                    "man_made",
                    "house_name",
                    "amenity",
                    "farm",
                    "tourism",
                    "historic",
                    "military",
                    "natural",
                ],
            )
            return LocationInfo(
                lat=lat,
                lon=lon,
                country=country,
                state=state,
                county=county,
                postcode=postcode,
                city=city,
                village=village,
                suburb=suburb,
                hamlet=hamlet,
                street=street,
                name=name,
            )
        else:
            return LocationInfo(lat=lat, lon=lon)
    except Exception:
        return LocationInfo(lat=lat, lon=lon)  # Fallback to just lat/lon if online geocoding fails


def get_address_field(address: dict, fields: list[str] | str):
    if isinstance(fields, str):
        fields = [fields]
    for field in fields:
        result = address.get(field, "")
        if result:
            return result
    return ""


def _get_nominatim_user_agent() -> str:
    """
    Returns a user agent string for Nominatim.
    This is required by the Nominatim geocoder to identify the application making the request.
    Encapsulated in a function, so we could extend this in the future to add e.g. a user-specific postfix.
    """
    return "image_search_llm_app/1.0"
