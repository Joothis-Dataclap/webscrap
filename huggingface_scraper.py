"""
HuggingFace Organizations Scraper using Firecrawl
Extracts company names and social media links, saves to Excel
"""

import os
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
HF_BASE_URL = "https://huggingface.co"
OUTPUT_FILE = "huggingface_organizations.xlsx"
RATE_LIMIT_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FIRECRAWL SETUP
# ============================================================================

def init_firecrawl():
    """Initialize Firecrawl"""
    if not FIRECRAWL_API_KEY or FIRECRAWL_API_KEY == "":
        logger.error("FIRECRAWL_API_KEY not set in .env file")
        raise ValueError("API key required")
    return FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# ============================================================================
# SCRAPING FUNCTIONS
# ============================================================================

def scrape_org_list_page(app: FirecrawlApp, page_num: int) -> Optional[List[Dict]]:
    """
    Scrape organization listing page
    Returns list of org dicts with 'name' and 'link'
    """
    url = f"https://huggingface.co/organizations?p={page_num}"
    
    try:
        logger.info(f"Scraping listing page: {url}")
        
        # Use LLM extraction to find all organization links
        result = app.extract(url, {
            "prompt": "Extract all organization names and their profile links. Return as JSON with 'organizations' array containing objects with 'name' and 'link' fields."
        })
        
        if result and isinstance(result, dict):
            if "organizations" in result:
                orgs = result["organizations"]
                if isinstance(orgs, list):
                    logger.info(f"Found {len(orgs)} organizations on page {page_num}")
                    return orgs
        
        logger.warning(f"No organizations found on page {page_num}")
        return []
    
    except Exception as e:
        logger.error(f"Error scraping page {page_num}: {str(e)}")
        return None

def scrape_org_profile(app: FirecrawlApp, org_link: str) -> Optional[Dict]:
    """
    Scrape organization profile page
    Returns dict with company_name and social_links
    """
    full_url = urljoin(HF_BASE_URL, org_link)
    
    try:
        logger.debug(f"Scraping profile: {full_url}")
        
        result = app.extract(full_url, {
            "prompt": "Extract the company/organization name and all social media links. For each social link, identify if it's LinkedIn, Twitter/X, GitHub, Instagram, or Facebook. Return as JSON with 'company_name' string and 'social_links' array of objects with 'platform' and 'url'."
        })
        
        if result and isinstance(result, dict):
            if "company_name" in result or "social_links" in result:
                logger.debug(f"Extracted profile for: {result.get('company_name', 'Unknown')}")
                return result
        
        return {"company_name": "", "social_links": []}
    
    except Exception as e:
        logger.error(f"Error scraping profile {org_link}: {str(e)}")
        return None

# ============================================================================
# SOCIAL MEDIA EXTRACTION
# ============================================================================

def extract_social_media(social_links: Optional[List[Dict]]) -> Dict[str, str]:
    """
    Extract specific social media URLs from social_links array
    """
    socials = {
        "linkedin": "",
        "twitter": "",
        "github": "",
        "instagram": "",
        "facebook": ""
    }
    
    if not social_links or not isinstance(social_links, list):
        return socials
    
    for link in social_links:
        if not isinstance(link, dict):
            continue
        
        platform = link.get("platform", "").lower()
        url = link.get("url", "")
        
        if not url:
            continue
        
        if "linkedin" in platform:
            socials["linkedin"] = url
        elif "twitter" in platform or "x.com" in url.lower():
            socials["twitter"] = url
        elif "github" in platform:
            socials["github"] = url
        elif "instagram" in platform:
            socials["instagram"] = url
        elif "facebook" in platform:
            socials["facebook"] = url
    
    return socials

# ============================================================================
# MAIN SCRAPER
# ============================================================================

def scrape_page(app: FirecrawlApp, page_num: int) -> List[Dict]:
    """
    Scrape one page of organizations and their profiles
    """
    organizations = []
    
    # Step 1: Get org list on the page
    org_list = scrape_org_list_page(app, page_num)
    
    if org_list is None:
        logger.error(f"Failed to scrape page {page_num}")
        return []
    
    if not org_list:
        logger.warning(f"No organizations on page {page_num}")
        return []
    
    logger.info(f"Processing {len(org_list)} organizations from page {page_num}")
    
    # Step 2: For each org, scrape their profile
    for i, org in enumerate(tqdm(org_list, desc=f"Page {page_num}", unit="org"), 1):
        try:
            org_name = org.get("name", "Unknown")
            org_link = org.get("link", "")
            
            if not org_link:
                logger.warning(f"No link for org: {org_name}")
                continue
            
            # Scrape profile
            profile = scrape_org_profile(app, org_link)
            
            if profile is None:
                logger.warning(f"Failed to scrape profile for: {org_name}")
                continue
            
            # Extract social media
            socials = extract_social_media(profile.get("social_links", []))
            
            # Build record
            record = {
                "Company Name": profile.get("company_name", org_name),
                "Org URL": urljoin(HF_BASE_URL, org_link),
                "LinkedIn": socials.get("linkedin", ""),
                "Twitter": socials.get("twitter", ""),
                "GitHub": socials.get("github", ""),
                "Instagram": socials.get("instagram", ""),
                "Facebook": socials.get("facebook", ""),
                "All Social Links": " | ".join([link.get("url", "") for link in profile.get("social_links", []) if link.get("url")])
            }
            
            organizations.append(record)
            logger.info(f"[{i}/{len(org_list)}] Scraped: {record['Company Name']}")
            
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
        
        except Exception as e:
            logger.error(f"Error processing org {org.get('name', 'Unknown')}: {str(e)}")
            continue
    
    return organizations

def save_to_excel(organizations: List[Dict], filename: str):
    """Save organizations to Excel file"""
    if not organizations:
        logger.error("No data to save")
        return
    
    try:
        df = pd.DataFrame(organizations)
        df.to_excel(filename, index=False, engine='openpyxl')
        logger.info(f"Saved {len(df)} organizations to {filename}")
        logger.info(f"File: {os.path.abspath(filename)}")
        return df
    except Exception as e:
        logger.error(f"Error saving to Excel: {str(e)}")
        return None

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    try:
        logger.info("=" * 60)
        logger.info("HuggingFace Organizations Scraper")
        logger.info("=" * 60)
        
        # Initialize
        app = init_firecrawl()
        logger.info("Firecrawl initialized")
        
        # Scrape page 0
        logger.info("\nStarting scrape...")
        organizations = scrape_page(app, page_num=0)
        
        # Save to Excel
        if organizations:
            logger.info(f"\nSaving {len(organizations)} organizations to Excel...")
            df = save_to_excel(organizations, OUTPUT_FILE)
            
            if df is not None:
                logger.info("\nSample data (first 5 rows):")
                logger.info(df.head().to_string())
                logger.info("\nDone!")
        else:
            logger.error("No organizations scraped")
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
