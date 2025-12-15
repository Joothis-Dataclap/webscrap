"""
HuggingFace Organizations Scraper
Scrapes organization names and URLs from all pages (p=0 to p=6614)
Saves checkpoints after each page to CSV
"""

import os
import csv
import time
import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "https://huggingface.co/organizations"
HF_BASE = "https://huggingface.co"
OUTPUT_DIR = Path("output")
OUTPUT_CSV = OUTPUT_DIR / "huggingface_organizations.csv"
CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint.txt"
START_PAGE = 0
END_PAGE = 6614  # Updated based on actual page count (6615 pages total)
DELAY_BETWEEN_PAGES = 1  # seconds between requests to be polite
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds to wait before retry
RATE_LIMIT_WAIT = 30  # 30 seconds wait on 429 Too Many Requests

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hf_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# SCRAPER CLASS
# ============================================================================

class HuggingFaceOrgScraper:
    """Scraper for HuggingFace organizations pages."""
    
    def __init__(self):
        """Initialize the scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Create output directory
        OUTPUT_DIR.mkdir(exist_ok=True)
        
    def get_last_checkpoint(self) -> int:
        """Get the last successfully scraped page number from checkpoint file."""
        if CHECKPOINT_FILE.exists():
            try:
                with open(CHECKPOINT_FILE, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, IOError):
                return -1
        return -1
    
    def save_checkpoint(self, page_num: int):
        """Save the current page number as checkpoint."""
        with open(CHECKPOINT_FILE, 'w') as f:
            f.write(str(page_num))
    
    def init_csv(self, resume: bool = False):
        """Initialize the CSV file with headers if not resuming."""
        if not resume or not OUTPUT_CSV.exists():
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['organization_name', 'organization_url', 'page_number'])
            logger.info(f"Created new CSV file: {OUTPUT_CSV}")
    
    def append_to_csv(self, organizations: List[Tuple[str, str]], page_num: int):
        """Append organization data to CSV file."""
        with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for name, url in organizations:
                writer.writerow([name, url, page_num])
    
    def scrape_page(self, page_num: int) -> Optional[List[Tuple[str, str]]]:
        """
        Scrape a single page of organizations.
        
        Args:
            page_num: Page number to scrape (0-indexed)
            
        Returns:
            List of tuples (organization_name, organization_url) or None on failure
        """
        url = f"{BASE_URL}?p={page_num}"
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                organizations = []
                
                # Find all organization links
                # Organizations are in anchor tags that link to organization profiles
                # Pattern: <a href="/org-name">Organization Name</a>
                
                # Look for organization cards/links in the main content
                # Based on the page structure, org links are direct links to /{org-slug}
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    
                    # Filter for organization profile links
                    # They follow pattern: /org-name (single path segment, not /models, /datasets, etc.)
                    if (href.startswith('/') and 
                        href.count('/') == 1 and 
                        len(href) > 1 and
                        not href.startswith('/#') and
                        href not in ['/models', '/datasets', '/spaces', '/docs', '/pricing', 
                                    '/terms-of-service', '/privacy', '/users', '/login',
                                    '/join', '/settings', '/new', '/organizations']):
                        
                        # Check if it's an organization link by looking at the link content
                        # Organization cards typically contain "followers" text
                        link_text = link.get_text(strip=True)
                        
                        if 'follower' in link_text.lower():
                            # Extract organization name (first part before additional info)
                            # Format varies:
                            # - "Org Name Team Company • X models • Y followers" 
                            # - "Org NameTeam68 models • Y followers" (no bullet before models)
                            import re
                            
                            # First split by bullet if present
                            org_name = link_text.split('•')[0].strip()
                            
                            # Remove model count patterns like "68 models", "1.05k models"
                            org_name = re.sub(r'\d+\.?\d*k?\s*models?', '', org_name, flags=re.IGNORECASE).strip()
                            
                            # Remove follower count patterns
                            org_name = re.sub(r'\d+\.?\d*k?\s*followers?', '', org_name, flags=re.IGNORECASE).strip()
                            
                            # Clean up common suffixes and type labels
                            # These labels appear without spaces sometimes
                            org_name = re.sub(r'(Team|Enterprise|Company|Non-Profit|Community|University|company|non-profit|community|university|\+\s*)+$', '', org_name, flags=re.IGNORECASE).strip()
                            
                            # Also handle "'s profile picture" if present in text
                            org_name = re.sub(r"'s profile picture.*$", '', org_name, flags=re.IGNORECASE).strip()
                            
                            # Remove any trailing special characters
                            org_name = org_name.rstrip('+ ').strip()
                            
                            org_url = f"{HF_BASE}{href}"
                            
                            # Avoid duplicates within same page
                            if (org_name, org_url) not in organizations:
                                organizations.append((org_name, org_url))
                
                logger.info(f"Page {page_num}: Found {len(organizations)} organizations")
                return organizations
                
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    # Rate limited - wait 3 minutes and retry
                    logger.warning(f"Rate limited (429) on page {page_num}. Waiting {RATE_LIMIT_WAIT} seconds (3 minutes) before retrying...")
                    time.sleep(RATE_LIMIT_WAIT)
                    # Don't count this as a failed attempt - retry immediately
                    continue
                else:
                    logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for page {page_num}: {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                    else:
                        logger.error(f"All retries failed for page {page_num}")
                        return None
                        
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for page {page_num}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All retries failed for page {page_num}")
                    return None
        
        return None
    
    def run(self, start_page: Optional[int] = None, end_page: Optional[int] = None):
        """
        Run the scraper for the specified page range.
        
        Args:
            start_page: Starting page number (default: resume from checkpoint or 0)
            end_page: Ending page number (default: END_PAGE)
        """
        # Determine starting page
        last_checkpoint = self.get_last_checkpoint()
        
        if start_page is None:
            if last_checkpoint >= 0:
                start_page = last_checkpoint + 1
                logger.info(f"Resuming from checkpoint: page {start_page}")
                resume = True
            else:
                start_page = START_PAGE
                resume = False
        else:
            resume = start_page > 0 and OUTPUT_CSV.exists()
        
        if end_page is None:
            end_page = END_PAGE
        
        # Initialize CSV
        self.init_csv(resume=resume)
        
        total_orgs = 0
        
        logger.info(f"Starting scrape from page {start_page} to {end_page}")
        
        for page_num in range(start_page, end_page + 1):
            organizations = self.scrape_page(page_num)
            
            if organizations is not None:
                if organizations:
                    self.append_to_csv(organizations, page_num)
                    total_orgs += len(organizations)
                
                # Save checkpoint after each successful page
                self.save_checkpoint(page_num)
                
                # Progress update every 100 pages
                if page_num % 100 == 0:
                    logger.info(f"Progress: Page {page_num}/{end_page} | Total organizations: {total_orgs}")
            else:
                logger.error(f"Failed to scrape page {page_num}. Stopping.")
                break
            
            # Be polite to the server
            time.sleep(DELAY_BETWEEN_PAGES)
        
        logger.info(f"Scraping complete! Total organizations collected: {total_orgs}")
        logger.info(f"Data saved to: {OUTPUT_CSV}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape HuggingFace organizations')
    parser.add_argument('--start', type=int, default=None, 
                        help='Starting page number (default: resume from checkpoint)')
    parser.add_argument('--end', type=int, default=END_PAGE,
                        help=f'Ending page number (default: {END_PAGE})')
    parser.add_argument('--reset', action='store_true',
                        help='Reset checkpoint and start fresh')
    
    args = parser.parse_args()
    
    scraper = HuggingFaceOrgScraper()
    
    if args.reset:
        # Remove checkpoint and CSV to start fresh
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
            logger.info("Checkpoint removed")
        if OUTPUT_CSV.exists():
            OUTPUT_CSV.unlink()
            logger.info("Previous CSV removed")
        args.start = 0
    
    scraper.run(start_page=args.start, end_page=args.end)


if __name__ == "__main__":
    main()
