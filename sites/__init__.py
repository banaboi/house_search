"""Site configurations for different property search websites."""

from .base import SiteConfig
from .domain import DomainConfig

# Registry of available site configurations
SITES = {
    "domain": DomainConfig,
}


def get_site_config(site_name: str) -> SiteConfig:
    """Get a site configuration by name."""
    site_name = site_name.lower()
    if site_name not in SITES:
        available = ", ".join(SITES.keys())
        raise ValueError(f"Unknown site: {site_name}. Available sites: {available}")
    return SITES[site_name]()


def list_available_sites() -> list[str]:
    """Return list of available site names."""
    return list(SITES.keys())


__all__ = [
    "SiteConfig",
    "get_site_config",
    "list_available_sites",
    "DomainConfig",
]
