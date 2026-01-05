"""Configuration for Domain.com.au property search."""

from dataclasses import dataclass, field
from typing import Optional

from .base import SiteConfig


@dataclass
class DomainConfig(SiteConfig):
    """Site configuration for domain.com.au."""
    
    name: str = "Domain"
    base_url: str = "https://www.domain.com.au/"
    search_results_url_pattern: str = "**/sale/**"
    
    selectors: dict = field(default_factory=lambda: {
        # Navigation buttons for search mode
        "mode": {
            "buy": '[data-testid="buy-navigation"]',
            "rent": '[data-testid="rent-navigation"]',
            "houseandland": '[data-testid="houseandland-navigation"]',
            "newhomes": '[data-testid="newhomes-navigation"]',
            "sold": '[data-testid="sold-navigation"]',
            "retirement": '[data-testid="retirement-navigation"]',
            "rural": '[data-testid="rural-navigation"]',
        },
        
        # Location input
        "location_input": "#fe-pa-domain-home-typeahead-input",
        
        # Filters button
        "filters_button_desktop": '[data-testid="search-filters-button-desktop"]',
        "filters_button_mobile": '[data-testid="search-filters-button-mobile"]',
        
        # Search buttons
        "search_button": '[data-testid="search-button"]',
        "filter_modal_search_button": 'button[type="submit"][aria-label="Search"]',
        
        # Filter modal close button
        "filter_close_button": '[data-testid="filter-control-close-button"]',
        
        # Property type checkboxes
        "property_types": {
            "all": 'input[name="All"]',
            "house": 'input[name="house"]',
            "apartment": 'input[name="apartment"]',
            "townhouse": 'input[name="town-house"]',
            "land": 'input[name="land"]',
            "retirement": 'input[name="retirements"]',
        },
        
        # Bedrooms selection
        "bedrooms": {
            "any": '[data-testid="bedrooms_0"]',
            "1+": '[data-testid="bedrooms_1"]',
            "2+": '[data-testid="bedrooms_2"]',
            "3+": '[data-testid="bedrooms_3"]',
            "4+": '[data-testid="bedrooms_4"]',
            "5+": '[data-testid="bedrooms_5"]',
        },
        "bedrooms_exact": 'input[name="bedrooms_exact"]',
        
        # Bathrooms selection
        "bathrooms": {
            "any": '[data-testid="Bathrooms_0"]',
            "1+": '[data-testid="Bathrooms_1"]',
            "2+": '[data-testid="Bathrooms_2"]',
            "3+": '[data-testid="Bathrooms_3"]',
            "4+": '[data-testid="Bathrooms_4"]',
            "5+": '[data-testid="Bathrooms_5"]',
        },
        "bathrooms_exact": 'input[name="Bathrooms_exact"]',
        
        # Carparks selection
        "carparks": {
            "any": '[data-testid="Carparks_0"]',
            "1+": '[data-testid="Carparks_1"]',
            "2+": '[data-testid="Carparks_2"]',
            "3+": '[data-testid="Carparks_3"]',
            "4+": '[data-testid="Carparks_4"]',
            "5+": '[data-testid="Carparks_5"]',
        },
        "carparks_exact": 'input[name="Carparks_exact"]',
        
        # New or established dropdown
        "new_or_established_button": "#search-filters-new-or-established-toggle-button",
        
        # Keywords input
        "keywords_input": 'input[name="keywords"]',
        
        # Other checkboxes
        "surrounding_suburbs": 'input[name="surrounding-suburbs"]',
        "exclude_under_offer": 'input[name="excludeUnderOffer"]',
        
        # Price slider handles
        "price_slider_min": '[data-testid="dynamic-search-filters__range-handle"][data-handle-key="0"]',
        "price_slider_max": '[data-testid="dynamic-search-filters__range-handle"][data-handle-key="1"]',
    })
    
    def get_mode_selector(self, mode: str) -> Optional[str]:
        return self.selectors["mode"].get(mode)
    
    def get_location_input_selector(self) -> str:
        return self.selectors["location_input"]
    
    def get_filters_button_selector(self) -> str:
        return self.selectors["filters_button_desktop"]
    
    def get_search_button_selector(self) -> str:
        return self.selectors["filter_modal_search_button"]
    
    def get_property_type_selector(self, property_type: str) -> Optional[str]:
        return self.selectors["property_types"].get(property_type)
    
    def get_bedroom_selector(self, count: int) -> Optional[str]:
        return self.selectors["bedrooms"].get(f"{count}+")
    
    def get_bathroom_selector(self, count: int) -> Optional[str]:
        return self.selectors["bathrooms"].get(f"{count}+")
    
    def get_carpark_selector(self, count: int) -> Optional[str]:
        return self.selectors["carparks"].get(f"{count}+")
    
    def get_keywords_input_selector(self) -> Optional[str]:
        return self.selectors["keywords_input"]
    
    def get_bedrooms_exact_selector(self) -> Optional[str]:
        return self.selectors["bedrooms_exact"]
    
    def get_bathrooms_exact_selector(self) -> Optional[str]:
        return self.selectors["bathrooms_exact"]
    
    def get_carparks_exact_selector(self) -> Optional[str]:
        return self.selectors["carparks_exact"]
    
    def get_new_or_established_button_selector(self) -> Optional[str]:
        return self.selectors["new_or_established_button"]
    
    def get_all_property_types_selector(self) -> Optional[str]:
        return self.selectors["property_types"].get("all")
    
    def get_all_property_type_selectors(self) -> dict[str, str]:
        return self.selectors["property_types"]
    
    def get_price_slider_min_selector(self) -> str:
        """Get selector for the minimum price slider handle."""
        return self.selectors["price_slider_min"]
    
    def get_price_slider_max_selector(self) -> str:
        """Get selector for the maximum price slider handle."""
        return self.selectors["price_slider_max"]
