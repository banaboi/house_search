"""
Search criteria configuration for property search.

This file contains ONLY the search criteria (what you're looking for).
Site-specific selectors are defined in the sites/ module.
"""

SEARCH_CRITERIA = {
    # Property features
    "bedrooms": 2,
    "bathrooms": 1,
    "carports": 1,
    
    # Locations to search
    "locations": [
        "North Shore - Lower"
    ],
    
    # Property type (house, apartment, townhouse, land, retirement)
    "property_type": "apartment",
    "new_or_established": "established",  # established, new, or any
    
    # Price range
    "price_min": 0,
    "price_max": 1000000,
    
    # Search mode
    "mode": "buy",  # buy, rent, sold, etc.

    # Additional features (optional)
    # "keywords": "brick",
    
    # Output settings
    "save_html_chunks": True,  # Set to True to save HTML chunks to disk
}
