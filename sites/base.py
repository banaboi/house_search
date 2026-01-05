"""Base configuration class for property search sites."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SiteConfig(ABC):
    """
    Base configuration for a property search website.
    
    Each site must implement this interface to define:
    - The base URL
    - CSS selectors for all interactive elements
    - URL patterns for result pages
    - Any site-specific behavior
    """
    
    # Site metadata
    name: str = ""
    base_url: str = ""
    
    # URL patterns for detecting page navigation
    search_results_url_pattern: str = ""
    
    # Selectors - these should be overridden by subclasses
    selectors: dict = field(default_factory=dict)
    
    @abstractmethod
    def get_mode_selector(self, mode: str) -> Optional[str]:
        """Get selector for search mode (buy, rent, sold, etc.)."""
        pass
    
    @abstractmethod
    def get_location_input_selector(self) -> str:
        """Get selector for the location search input."""
        pass
    
    @abstractmethod
    def get_filters_button_selector(self) -> str:
        """Get selector for the filters button."""
        pass
    
    @abstractmethod
    def get_search_button_selector(self) -> str:
        """Get selector for the search/submit button in filter modal."""
        pass
    
    @abstractmethod
    def get_property_type_selector(self, property_type: str) -> Optional[str]:
        """Get selector for a property type checkbox."""
        pass
    
    @abstractmethod
    def get_bedroom_selector(self, count: int) -> Optional[str]:
        """Get selector for bedroom count button/radio."""
        pass
    
    @abstractmethod
    def get_bathroom_selector(self, count: int) -> Optional[str]:
        """Get selector for bathroom count button/radio."""
        pass
    
    @abstractmethod
    def get_carpark_selector(self, count: int) -> Optional[str]:
        """Get selector for carpark count button/radio."""
        pass
    
    @abstractmethod
    def get_keywords_input_selector(self) -> Optional[str]:
        """Get selector for keywords input field."""
        pass
    
    # Optional methods with default implementations
    def get_bedrooms_exact_selector(self) -> Optional[str]:
        """Get selector for 'exact bedrooms' checkbox. Return None if not supported."""
        return None
    
    def get_bathrooms_exact_selector(self) -> Optional[str]:
        """Get selector for 'exact bathrooms' checkbox. Return None if not supported."""
        return None
    
    def get_carparks_exact_selector(self) -> Optional[str]:
        """Get selector for 'exact carparks' checkbox. Return None if not supported."""
        return None
    
    def get_new_or_established_button_selector(self) -> Optional[str]:
        """Get selector for new/established dropdown. Return None if not supported."""
        return None
    
    def get_all_property_types_selector(self) -> Optional[str]:
        """Get selector for 'All' property types checkbox."""
        return None
    
    def get_all_property_type_selectors(self) -> dict[str, str]:
        """Get all property type selectors as a dict."""
        return {}
    
    def get_price_slider_min_selector(self) -> Optional[str]:
        """Get selector for minimum price slider handle. Return None if not supported."""
        return None
    
    def get_price_slider_max_selector(self) -> Optional[str]:
        """Get selector for maximum price slider handle. Return None if not supported."""
        return None
    
    def format_new_or_established_option(self, value: str) -> str:
        """Format the new/established option value for selection."""
        return value.capitalize()
    
    def requires_location_enter_key(self) -> bool:
        """Whether pressing Enter is needed to confirm location selection."""
        return True
    
    def get_location_wait_time(self) -> int:
        """Milliseconds to wait after entering location for typeahead."""
        return 800
