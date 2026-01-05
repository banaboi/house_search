"""Domain.com.au listing parser."""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from .base import BaseListingParser
from .models import PropertyListing

logger = logging.getLogger(__name__)


class DomainListingParser(BaseListingParser):
    """Parser for Domain.com.au property listings."""
    
    def __init__(self):
        super().__init__(source="domain")
    
    def extract_listings(self, soup: BeautifulSoup) -> list[PropertyListing]:
        """
        Extract all listings from Domain search results HTML.
        
        Domain listings are contained in <li> elements with data-testid="listing-{ID}"
        """
        listings = []
        seen_ids = set()  # Track seen listing IDs to avoid duplicates
        
        # Find all listing elements by data-testid pattern
        # Pattern: data-testid="listing-{numeric_id}"
        listing_elements = soup.find_all(
            'li', 
            attrs={'data-testid': re.compile(r'^listing-\d+$')}
        )
        
        logger.debug(f"Found {len(listing_elements)} listing elements")
        
        for element in listing_elements:
            listing = self.parse_listing_element(element)
            if listing and listing.listing_id not in seen_ids:
                seen_ids.add(listing.listing_id)
                listings.append(listing)
        
        # Also try to find listings from fragmented HTML chunks
        # by looking for address wrappers and reconstructing data
        if not listings:
            listings = self._extract_from_fragments(soup, seen_ids)
        
        return listings
    
    def _extract_from_fragments(
        self, soup: BeautifulSoup, seen_ids: set
    ) -> list[PropertyListing]:
        """
        Extract listings from fragmented HTML where full listing elements
        may be split across chunks.
        """
        listings = []
        
        # Find all address wrappers as anchor points
        address_wrappers = soup.find_all(
            attrs={'data-testid': 'address-wrapper'}
        )
        
        for addr_wrapper in address_wrappers:
            listing = self._extract_listing_from_address(addr_wrapper, soup)
            if listing and listing.listing_id and listing.listing_id not in seen_ids:
                seen_ids.add(listing.listing_id)
                listings.append(listing)
            elif listing and not listing.listing_id:
                # Generate a pseudo-ID from address for deduplication
                pseudo_id = f"{listing.address_line1}_{listing.address_line2}".replace(' ', '_')
                if pseudo_id not in seen_ids:
                    seen_ids.add(pseudo_id)
                    listings.append(listing)
        
        return listings
    
    def _extract_listing_from_address(
        self, addr_wrapper: Tag, soup: BeautifulSoup
    ) -> Optional[PropertyListing]:
        """Extract listing data starting from an address wrapper element."""
        listing = PropertyListing()
        
        # Extract address
        addr_line1 = addr_wrapper.find(attrs={'data-testid': 'address-line1'})
        addr_line2 = addr_wrapper.find(attrs={'data-testid': 'address-line2'})
        
        if addr_line1:
            listing.address_line1 = addr_line1.get_text(strip=True)
        if addr_line2:
            listing.address_line2 = addr_line2.get_text(strip=True)
        
        listing.full_address = f"{listing.address_line1} {listing.address_line2}".strip()
        
        # Try to find the parent link which contains the URL and listing ID
        parent_link = addr_wrapper.find_parent('a')
        if parent_link and parent_link.get('href'):
            listing.url = str(parent_link['href'])
            if not listing.url.startswith('http'):
                listing.url = f"https://www.domain.com.au{listing.url}"
            
            # Extract listing ID from URL
            match = re.search(r'-(\d+)$', listing.url)
            if match:
                listing.listing_id = match.group(1)
        
        return listing if listing.full_address else None
    
    def parse_listing_element(self, element: Tag) -> Optional[PropertyListing]:
        """
        Parse a single listing <li> element into a PropertyListing.
        """
        try:
            listing = PropertyListing()
            
            # Extract listing ID from data-testid
            testid = str(element.get('data-testid', ''))
            match = re.match(r'listing-(\d+)', testid)
            if match:
                listing.listing_id = match.group(1)
            
            # Extract URL from listing link
            listing.url = self._extract_url(element)
            
            # Extract address
            self._extract_address(element, listing)
            
            # Extract price
            self._extract_price(element, listing)
            
            # Extract features (beds, baths, parking)
            self._extract_features(element, listing)
            
            # Extract property type
            self._extract_property_type(element, listing)
            
            # Extract images
            self._extract_images(element, listing)
            
            # Extract agent/agency info
            self._extract_agent_info(element, listing)
            
            # Extract inspection time
            self._extract_inspection(element, listing)
            
            # Extract status (sold, etc.)
            self._extract_status(element, listing)
            
            return listing
            
        except Exception as e:
            logger.warning(f"Failed to parse listing element: {e}")
            return None
    
    def _extract_url(self, element: Tag) -> str:
        """Extract the listing URL."""
        # Find the first link to the property detail page
        link = element.find('a', href=re.compile(r'/[\w-]+-\d+$'))
        if link and link.get('href'):
            url = str(link['href'])
            if not url.startswith('http'):
                url = f"https://www.domain.com.au{url}"
            return url
        return ""
    
    def _extract_address(self, element: Tag, listing: PropertyListing) -> None:
        """Extract address from listing element."""
        # Try address wrapper first
        addr_wrapper = element.find(attrs={'data-testid': 'address-wrapper'})
        if addr_wrapper:
            addr_line1 = addr_wrapper.find(attrs={'data-testid': 'address-line1'})
            addr_line2 = addr_wrapper.find(attrs={'data-testid': 'address-line2'})
            
            if addr_line1:
                listing.address_line1 = addr_line1.get_text(strip=True)
            if addr_line2:
                listing.address_line2 = addr_line2.get_text(strip=True)
        
        # Fallback: try to extract from image alt text
        if not listing.address_line1:
            img = element.find('img', alt=re.compile(r'^Picture of'))
            if img:
                alt = str(img.get('alt', ''))
                match = re.match(r'Picture of (.+)', alt)
                if match:
                    listing.full_address = match.group(1)
                    # Try to split into line1 and line2
                    parts = listing.full_address.rsplit(',', 1)
                    if len(parts) == 2:
                        listing.address_line1 = parts[0].strip() + ','
                        listing.address_line2 = parts[1].strip()
        
        # Build full address if not already set
        if not listing.full_address and (listing.address_line1 or listing.address_line2):
            listing.full_address = f"{listing.address_line1} {listing.address_line2}".strip()
    
    def _extract_price(self, element: Tag, listing: PropertyListing) -> None:
        """Extract price from listing element."""
        price_elem = element.find(attrs={'data-testid': 'listing-card-price'})
        if price_elem:
            listing.price = price_elem.get_text(strip=True)
    
    def _extract_features(self, element: Tag, listing: PropertyListing) -> None:
        """Extract bedrooms, bathrooms, and parking from listing element."""
        features_wrapper = element.find(attrs={'data-testid': 'property-features-wrapper'})
        if not features_wrapper:
            return
        
        features = features_wrapper.find_all(attrs={'data-testid': 'property-features-feature'})
        
        for feature in features:
            text_container = feature.find(attrs={'data-testid': 'property-features-text-container'})
            feature_label = feature.find(attrs={'data-testid': 'property-features-text'})
            
            if not text_container or not feature_label:
                continue
            
            # Get the full text and extract the number
            full_text = text_container.get_text(strip=True)
            label = feature_label.get_text(strip=True).lower()
            
            # Extract number from text like "2 Beds"
            match = re.match(r'(\d+)', full_text)
            if match:
                count = int(match.group(1))
                
                if 'bed' in label:
                    listing.bedrooms = count
                elif 'bath' in label:
                    listing.bathrooms = count
                elif 'parking' in label or 'car' in label:
                    listing.parking = count
    
    def _extract_property_type(self, element: Tag, listing: PropertyListing) -> None:
        """Extract property type from listing element."""
        # Property type is usually in a span with class css-20sx0y
        # containing text like "Apartment / Unit / Flat"
        type_elem = element.find('span', class_='css-20sx0y')
        if type_elem:
            listing.property_type = type_elem.get_text(strip=True)
    
    def _extract_images(self, element: Tag, listing: PropertyListing) -> None:
        """Extract image URLs from listing element."""
        image_containers = element.find_all(attrs={'data-testid': 'listing-card-lazy-image'})
        
        seen_urls = set()
        for container in image_containers:
            img = container.find('img')
            if img and img.get('src'):
                src = str(img['src'])
                # Filter out agent/agency logos
                if 'Agencys' not in src and 'contact_' not in src:
                    if src not in seen_urls:
                        seen_urls.add(src)
                        listing.image_urls.append(src)
        
        # Set the primary image
        if listing.image_urls:
            listing.image_url = listing.image_urls[0]
    
    def _extract_agent_info(self, element: Tag, listing: PropertyListing) -> None:
        """Extract agent and agency information."""
        branding = element.find(attrs={'data-testid': 'listing-card-branding'})
        if not branding:
            return
        
        # Agent name - usually in a span with class css-1xyru6o
        agent_spans = branding.find_all('span', class_='css-1xyru6o')
        if agent_spans:
            if len(agent_spans) >= 1:
                listing.agent_name = agent_spans[0].get_text(strip=True)
            if len(agent_spans) >= 2:
                listing.agency_name = agent_spans[1].get_text(strip=True)
        
        # Agency logo
        logo_img = branding.find('img', alt=re.compile(r'^Logo for'))
        if logo_img:
            listing.agency_logo_url = str(logo_img.get('src', ''))
    
    def _extract_inspection(self, element: Tag, listing: PropertyListing) -> None:
        """Extract inspection time from listing element."""
        # Inspection info is in a div with class css-thvxpe
        inspection_div = element.find('div', class_='css-thvxpe')
        if inspection_div:
            # Get all spans - first is label, second is time
            spans = inspection_div.find_all('span')
            if len(spans) >= 2:
                listing.inspection_time = spans[1].get_text(strip=True)
    
    def _extract_status(self, element: Tag, listing: PropertyListing) -> None:
        """Extract listing status (e.g., Sold)."""
        tag_elem = element.find(attrs={'data-testid': 'listing-card-tag'})
        if tag_elem:
            listing.status = tag_elem.get_text(strip=True)
        elif listing.price:
            # Infer status from price text
            price_lower = listing.price.lower()
            if 'sold' in price_lower:
                listing.status = 'Sold'
            elif 'for sale' in price_lower or 'contact' in price_lower:
                listing.status = 'For Sale'
