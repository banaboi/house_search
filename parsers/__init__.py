"""Parsers for extracting property listing data from HTML."""

from .base import BaseListingParser
from .domain import DomainListingParser
from .models import PropertyListing, PropertyListingCollection

# Registry of available parsers
PARSERS = {
    "domain": DomainListingParser,
}


def get_parser(site_name: str) -> BaseListingParser:
    """Get a parser instance for the given site."""
    site_name = site_name.lower()
    if site_name not in PARSERS:
        available = ", ".join(PARSERS.keys())
        raise ValueError(f"No parser available for site: {site_name}. Available: {available}")
    return PARSERS[site_name]()


def list_available_parsers() -> list[str]:
    """Return list of sites with available parsers."""
    return list(PARSERS.keys())


__all__ = [
    "BaseListingParser",
    "DomainListingParser",
    "PropertyListing",
    "PropertyListingCollection",
    "get_parser",
    "list_available_parsers",
]
