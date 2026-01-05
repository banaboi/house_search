"""Distance enrichment for property listings."""

import logging
from typing import Optional

from parsers.models import PropertyListing, PropertyListingCollection
from utils.distance import DistanceCalculator

logger = logging.getLogger(__name__)


class DistanceEnricher:
    """
    Enriches property listings with public transport travel times to key locations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the distance enricher.
        
        Args:
            api_key: Google Maps API key. If not provided, will look for
                     GOOGLE_MAPS_API_KEY environment variable.
        """
        self.calculator = DistanceCalculator(api_key=api_key)
    
    def enrich_listing(self, listing: PropertyListing) -> PropertyListing:
        """
        Add public transport travel time information to a single listing.
        
        Args:
            listing: The property listing to enrich
            
        Returns:
            The same listing object with travel time fields populated
        """
        if not listing.full_address:
            logger.warning(f"Skipping listing {listing.listing_id}: no address")
            return listing
        
        logger.info(f"Calculating transit times for: {listing.full_address}")
        
        distances = self.calculator.get_distances_to_key_locations(
            listing.full_address
        )
        
        # Update listing with transit time data
        for slug, distance_data in distances.items():
            if distance_data:
                # Set travel time in minutes
                mins_field = f"distance_{slug}_mins"
                
                if hasattr(listing, mins_field):
                    setattr(listing, mins_field, distance_data['duration_mins'])
        
        return listing
    
    def enrich_collection(
        self, 
        collection: PropertyListingCollection,
        skip_cached: bool = True
    ) -> PropertyListingCollection:
        """
        Add public transport travel time information to all listings in a collection.
        
        Args:
            collection: The collection of listings to enrich
            skip_cached: If True, skip listings that already have travel time data
            
        Returns:
            The same collection with travel time fields populated
        """
        total = len(collection)
        enriched = 0
        skipped = 0
        
        for i, listing in enumerate(collection.listings, 1):
            # Check if already has travel time data
            if skip_cached and listing.distance_bella_vista_mins is not None:
                logger.debug(f"Skipping {listing.listing_id}: already enriched")
                skipped += 1
                continue
            
            logger.info(f"Processing {i}/{total}: {listing.full_address}")
            self.enrich_listing(listing)
            enriched += 1
        
        logger.info(
            f"Enrichment complete: {enriched} enriched, {skipped} skipped"
        )
        
        # Log cache stats
        cache_stats = self.calculator.get_cache_stats()
        logger.info(f"Cache contains {cache_stats['cached_routes']} routes")
        
        return collection
