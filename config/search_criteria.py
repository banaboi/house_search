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
        "Chatswood",
        "Chatswood West",
        "Willoughby",
        "Lane Cove",
        "Lane Cove North",
        "Lane Cove West",
        "Greenwich",
        "Gladesville",
        "Hunters Hill",
        "Woolwich",
        "Drummoyne",
        "Artarmon",
        "Lindfield",
        "Killara",
        "Roseville",
        "St Ives",
        "West Ryde",
        "East Ryde",
        "North Ryde",
        "Macquarie Park",
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
    "keywords": "brick",
}
