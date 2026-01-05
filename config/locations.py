"""Key locations for distance calculations."""

from dataclasses import dataclass


@dataclass
class Location:
    """A key location for distance calculations."""
    name: str
    address: str
    slug: str  # Used for field names in CSV


# Key locations to calculate distances to
KEY_LOCATIONS = [
    Location(
        name="Bella Vista",
        address="Bella Vista, NSW, Australia",
        slug="bella_vista",
    ),
    Location(
        name="Royal North Shore Hospital",
        address="Reserve Road, St Leonards, NSW 2065, Australia",
        slug="rnsh",
    ),
    Location(
        name="Queen Victoria Building",
        address="455 George St, Sydney NSW 2000, Australia",
        slug="qvb",
    ),
]


def get_location_by_slug(slug: str) -> Location | None:
    """Get a location by its slug."""
    for loc in KEY_LOCATIONS:
        if loc.slug == slug:
            return loc
    return None
