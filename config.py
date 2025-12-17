"""
Google Sheets Integration Configuration
Configure how the scraper syncs with Google Sheets
"""

# ============================================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================================

# Enable live Google Sheets updates during scraping
GOOGLE_SHEETS_ENABLED = True

# Path to Google service account credentials JSON file
# Get this from: https://console.cloud.google.com/
# Instructions in src/google_sheets_uploader.py
GOOGLE_CREDENTIALS_PATH = "webscrapping-481404-c6ff8576cf4a.json"

# Name of the Google Sheet to create/update
GOOGLE_SHEET_NAME = "HuggingFace Organizations Live"

# Upload data to Google Sheets every N organizations scraped
# Lower value = more frequent updates, higher = faster scraping
UPLOAD_INTERVAL = 25  # Every 25 organizations

# ============================================================================
# SCRAPING CONFIGURATION
# ============================================================================

# Maximum retries for failed requests
MAX_RETRIES = 3

# Retry delays (seconds)
RETRY_DELAYS = [30, 60, 180]  # 30s → 60s → 3min

# Request timeout (seconds)
REQUEST_TIMEOUT = 60

# Delay between requests (seconds) - be respectful!
REQUEST_DELAY = 1

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Input CSV path (Phase 1 output)
INPUT_CSV_PATH = "output/huggingface_organizations.csv"

# Output CSV path (Phase 2 enhanced data)
OUTPUT_CSV_PATH = "output/huggingface_organizations_detailed.csv"

# Checkpoint file for resume capability
CHECKPOINT_FILE = "output/phase2_checkpoint.json"

# ============================================================================
# LOGGING
# ============================================================================

# Log file location
LOG_DIR = "output"

# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

"""
To enable Google Sheets integration:

1. Set GOOGLE_SHEETS_ENABLED = True above

2. Create Google Sheets credentials:
   python -c "from src.google_sheets_uploader import setup_google_sheets_integration; setup_google_sheets_integration()"

3. Download credentials JSON from Google Cloud Console
   - Save as 'google_credentials.json' in project root

4. Share your Google Sheet with the service account email
   - Email is in the credentials JSON file

5. Update GOOGLE_SHEET_NAME if needed (default: "HuggingFace Organizations Live")

6. Adjust UPLOAD_INTERVAL for frequency (lower = more updates, slower scraping)

7. Run the scraper - it will automatically sync to Google Sheets!

"""
