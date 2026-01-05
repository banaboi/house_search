"""Data models for property listings."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import csv
import os


@dataclass
class PropertyListing:
    """Represents a single property listing."""
    
    # Core identification
    listing_id: str = ""
    url: str = ""
    
    # Address
    address_line1: str = ""
    address_line2: str = ""  # Usually suburb
    full_address: str = ""
    
    # Price
    price: str = ""
    
    # Features
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking: Optional[int] = None
    
    # Property details
    property_type: str = ""
    
    # Images
    image_url: str = ""
    image_urls: list[str] = field(default_factory=list)
    
    # Agent/Agency
    agent_name: str = ""
    agency_name: str = ""
    agency_logo_url: str = ""
    
    # Inspection
    inspection_time: str = ""
    
    # Status
    status: str = ""  # e.g., "Sold", "For Sale", etc.
    
    # Transit time to key locations (in minutes via public transport)
    distance_bella_vista_mins: Optional[float] = None
    distance_rnsh_mins: Optional[float] = None
    distance_qvb_mins: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary, handling list fields."""
        data = asdict(self)
        # Convert image_urls list to comma-separated string for CSV
        data['image_urls'] = ';'.join(self.image_urls) if self.image_urls else ''
        return data


@dataclass
class PropertyListingCollection:
    """A collection of property listings with export capabilities."""
    
    listings: list[PropertyListing] = field(default_factory=list)
    source: str = ""  # e.g., "domain"
    
    def add(self, listing: PropertyListing) -> None:
        """Add a listing to the collection."""
        self.listings.append(listing)
    
    def __len__(self) -> int:
        return len(self.listings)
    
    def __iter__(self):
        return iter(self.listings)
    
    def to_csv(self, filepath: str) -> str:
        """
        Export listings to a CSV file.
        
        Args:
            filepath: Path to the output CSV file
            
        Returns:
            The absolute path to the saved file
        """
        if not self.listings:
            raise ValueError("No listings to export")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        # Get field names from the first listing
        fieldnames = list(self.listings[0].to_dict().keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for listing in self.listings:
                writer.writerow(listing.to_dict())
        
        return os.path.abspath(filepath)
    
    def get_unique_suburbs(self) -> list[str]:
        """Get list of unique suburbs from listings."""
        suburbs = set()
        for listing in self.listings:
            if listing.address_line2:
                suburbs.add(listing.address_line2.strip())
        return sorted(suburbs)
    
    def filter_by_suburb(self, suburb: str) -> 'PropertyListingCollection':
        """Return a new collection filtered by suburb."""
        filtered = PropertyListingCollection(source=self.source)
        for listing in self.listings:
            if listing.address_line2 and suburb.lower() in listing.address_line2.lower():
                filtered.add(listing)
        return filtered

    def to_html(self, filepath: str) -> str:
        """
        Export listings to an HTML file.
        
        Args:
            filepath: Path to the output HTML file
            
        Returns:
            The absolute path to the saved file
        """
        from output.html_generator import generate_html
        return generate_html(self, filepath)
