"""Base parser class for property listing data extraction."""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

from bs4 import BeautifulSoup

from .models import PropertyListing, PropertyListingCollection

logger = logging.getLogger(__name__)


class BaseListingParser(ABC):
    """
    Base class for parsing property listings from HTML.
    
    Each site should implement a subclass that knows how to extract
    listing data from that site's specific HTML structure.
    """
    
    def __init__(self, source: str = ""):
        """
        Initialize the parser.
        
        Args:
            source: The source site name (e.g., "domain")
        """
        self.source = source
    
    def parse_directory(self, directory: str) -> PropertyListingCollection:
        """
        Parse all HTML chunk files in a directory.
        
        Args:
            directory: Path to directory containing HTML chunk files
            
        Returns:
            PropertyListingCollection with all parsed listings
        """
        collection = PropertyListingCollection(source=self.source)
        
        if not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")
        
        # Get all HTML files sorted by name
        html_files = sorted([
            f for f in os.listdir(directory) 
            if f.endswith('.html')
        ])
        
        if not html_files:
            logger.warning(f"No HTML files found in {directory}")
            return collection
        
        logger.info(f"Found {len(html_files)} HTML files to parse")
        
        # Combine all HTML content for parsing
        combined_html = ""
        for filename in html_files:
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                combined_html += f.read() + "\n"
        
        # Parse the combined HTML
        listings = self.parse_html(combined_html)
        
        for listing in listings:
            collection.add(listing)
        
        logger.info(f"Parsed {len(collection)} unique listings")
        return collection
    
    def parse_html(self, html: str) -> list[PropertyListing]:
        """
        Parse HTML content and extract all listings.
        
        Args:
            html: Raw HTML string
            
        Returns:
            List of PropertyListing objects
        """
        soup = BeautifulSoup(html, 'html.parser')
        return self.extract_listings(soup)
    
    @abstractmethod
    def extract_listings(self, soup: BeautifulSoup) -> list[PropertyListing]:
        """
        Extract all listings from parsed HTML.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            List of PropertyListing objects
        """
        pass
    
    @abstractmethod
    def parse_listing_element(self, element) -> Optional[PropertyListing]:
        """
        Parse a single listing element into a PropertyListing.
        
        Args:
            element: BeautifulSoup element containing a single listing
            
        Returns:
            PropertyListing object or None if parsing fails
        """
        pass
