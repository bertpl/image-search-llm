"""
General functions for extracting EXIF data from images and resolving this into huma-readable text.
"""

from datetime import datetime
from pathlib import Path
from typing import Literal

import reverse_geocode
from exif import Image

from core.data import LocationInfo, TimeInfo

from ._geocode import reverse_geocode_offline, reverse_geocode_online


def extract_time_and_location(
    image_path: Path, geolookup: Literal["off", "offline", "online"]
) -> tuple[TimeInfo | None, LocationInfo | None]:
    """
    Returns the time and location of the image as a tuple of TimeInfo and LocationInfo.
    """
    time_info: TimeInfo | None = None
    location_info: LocationInfo | None = None
    try:
        with open(image_path, "rb") as image_file:
            img = Image(image_file)

        if img.has_exif:
            # Extract datetime
            dt_str = (
                img.get("datetime", None) or img.get("datetime_original", None) or img.get("datetime_digitized", None)
            )
            if dt_str:
                time_info = TimeInfo(dt=datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S"))

            # Extract GPS coordinates & reverse geocode if needed
            lat, lon = get_lon_lat_as_float(img)
            if (lat is not None) and (lon is not None) and (geolookup != "off"):
                if geolookup == "offline":
                    location_info = reverse_geocode_offline(lat, lon)
                else:
                    location_info = reverse_geocode_online(lat, lon)
            else:
                location_info = LocationInfo(lat=lat, lon=lon)

    except Exception:
        pass

    # return the datetime and latitude/longitude as a tuple
    return time_info, location_info


def get_lon_lat_as_float(img: Image) -> tuple[float, float]:
    lat_deg, lat_min, lat_sec = img.get("gps_latitude", None)
    lat_ref = img.get("gps_latitude_ref", "N")
    lon_deg, lon_min, lon_sec = img.get("gps_longitude", None)
    lon_ref = img.get("gps_longitude_ref", "E")

    # convert (degrees, minutes, seconds) to decimal degrees
    lat = lat_deg + (lat_min / 60) + (lat_sec / 3600)
    if lat_ref == "S":
        lat = -lat

    # convert (degrees, minutes, seconds) to decimal degrees
    lon = lon_deg + (lon_min / 60) + (lon_sec / 3600)
    if lon_ref == "W":
        lon = -lon

    return lat, lon


def resolve_coordinates(lat: float, lon: float) -> tuple[str, str, str]:
    location_dict = reverse_geocode.get((lat, lon)) or dict()
    country = location_dict.get("country", "")
    state = location_dict.get("state", "")
    city = location_dict.get("city", "")
    return country, state, city
