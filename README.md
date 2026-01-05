# House Search Automation 🏠

A modular property search automation tool for Australian real estate websites. Automates property searches, parses results, enriches listings with transit times, and generates beautiful HTML reports.

## Features

- 🔍 **Automated Property Search** - Automate searches on Domain.com.au with customizable criteria
- 📊 **HTML Parsing & CSV Export** - Parse search results and export to structured CSV
- 🚇 **Transit Time Enrichment** - Calculate public transport times to key locations using Google Maps
- 📱 **Mobile-Friendly HTML Reports** - Generate beautiful, responsive property listing pages
- 🎭 **Anti-Detection** - Uses Playwright with stealth techniques to avoid bot detection
- 🧩 **Modular Architecture** - Easily extensible to support additional property websites

## Supported Sites

| Site | Status |
|------|--------|
| Domain.com.au | ✅ Supported |
| RealEstate.com.au | 🚧 In Progress |

## Installation

### Prerequisites

- Python 3.11+
- A Google Maps API key (for distance enrichment)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/banaboi/house_search.git
   cd house_search
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

5. **Configure API keys**
   ```bash
   cp config/secrets.example.py config/secrets.py
   ```
   Edit `config/secrets.py` and add your Google Maps API key.

   Alternatively, set the environment variable:
   ```bash
   export GOOGLE_MAPS_API_KEY="your-api-key-here"
   ```

## Configuration

### Search Criteria

Edit `config/search_criteria.py` to customize your property search:

```python
SEARCH_CRITERIA = {
    # Property features
    "bedrooms": 2,
    "bathrooms": 1,
    "carports": 1,
    
    # Locations to search
    "locations": [
        "Chatswood",
        "Lane Cove",
        "Willoughby",
        # Add more suburbs...
    ],
    
    # Property type (house, apartment, townhouse, land, retirement)
    "property_type": "apartment",
    "new_or_established": "established",
    
    # Price range
    "price_min": 0,
    "price_max": 1000000,
    
    # Search mode (buy, rent, sold)
    "mode": "buy",
    
    # Optional keywords
    "keywords": "brick",
}
```

### Key Locations for Distance Calculations

Edit `config/locations.py` to customize the locations for transit time calculations:

```python
KEY_LOCATIONS = [
    Location(
        name="Bella Vista",
        address="Bella Vista, NSW, Australia",
        slug="bella_vista",
    ),
    Location(
        name="Royal North Shore Hospital",
        address="Reserve Road, St Leonards, NSW 2065, Australia",
        slug="rnsh",
    ),
    # Add more locations...
]
```

## Usage

### Commands

```bash
# List all available property sites
python main.py list-sites

# Grab homepage HTML (for development/debugging)
python main.py grab-home --site domain

# Grab filters modal HTML (for development/debugging)
python main.py grab-filters --site domain

# Perform a property search
python main.py search --site domain

# Parse search results to CSV
python main.py parse --site domain

# Parse and enrich with transit times
python main.py parse --site domain --enrich

# Parse, enrich, and generate HTML report
python main.py parse --site domain --enrich --html
```

### Example Workflow

1. **Configure your search criteria** in `config/search_criteria.py`

2. **Run the search** to scrape property listings:
   ```bash
   python main.py search --site domain
   ```

3. **Parse and export** the results:
   ```bash
   python main.py parse --site domain --enrich --html
   ```

4. **View your results**:
   - CSV file: `output/domain/listings.csv`
   - HTML report: `output/domain/listings.html`

## Project Structure

```
house_search/
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── config/
│   ├── locations.py        # Key locations for distance calculations
│   ├── search_criteria.py  # Search filters and criteria
│   └── secrets.py          # API keys (not in version control)
├── engine/
│   └── search_engine.py    # Core search automation logic
├── sites/
│   ├── base.py             # Base site configuration class
│   ├── domain.py           # Domain.com.au configuration
│   └── realestate.py       # RealEstate.com.au configuration
├── parsers/
│   ├── base.py             # Base parser class
│   ├── domain.py           # Domain.com.au HTML parser
│   └── models.py           # PropertyListing data models
├── enrichment/
│   └── distance_enricher.py # Transit time calculations
├── output/
│   └── html_generator.py   # HTML report generator
├── utils/
│   ├── browser.py          # Playwright browser utilities
│   ├── distance.py         # Google Maps distance calculator
│   └── html_parser.py      # HTML parsing utilities
└── cache/
    └── distance_cache.json # Cached distance calculations
```

## Output

### CSV Export

The CSV file includes the following fields for each listing:

| Field | Description |
|-------|-------------|
| `listing_id` | Unique identifier |
| `url` | Link to the listing |
| `address_line1` | Street address |
| `address_line2` | Suburb |
| `full_address` | Complete address |
| `price` | Listed price |
| `bedrooms` | Number of bedrooms |
| `bathrooms` | Number of bathrooms |
| `parking` | Number of parking spaces |
| `property_type` | Type of property |
| `image_url` | Primary image URL |
| `agent_name` | Listing agent |
| `agency_name` | Real estate agency |
| `inspection_time` | Open inspection times |
| `status` | Listing status |
| `distance_*_mins` | Transit time to key locations |

### HTML Report

The HTML report features:
- 📱 Mobile-responsive design
- 🖼️ Property images with gallery
- 🏷️ Price and feature badges
- 🗺️ Transit times to key locations
- 🔗 Direct links to listings
- 🔍 Filter and sort functionality

## API Keys

### Google Maps API

The distance enrichment feature requires a Google Maps API key with the **Distance Matrix API** enabled.

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new API key
3. Enable the "Distance Matrix API"
4. Add the key to `config/secrets.py` or set `GOOGLE_MAPS_API_KEY` environment variable

## Caching

Distance calculations are cached in `cache/distance_cache.json` to:
- Reduce API calls and costs
- Speed up subsequent runs
- Avoid redundant calculations

## Development

### Adding a New Site

1. Create a new configuration in `sites/` (e.g., `sites/newsite.py`)
2. Extend `SiteConfig` with site-specific selectors
3. Create a parser in `parsers/` (e.g., `parsers/newsite.py`)
4. Register the site in `sites/__init__.py` and `parsers/__init__.py`

### Running in CI/GitHub Actions

The tool automatically detects CI environments and:
- Forces headless browser mode
- Uses Firefox for better compatibility
- Adjusts timeouts and retry logic

## License

This project is for personal use.

## Disclaimer

This tool is for personal use only. Please respect the terms of service of the property websites and use responsibly. The authors are not responsible for any misuse or violations of website terms of service.
