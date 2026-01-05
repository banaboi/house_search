"""API keys and secrets configuration.

IMPORTANT: Do not commit this file to version control with real API keys!

For local development:
    Copy secrets.example.py to secrets.py and add your actual keys.

For GitHub Actions:
    Set the GOOGLE_MAPS_API_KEY as a repository secret.
    The code will automatically use the environment variable.
"""

# Google Maps API key for distance calculations
# Get your key from: https://console.cloud.google.com/apis/credentials
# Enable the "Distance Matrix API" for your project
GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"
