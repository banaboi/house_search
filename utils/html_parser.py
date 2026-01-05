"""HTML parsing and extraction utilities."""

import logging
import os
from bs4 import BeautifulSoup, Comment

logger = logging.getLogger(__name__)

# Default chunk size for splitting HTML
DEFAULT_CHUNK_SIZE = 4000


def extract_filter_html(html: str) -> str:
    """
    Returns a token-friendly snippet containing relevant interactive and content elements:
    - inputs, selects, buttons, labels (for filters/forms)
    - anchors (for clickable links to property pages)
    - elements with data-testid attributes (for structured content)
    - spans, divs with address/price/feature related attributes
    Removes scripts, styles, comments, and common irrelevant sections.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts and styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Optional: remove headers, footers, navs, banners
    for selector in ["header", "footer", "nav", ".ads", ".promo", ".banner"]:
        for tag in soup.select(selector):
            tag.decompose()

    # Keep form elements and interactive elements
    form_elements = soup.find_all(["input", "select", "button", "label"])
    
    # Keep anchor tags (links to property pages)
    anchor_elements = soup.find_all("a", href=True)
    
    # Keep elements with data-testid attributes (structured content)
    # These are commonly used for addresses, prices, features, listing cards
    testid_elements = soup.find_all(attrs={"data-testid": True})
    
    # Combine all elements, removing duplicates while preserving order
    seen = set()
    all_elements = []
    for el in form_elements + anchor_elements + testid_elements:
        el_id = id(el)
        if el_id not in seen:
            seen.add(el_id)
            all_elements.append(el)

    # Convert to string
    token_safe_html = "\n".join(str(el) for el in all_elements)

    return token_safe_html


def chunk_html(html: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    """Split HTML into chunks of approximately chunk_size characters."""
    chunks = []
    for i in range(0, len(html), chunk_size):
        chunks.append(html[i:i + chunk_size])
    return chunks


def save_chunks(chunks: list[str], output_dir: str, prefix: str = "chunk") -> list[str]:
    """Save HTML chunks to files and return list of file paths."""
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    for i, chunk in enumerate(chunks, 1):
        filename = f"{prefix}_{i:03d}.html"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(chunk)
        logger.info(f"Saved {filepath}")
        saved_files.append(filepath)
    
    return saved_files


def extract_and_save(html: str, output_dir: str, prefix: str = "chunk", 
                     chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    """Extract filter HTML, chunk it, and save to files."""
    filter_html = extract_filter_html(html)
    logger.info(f"Extracted {len(filter_html)} characters of filter HTML")
    
    chunks = chunk_html(filter_html, chunk_size)
    logger.info(f"Split into {len(chunks)} chunks of ~{chunk_size} characters each")
    
    return save_chunks(chunks, output_dir, prefix)
