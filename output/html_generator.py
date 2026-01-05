"""
HTML Generator for Property Listings

Generates a mobile-friendly HTML webpage displaying property listings
with images, prices, features, and transit times to key locations.
"""

import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parsers.models import PropertyListingCollection, PropertyListing


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Listings - {date}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary-color: #64748b;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --radius: 12px;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
            color: white;
            padding: 20px 16px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow);
        }}

        .header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .header p {{
            font-size: 0.875rem;
            opacity: 0.9;
        }}

        .stats-bar {{
            display: flex;
            gap: 16px;
            margin-top: 12px;
            flex-wrap: wrap;
        }}

        .stat {{
            background: rgba(255,255,255,0.15);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .filter-bar {{
            background: var(--card-bg);
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 8px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        .filter-btn {{
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 16px;
        }}

        .listings-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }}

        .listing-card {{
            background: var(--card-bg);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .listing-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}

        .listing-card a {{
            text-decoration: none;
            color: inherit;
        }}

        .image-container {{
            position: relative;
            width: 100%;
            height: 200px;
            overflow: hidden;
        }}

        .listing-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }}

        .listing-card:hover .listing-image {{
            transform: scale(1.05);
        }}

        .image-count {{
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
        }}

        .status-badge {{
            position: absolute;
            top: 8px;
            left: 8px;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .status-badge.sold {{
            background: var(--danger-color);
            color: white;
        }}

        .status-badge.for-sale {{
            background: var(--success-color);
            color: white;
        }}

        .status-badge.auction {{
            background: var(--warning-color);
            color: white;
        }}

        .listing-content {{
            padding: 16px;
        }}

        .price {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 8px;
        }}

        .address {{
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 4px;
        }}

        .suburb {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }}

        .features {{
            display: flex;
            gap: 16px;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }}

        .feature {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }}

        .feature svg {{
            width: 18px;
            height: 18px;
            fill: var(--text-secondary);
        }}

        .feature span {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .transit-times {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .transit-times h4 {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}

        .transit-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }}

        .transit-location {{
            color: var(--text-secondary);
        }}

        .transit-time {{
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
        }}

        .transit-time.fast {{
            background: #dcfce7;
            color: #166534;
        }}

        .transit-time.medium {{
            background: #fef3c7;
            color: #92400e;
        }}

        .transit-time.slow {{
            background: #fee2e2;
            color: #991b1b;
        }}

        .agent-info {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--border-color);
        }}

        .agency-logo {{
            width: 60px;
            height: 30px;
            object-fit: contain;
        }}

        .agent-details {{
            font-size: 0.8rem;
        }}

        .agent-name {{
            font-weight: 500;
            color: var(--text-primary);
        }}

        .agency-name {{
            color: var(--text-secondary);
        }}

        .inspection-badge {{
            background: linear-gradient(135deg, #fef3c7, #fde68a);
            color: #92400e;
            padding: 8px 12px;
            border-radius: 8px;
            margin-top: 12px;
            font-size: 0.8rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .inspection-badge svg {{
            width: 16px;
            height: 16px;
            fill: #92400e;
        }}

        .no-listings {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }}

        .no-listings h2 {{
            font-size: 1.5rem;
            margin-bottom: 8px;
        }}

        /* Sort controls */
        .sort-container {{
            background: var(--card-bg);
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .sort-container label {{
            font-size: 0.85rem;
            font-weight: 500;
        }}

        .sort-container select {{
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 0.85rem;
            background: var(--bg-color);
        }}

        @media (max-width: 640px) {{
            .listings-grid {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 1.25rem;
            }}
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 24px 16px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            border-top: 1px solid var(--border-color);
            margin-top: 24px;
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>🏠 Property Listings</h1>
        <p>Last updated: {date}</p>
        <div class="stats-bar">
            <div class="stat">📊 {total_listings} Properties</div>
            <div class="stat">📍 {suburb_count} Suburbs</div>
        </div>
    </header>

    <div class="filter-bar" id="suburbFilters">
        <button class="filter-btn active" data-suburb="all">All Suburbs</button>
        {suburb_filters}
    </div>

    <div class="sort-container">
        <label>Sort by:</label>
        <select id="sortSelect" onchange="sortListings(this.value)">
            <option value="default">Default</option>
            <option value="price-asc">Price (Low to High)</option>
            <option value="price-desc">Price (High to Low)</option>
            <option value="transit-bella">Transit to Bella Vista</option>
            <option value="transit-rnsh">Transit to RNSH</option>
            <option value="transit-qvb">Transit to QVB</option>
        </select>
    </div>

    <main class="container">
        <div class="listings-grid" id="listingsGrid">
            {listings_html}
        </div>
    </main>

    <footer class="footer">
        <p>Generated by House Search Tool • {date}</p>
    </footer>

    <script>
        // Filter by suburb
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const suburb = this.dataset.suburb;
                filterBySuburb(suburb);
            }});
        }});

        function filterBySuburb(suburb) {{
            document.querySelectorAll('.listing-card').forEach(card => {{
                if (suburb === 'all' || card.dataset.suburb === suburb) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function sortListings(sortBy) {{
            const grid = document.getElementById('listingsGrid');
            const cards = Array.from(grid.querySelectorAll('.listing-card'));
            
            cards.sort((a, b) => {{
                switch(sortBy) {{
                    case 'price-asc':
                        return parsePrice(a.dataset.price) - parsePrice(b.dataset.price);
                    case 'price-desc':
                        return parsePrice(b.dataset.price) - parsePrice(a.dataset.price);
                    case 'transit-bella':
                        return parseFloat(a.dataset.transitBella || 999) - parseFloat(b.dataset.transitBella || 999);
                    case 'transit-rnsh':
                        return parseFloat(a.dataset.transitRnsh || 999) - parseFloat(b.dataset.transitRnsh || 999);
                    case 'transit-qvb':
                        return parseFloat(a.dataset.transitQvb || 999) - parseFloat(b.dataset.transitQvb || 999);
                    default:
                        return 0;
                }}
            }});
            
            cards.forEach(card => grid.appendChild(card));
        }}

        function parsePrice(priceStr) {{
            if (!priceStr) return 999999999;
            const match = priceStr.match(/\\d[\\d,]*/);
            if (match) {{
                return parseInt(match[0].replace(/,/g, ''));
            }}
            return 999999999;
        }}
    </script>
</body>
</html>
'''

LISTING_CARD_TEMPLATE = '''
<article class="listing-card" 
         data-suburb="{suburb_slug}" 
         data-price="{price}"
         data-transit-bella="{transit_bella}"
         data-transit-rnsh="{transit_rnsh}"
         data-transit-qvb="{transit_qvb}">
    <a href="{url}" target="_blank" rel="noopener noreferrer">
        <div class="image-container">
            <img class="listing-image" src="{image_url}" alt="{address}" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 200%22><rect fill=%22%23e2e8f0%22 width=%22400%22 height=%22200%22/><text fill=%22%2394a3b8%22 x=%2250%%22 y=%2250%%22 text-anchor=%22middle%22 dy=%22.3em%22 font-family=%22sans-serif%22>No Image</text></svg>'">
            {status_badge}
            {image_count_badge}
        </div>
        <div class="listing-content">
            <div class="price">{price}</div>
            <div class="address">{address_line1}</div>
            <div class="suburb">{suburb}</div>
            
            <div class="features">
                <div class="feature">
                    <svg viewBox="0 0 24 24"><path d="M7 14c1.66 0 3-1.34 3-3S8.66 8 7 8s-3 1.34-3 3 1.34 3 3 3zm0-4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm12-3h-8v8H3V5H1v15h2v-3h18v3h2v-9c0-2.21-1.79-4-4-4zm2 8h-8V9h6c1.1 0 2 .9 2 2v4z"/></svg>
                    <span>{bedrooms}</span>
                </div>
                <div class="feature">
                    <svg viewBox="0 0 24 24"><path d="M7 7c0-1.1.9-2 2-2s2 .9 2 2-.9 2-2 2-2-.9-2-2zm2-4C6.24 3 4 5.24 4 8v8c0 .55.45 1 1 1h1v4h12v-4h1c.55 0 1-.45 1-1V8c0-2.76-2.24-5-5-5H9zm7 9V8c0-1.66-1.34-3-3-3H9c-1.66 0-3 1.34-3 3v4h2V8c0-.55.45-1 1-1h4c.55 0 1 .45 1 1v4h2z"/></svg>
                    <span>{bathrooms}</span>
                </div>
                <div class="feature">
                    <svg viewBox="0 0 24 24"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>
                    <span>{parking}</span>
                </div>
            </div>

            <div class="transit-times">
                <h4>🚇 Transit Times</h4>
                <div class="transit-row">
                    <span class="transit-location">Bella Vista</span>
                    <span class="transit-time {transit_bella_class}">{transit_bella_display}</span>
                </div>
                <div class="transit-row">
                    <span class="transit-location">RNSH</span>
                    <span class="transit-time {transit_rnsh_class}">{transit_rnsh_display}</span>
                </div>
                <div class="transit-row">
                    <span class="transit-location">QVB (Sydney)</span>
                    <span class="transit-time {transit_qvb_class}">{transit_qvb_display}</span>
                </div>
            </div>

            {agent_section}
            {inspection_section}
        </div>
    </a>
</article>
'''


def get_transit_class(mins: float | None) -> str:
    """Get CSS class based on transit time."""
    if mins is None:
        return "medium"
    if mins <= 30:
        return "fast"
    elif mins <= 50:
        return "medium"
    else:
        return "slow"


def format_transit_time(mins: float | None) -> str:
    """Format transit time for display."""
    if mins is None:
        return "N/A"
    return f"{int(mins)} min"


def get_status_badge(status: str, price: str) -> str:
    """Generate status badge HTML."""
    status_lower = status.lower() if status else ""
    price_lower = price.lower() if price else ""
    
    if "sold" in status_lower:
        return '<span class="status-badge sold">Sold</span>'
    elif "auction" in price_lower:
        return '<span class="status-badge auction">Auction</span>'
    elif "for sale" in status_lower or "for sale" in price_lower:
        return '<span class="status-badge for-sale">For Sale</span>'
    return ""


def generate_listing_card(listing: 'PropertyListing') -> str:
    """Generate HTML for a single listing card."""
    # Get image URLs
    image_urls = listing.image_urls if listing.image_urls else []
    image_url = listing.image_url or (image_urls[0] if image_urls else "")
    image_count = len(image_urls) if image_urls else 0
    
    # Image count badge
    image_count_badge = ""
    if image_count > 1:
        image_count_badge = f'<span class="image-count">📷 {image_count}</span>'
    
    # Status badge
    status_badge = get_status_badge(listing.status, listing.price)
    
    # Transit times
    transit_bella = listing.distance_bella_vista_mins
    transit_rnsh = listing.distance_rnsh_mins
    transit_qvb = listing.distance_qvb_mins
    
    # Agent section
    agent_section = ""
    if listing.agent_name or listing.agency_name:
        agency_logo_html = ""
        if listing.agency_logo_url:
            agency_logo_html = f'<img class="agency-logo" src="{listing.agency_logo_url}" alt="{listing.agency_name}" onerror="this.style.display=\'none\'">'
        
        agent_section = f'''
        <div class="agent-info">
            {agency_logo_html}
            <div class="agent-details">
                <div class="agent-name">{listing.agent_name or "Agent"}</div>
                <div class="agency-name">{listing.agency_name or ""}</div>
            </div>
        </div>
        '''
    
    # Inspection section
    inspection_section = ""
    if listing.inspection_time:
        inspection_section = f'''
        <div class="inspection-badge">
            <svg viewBox="0 0 24 24"><path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/></svg>
            {listing.inspection_time}
        </div>
        '''
    
    # Suburb slug for filtering
    suburb_slug = (listing.address_line2 or "unknown").lower().replace(" ", "-")
    
    return LISTING_CARD_TEMPLATE.format(
        url=listing.url or "#",
        image_url=image_url,
        address=listing.full_address or listing.address_line1,
        status_badge=status_badge,
        image_count_badge=image_count_badge,
        price=listing.price or "Contact Agent",
        address_line1=listing.address_line1 or "",
        suburb=listing.address_line2 or "",
        suburb_slug=suburb_slug,
        bedrooms=listing.bedrooms or "-",
        bathrooms=listing.bathrooms or "-",
        parking=listing.parking or "-",
        transit_bella=transit_bella or "",
        transit_rnsh=transit_rnsh or "",
        transit_qvb=transit_qvb or "",
        transit_bella_display=format_transit_time(transit_bella),
        transit_rnsh_display=format_transit_time(transit_rnsh),
        transit_qvb_display=format_transit_time(transit_qvb),
        transit_bella_class=get_transit_class(transit_bella),
        transit_rnsh_class=get_transit_class(transit_rnsh),
        transit_qvb_class=get_transit_class(transit_qvb),
        agent_section=agent_section,
        inspection_section=inspection_section,
    )


def generate_html(collection: 'PropertyListingCollection', output_path: str) -> str:
    """
    Generate a mobile-friendly HTML page from a property listing collection.
    
    Args:
        collection: The PropertyListingCollection to generate HTML from
        output_path: Path to save the HTML file
        
    Returns:
        The absolute path to the saved HTML file
    """
    if not collection.listings:
        raise ValueError("No listings to export")
    
    # Generate listing cards
    listings_html = "\n".join(
        generate_listing_card(listing) for listing in collection.listings
    )
    
    # Generate suburb filter buttons
    suburbs = collection.get_unique_suburbs()
    suburb_filters = "\n".join(
        f'<button class="filter-btn" data-suburb="{suburb.lower().replace(" ", "-")}">{suburb}</button>'
        for suburb in suburbs
    )
    
    # Format the date
    date_str = datetime.now().strftime("%d %B %Y, %I:%M %p")
    
    # Generate full HTML
    html = HTML_TEMPLATE.format(
        date=date_str,
        total_listings=len(collection),
        suburb_count=len(suburbs),
        suburb_filters=suburb_filters,
        listings_html=listings_html,
    )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return os.path.abspath(output_path)
