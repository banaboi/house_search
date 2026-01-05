"""
Property Search Engine

Core business logic for performing property searches across different sites.
This module is site-agnostic and uses SiteConfig for site-specific selectors.
"""

import logging
import os
from typing import Optional

from sites.base import SiteConfig
from utils import BrowserSession, extract_and_save

logger = logging.getLogger(__name__)


class PropertySearchEngine:
    """
    Site-agnostic property search engine.
    
    Uses a SiteConfig to get the appropriate selectors and URLs
    for the target property search website.
    """
    
    def __init__(self, site_config: SiteConfig, search_criteria: dict):
        self.config = site_config
        self.criteria = search_criteria
        self.session: Optional[BrowserSession] = None
    
    def grab_homepage_html(self, output_dir: str = "output/home"):
        """Grab the homepage HTML and save chunks."""
        with BrowserSession(headless=True) as session:
            session.goto(self.config.base_url)
            html = session.get_html()
            save_chunks = self.criteria.get("save_html_chunks", False)
            files = extract_and_save(html, output_dir, prefix="chunk", save_to_disk=save_chunks)
            if save_chunks:
                logger.info(f"Saved {len(files)} chunks to {output_dir}")
    
    def grab_filters_html(self, output_dir: str = "output/filters"):
        """Open the filters modal and grab HTML."""
        with BrowserSession(headless=False) as session:
            session.goto(self.config.base_url)
            
            # Click mode (Buy/Rent) first
            mode = self.criteria.get("mode", "buy")
            mode_selector = self.config.get_mode_selector(mode)
            if mode_selector:
                session.click(mode_selector)
            
            # Click the filters button to open modal
            logger.info("Opening filters modal")
            filters_btn = self.config.get_filters_button_selector()
            session.click(filters_btn, wait_after=1000)
            
            # Wait for modal to fully load
            session.page.wait_for_timeout(2000)
            
            # Grab the HTML with the modal open
            html = session.get_html()
            save_chunks = self.criteria.get("save_html_chunks", False)
            files = extract_and_save(html, output_dir, prefix="filter_chunk", save_to_disk=save_chunks)
            if save_chunks:
                logger.info(f"Saved {len(files)} chunks to {output_dir}")
            
            # Also take a screenshot of the modal
            os.makedirs(os.path.dirname(output_dir) or ".", exist_ok=True)
            session.screenshot(f"{output_dir}_modal.png")
    
    def perform_search(self, output_dir: str = "output/search"):
        """Perform a property search based on search criteria."""
        with BrowserSession(headless=False) as session:
            self.session = session
            session.goto(self.config.base_url)
            
            # 1. Select search mode (Buy/Rent/etc.)
            self._select_mode()
            
            # 2. Enter locations
            self._enter_locations()
            
            # 3. Open filters modal
            self._open_filters()
            
            # 4. Apply all filters
            self._apply_property_type_filter()
            self._apply_bedroom_filter()
            self._apply_bathroom_filter()
            self._apply_carpark_filter()
            self._apply_price_filter()
            self._apply_new_or_established_filter()
            self._apply_keywords_filter()
            
            # 5. Submit search
            self._submit_search()
            
            # 6. Wait for results and save
            self._wait_for_results()
            self._save_results(output_dir)
            
            # Keep browser open briefly
            session.page.wait_for_timeout(5000)
    
    def _select_mode(self):
        """Select the search mode (buy, rent, etc.)."""
        mode = self.criteria.get("mode", "buy")
        mode_selector = self.config.get_mode_selector(mode)
        if mode_selector:
            logger.info(f"Clicking '{mode}' button")
            self.session.click(mode_selector)
    
    def _enter_locations(self):
        """Enter all search locations."""
        locations = self.criteria.get("locations", [])
        if not locations:
            return
        
        location_input = self.config.get_location_input_selector()
        wait_time = self.config.get_location_wait_time()
        
        for location in locations:
            logger.info(f"Adding location: {location}")
            
            self.session.click(location_input)
            self.session.fill(location_input, location, wait_after=wait_time)
            
            # Select first suggestion from typeahead
            if self.config.requires_location_enter_key():
                self.session.press_key("Enter")
            
            # Brief wait before adding next location
            self.session.page.wait_for_timeout(300)
        
        logger.info(f"Added {len(locations)} locations")
    
    def _open_filters(self):
        """Open the filters modal."""
        logger.info("Opening filters modal")
        filters_btn = self.config.get_filters_button_selector()
        self.session.click(filters_btn, wait_after=1500)
    
    def _apply_property_type_filter(self):
        """Apply property type filter."""
        property_type = self.criteria.get("property_type")
        if not property_type or property_type == "all":
            return
        
        all_checkbox_selector = self.config.get_all_property_types_selector()
        
        if all_checkbox_selector:
            # Check if "All" is currently checked
            all_is_checked = self.session.page.locator(all_checkbox_selector).is_checked()
            
            if all_is_checked:
                logger.info("Unchecking 'All' property types")
                self.session.click(all_checkbox_selector, wait_after=500)
        
        # Uncheck any property types that might be checked (except our target)
        all_types = self.config.get_all_property_type_selectors()
        for ptype, selector in all_types.items():
            if ptype == "all":
                continue
            try:
                checkbox = self.session.page.locator(selector)
                if checkbox.is_checked() and ptype != property_type:
                    logger.info(f"Unchecking property type: {ptype}")
                    self.session.click(selector, wait_after=200)
            except Exception as e:
                logger.debug(f"Could not check state of {ptype}: {e}")
        
        # Now check our desired property type
        type_selector = self.config.get_property_type_selector(property_type)
        if type_selector:
            checkbox = self.session.page.locator(type_selector)
            if not checkbox.is_checked():
                logger.info(f"Selecting property type: {property_type}")
                self.session.click(type_selector, wait_after=300)
    
    def _apply_bedroom_filter(self):
        """Apply bedroom filter."""
        bedrooms = self.criteria.get("bedrooms")
        if not bedrooms:
            return
        
        bedroom_selector = self.config.get_bedroom_selector(bedrooms)
        if bedroom_selector:
            logger.info(f"Selecting {bedrooms}+ bedrooms")
            self.session.click(bedroom_selector, wait_after=300)
        exact_selector = self.config.get_bedrooms_exact_selector()
        if exact_selector:
            logger.info(f"Selecting exact bedrooms option")
            self.session.click(exact_selector, wait_after=300)
    
    def _apply_bathroom_filter(self):
        """Apply bathroom filter."""
        bathrooms = self.criteria.get("bathrooms")
        if not bathrooms:
            return
        
        bathroom_selector = self.config.get_bathroom_selector(bathrooms)
        if bathroom_selector:
            logger.info(f"Selecting {bathrooms}+ bathrooms")
            self.session.click(bathroom_selector, wait_after=300)
    
    def _apply_carpark_filter(self):
        """Apply carpark filter."""
        carports = self.criteria.get("carports")
        if not carports:
            return
        
        carpark_selector = self.config.get_carpark_selector(carports)
        if carpark_selector:
            logger.info(f"Selecting {carports}+ carparks")
            self.session.click(carpark_selector, wait_after=300)
    
    def _apply_price_filter(self):
        """
        Apply price filter using the slider.
        
        The Domain price slider is controlled by setting aria-valuenow via keyboard
        navigation or by directly manipulating the element. We use a combination of:
        1. Focus on the slider handle
        2. Use keyboard navigation to adjust
        3. Verify the final value matches expectation
        """
        price_min = self.criteria.get("price_min")
        price_max = self.criteria.get("price_max")
        
        if not price_min and not price_max:
            return
        
        # Domain has two separate range sliders - one for price (with aria-valuemax=13000000)
        # We need to find the correct slider by checking aria-valuemax
        price_slider_handles = self.session.page.locator(
            '[data-testid="dynamic-search-filters__range-handle"][aria-valuemax="13000000"]'
        )
        
        # Apply minimum price
        if price_min:
            self._set_price_slider_value(price_slider_handles.first, price_min, "min")
        
        # Apply maximum price
        if price_max:
            self._set_price_slider_value(price_slider_handles.last, price_max, "max")
    
    def _set_price_slider_value(self, slider_handle, target_value: int, handle_type: str):
        """
        Set a price slider to a specific value and verify.
        
        Args:
            slider_handle: The Playwright locator for the slider handle
            target_value: The target price value (e.g., 1000000 for $1M)
            handle_type: "min" or "max" for logging purposes
        """
        logger.info(f"Setting {handle_type} price to ${target_value:,}")
        
        # Focus on the slider handle
        slider_handle.focus()
        self.session.page.wait_for_timeout(200)
        
        # Get the current value and range
        current_value = int(slider_handle.get_attribute("aria-valuenow") or "0")
        max_value = int(slider_handle.get_attribute("aria-valuemax") or "13000000")
        
        logger.info(f"Current {handle_type} value: ${current_value:,}, target: ${target_value:,}")
        
        # Calculate how much we need to move
        # The slider likely has discrete steps. Use Home/End keys to go to extremes,
        # then use arrow keys or Page Up/Down to reach the target
        
        if handle_type == "max":
            # For max price, start from the end and work backwards
            self.session.page.keyboard.press("End")
            self.session.page.wait_for_timeout(200)
            
            # Now use arrow keys to decrease to target
            # Each arrow key press typically moves by one step
            # We'll use a loop to gradually adjust
            attempts = 0
            max_attempts = 200  # Prevent infinite loop
            
            while attempts < max_attempts:
                current_value = int(slider_handle.get_attribute("aria-valuenow") or "0")
                
                if current_value <= target_value:
                    break
                
                # Use Page Down for faster movement if far from target
                if current_value - target_value > 1000000:
                    self.session.page.keyboard.press("PageDown")
                else:
                    self.session.page.keyboard.press("ArrowLeft")
                
                attempts += 1
                
                # Small delay to let the UI update
                if attempts % 10 == 0:
                    self.session.page.wait_for_timeout(50)
        
        else:  # min price
            # For min price, start from the beginning and work forwards
            self.session.page.keyboard.press("Home")
            self.session.page.wait_for_timeout(200)
            
            attempts = 0
            max_attempts = 200
            
            while attempts < max_attempts:
                current_value = int(slider_handle.get_attribute("aria-valuenow") or "0")
                
                if current_value >= target_value:
                    break
                
                if target_value - current_value > 1000000:
                    self.session.page.keyboard.press("PageUp")
                else:
                    self.session.page.keyboard.press("ArrowRight")
                
                attempts += 1
                
                if attempts % 10 == 0:
                    self.session.page.wait_for_timeout(50)
        
        # Verify the final value
        final_value = int(slider_handle.get_attribute("aria-valuenow") or "0")
        logger.info(f"Final {handle_type} price value: ${final_value:,}")
        
        # Check if we're close to the target (within reasonable tolerance)
        tolerance = 50000  # $50k tolerance for slider steps
        if abs(final_value - target_value) <= tolerance:
            logger.info(f"✓ Successfully set {handle_type} price to ${final_value:,} (target: ${target_value:,})")
        else:
            logger.warning(
                f"⚠ {handle_type.capitalize()} price set to ${final_value:,}, "
                f"but target was ${target_value:,}. Difference: ${abs(final_value - target_value):,}"
            )
    
    def _apply_new_or_established_filter(self):
        """Apply new/established filter."""
        new_or_established = self.criteria.get("new_or_established")
        if not new_or_established or new_or_established == "any":
            return
        
        button_selector = self.config.get_new_or_established_button_selector()
        if not button_selector:
            return
        
        logger.info(f"Selecting new or established: {new_or_established}")
        self.session.click(button_selector, wait_after=500)
        
        # Select the option from the dropdown
        option_text = self.config.format_new_or_established_option(new_or_established)
        option_selector = f'[role="option"]:has-text("{option_text}")'
        try:
            self.session.page.click(option_selector, timeout=3000)
            self.session.page.wait_for_timeout(300)
        except Exception as e:
            logger.warning(f"Could not select new/established option: {e}")
    
    def _apply_keywords_filter(self):
        """Apply keywords filter."""
        keywords = self.criteria.get("keywords")
        if not keywords:
            return
        
        keywords_selector = self.config.get_keywords_input_selector()
        if keywords_selector:
            logger.info(f"Entering keywords: {keywords}")
            self.session.fill(keywords_selector, keywords, wait_after=300)
    
    def _submit_search(self):
        """Submit the search form."""
        logger.info("Clicking search button")
        search_btn = self.config.get_search_button_selector()
        self.session.click(search_btn)
    
    def _wait_for_results(self):
        """Wait for search results page to load."""
        logger.info("Waiting for search results page...")
        try:
            url_pattern = self.config.search_results_url_pattern
            self.session.page.wait_for_url(url_pattern, timeout=30000)
        except Exception:
            # Fallback: just wait for the page to load
            self.session.page.wait_for_load_state("load", timeout=30000)
        
        # Additional wait for content to render
        self.session.page.wait_for_timeout(2000)
        logger.info(f"Search results URL: {self.session.page.url}")
    
    def _save_results(self, output_dir: str):
        """Save search results HTML and screenshot."""
        os.makedirs("output", exist_ok=True)
        
        # Take screenshot
        self.session.screenshot("output/search_results.png")
        
        # Save and chunk the search results HTML
        save_chunks = self.criteria.get("save_html_chunks", False)
        logger.info("Saving search results HTML...")
        html = self.session.get_html()
        files = extract_and_save(html, output_dir, prefix="result_chunk", save_to_disk=save_chunks)
        if save_chunks:
            logger.info(f"Saved {len(files)} chunks to {output_dir}")
