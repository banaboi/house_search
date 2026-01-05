"""Key locations for distance calculations."""

from dataclasses import dataclass
from enum import Enum


class TravelMode(Enum):
    """Travel mode for distance calculations."""
    TRANSIT = "transit"
    DRIVING = "driving"


@dataclass
class Location:
    """A key location for distance calculations."""
    name: str
    address: str
    slug: str  # Used for field names in CSV
    travel_mode: TravelMode = TravelMode.TRANSIT  # Default to transit


# Maximum travel times in minutes
MAX_TRANSIT_TIME_MINS = 40
MAX_DRIVING_TIME_MINS = 35


# Transit locations - places we would go to via public transport
TRANSIT_LOCATIONS = [
    Location(
        name="Royal North Shore Hospital",
        address="Reserve Road, St Leonards, NSW 2065, Australia",
        slug="rnsh",
        travel_mode=TravelMode.TRANSIT,
    ),
    Location(
        name="Queen Victoria Building",
        address="455 George St, Sydney NSW 2000, Australia",
        slug="qvb",
        travel_mode=TravelMode.TRANSIT,
    ),
]


# Driving locations - places we would drive to
DRIVING_LOCATIONS = [
    Location(
        name="Bella Vista",
        address="Bella Vista, NSW, Australia",
        slug="bella_vista",
        travel_mode=TravelMode.DRIVING,
    ),
]


# Combined list for backward compatibility
KEY_LOCATIONS = TRANSIT_LOCATIONS + DRIVING_LOCATIONS


def get_location_by_slug(slug: str) -> Location | None:
    """Get a location by its slug."""
    for loc in KEY_LOCATIONS:
        if loc.slug == slug:
            return loc
    return None


def get_transit_locations() -> list[Location]:
    """Get all transit locations."""
    return TRANSIT_LOCATIONS


def get_driving_locations() -> list[Location]:
    """Get all driving locations."""
    return DRIVING_LOCATIONS
