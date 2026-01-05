"""Distance calculation utilities using Google Maps API."""

import json
import logging
import os
import time
from typing import Optional

import googlemaps

from config.locations import KEY_LOCATIONS, Location, TravelMode

logger = logging.getLogger(__name__)

# Cache file for storing distance results
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
DISTANCE_CACHE_FILE = os.path.join(CACHE_DIR, "distance_cache.json")


def _get_api_key() -> Optional[str]:
    """Get the Google Maps API key from config or environment."""
    # First try environment variable
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if api_key:
        return api_key
    
    # Then try config file
    try:
        from config.secrets import GOOGLE_MAPS_API_KEY
        if GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != "YOUR_API_KEY_HERE":
            return GOOGLE_MAPS_API_KEY
    except ImportError:
        pass
    
    return None


class DistanceCalculator:
    """
    Calculate public transport travel times using Google Maps Distance Matrix API.
    
    Caches results to minimize API calls.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the distance calculator.
        
        Args:
            api_key: Google Maps API key. If not provided, will look for
                     GOOGLE_MAPS_API_KEY in config/secrets.py or environment variable.
        """
        self.api_key = api_key or _get_api_key()
        if not self.api_key:
            raise ValueError(
                "Google Maps API key required. Either:\n"
                "  1. Add your key to config/secrets.py, or\n"
                "  2. Set GOOGLE_MAPS_API_KEY environment variable"
            )
        
        self.client = googlemaps.Client(key=self.api_key)
        self.cache = self._load_cache()
        self.locations = KEY_LOCATIONS
    
    def _load_cache(self) -> dict:
        """Load the distance cache from disk."""
        if os.path.exists(DISTANCE_CACHE_FILE):
            try:
                with open(DISTANCE_CACHE_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load distance cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save the distance cache to disk."""
        os.makedirs(CACHE_DIR, exist_ok=True)
        try:
            with open(DISTANCE_CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save distance cache: {e}")
    
    def _get_cache_key(self, origin: str, destination: str, mode: str = "transit") -> str:
        """Generate a cache key for an origin-destination pair."""
        return f"{mode}|{origin.lower().strip()}|{destination.lower().strip()}"
    
    def get_travel_time(
        self, 
        origin: str, 
        destination: str,
        mode: TravelMode = TravelMode.TRANSIT,
        use_cache: bool = True
    ) -> Optional[dict]:
        """
        Get travel time between two addresses using the specified mode.
        
        Args:
            origin: Origin address
            destination: Destination address
            mode: Travel mode (TRANSIT or DRIVING)
            use_cache: Whether to use cached results
            
        Returns:
            Dict with 'duration_mins' or None if failed
        """
        mode_str = mode.value
        cache_key = self._get_cache_key(origin, destination, mode_str)
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            logger.debug(f"Cache hit for {origin} -> {destination} ({mode_str})")
            return self.cache[cache_key]
        
        try:
            # Call Google Maps Distance Matrix API with specified mode
            result = self.client.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode=mode_str,
                units="metric",
            )
            
            # Parse the response
            if result['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                if element['status'] == 'OK':
                    distance_data = {
                        'duration_mins': round(element['duration']['value'] / 60, 0),
                        'mode': mode_str,
                    }
                    
                    # Cache the result
                    self.cache[cache_key] = distance_data
                    self._save_cache()
                    
                    return distance_data
                else:
                    logger.warning(
                        f"Distance calculation failed for {origin} -> {destination}: "
                        f"{element['status']}"
                    )
            else:
                logger.warning(f"Distance Matrix API error: {result['status']}")
                
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
        
        return None

    def get_transit_time(
        self, 
        origin: str, 
        destination: str,
        use_cache: bool = True
    ) -> Optional[dict]:
        """
        Get public transport travel time between two addresses.
        
        Args:
            origin: Origin address
            destination: Destination address
            use_cache: Whether to use cached results
            
        Returns:
            Dict with 'duration_mins' or None if failed
        """
        return self.get_travel_time(origin, destination, TravelMode.TRANSIT, use_cache)
    
    def get_distances_to_key_locations(
        self, 
        property_address: str
    ) -> dict[str, Optional[dict]]:
        """
        Get travel times from a property to all key locations using appropriate mode.
        
        Args:
            property_address: The property address
            
        Returns:
            Dict mapping location slug to travel time data
        """
        distances = {}
        
        for location in self.locations:
            logger.debug(f"Calculating {location.travel_mode.value} time to {location.name}")
            distance_data = self.get_travel_time(
                property_address, 
                location.address,
                location.travel_mode
            )
            distances[location.slug] = distance_data
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return distances
    
    def get_cache_stats(self) -> dict:
        """Get statistics about the cache."""
        return {
            'cached_routes': len(self.cache),
            'cache_file': DISTANCE_CACHE_FILE,
        }
