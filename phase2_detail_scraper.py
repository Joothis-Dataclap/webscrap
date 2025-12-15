#!/usr/bin/env python3
"""
HuggingFace Organization Detail Scraper - Phase 2
Scrapes detailed information from organization pages including:
- Social media links (Twitter, LinkedIn, etc.)
- GitHub links
- Website links
- Company location
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
import json
import re
from urllib.parse import urljoin, urlparse
import os
from typing import Dict, List, Optional, Tuple

class Phase2OrganizationScraper:
    def __init__(self, input_csv_path: str, output_csv_path: str, checkpoint_file: str = "output/phase2_checkpoint.json"):
        """
        Initialize the Phase 2 scraper
        
        Args:
            input_csv_path: Path to Phase 1 CSV file
            output_csv_path: Path to save enhanced CSV
            checkpoint_file: Path to checkpoint file for resume functionality
        """
        self.input_csv_path = input_csv_path
        self.output_csv_path = output_csv_path
        self.checkpoint_file = checkpoint_file
        
        # Retry configuration
        self.retry_delays = [30, 60, 180]  # 30s, 60s, 3min
        
        # Setup logging
        self.setup_logging()
        
        # Load data
        self.organizations_df = pd.read_csv(input_csv_path)
        self.processed_count = 0
        
        # Checkpoint data
        self.checkpoint_data = self.load_checkpoint()
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize enhanced dataframe columns
        self.initialize_enhanced_dataframe()
        
    def setup_logging(self):
        """Setup logging to both file and console"""
        log_filename = f"output/phase2_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Phase 2 scraper initialized. Log file: {log_filename}")
        
    def load_checkpoint(self) -> Dict:
        """Load checkpoint data if exists"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                self.logger.info(f"Loaded checkpoint. Last processed: {checkpoint.get('last_processed_index', 0)}")
                return checkpoint
            except Exception as e:
                self.logger.warning(f"Could not load checkpoint: {e}")
        
        return {'last_processed_index': 0, 'processed_organizations': []}
    
    def save_checkpoint(self, index: int, org_data: Dict):
        """Save checkpoint data"""
        self.checkpoint_data['last_processed_index'] = index
        self.checkpoint_data['processed_organizations'].append(org_data)
        
        try:
            os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.checkpoint_data, f, indent=2)
            self.logger.debug(f"Checkpoint saved at index {index}")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
    
    def initialize_enhanced_dataframe(self):
        """Initialize the enhanced dataframe with new columns"""
        # Add new columns if they don't exist
        new_columns = [
            'github_links',
            'website_links', 
            'social_media_links',
            'location',
            'description',
            'member_count',
            'model_count',
            'dataset_count',
            'last_updated',
            'scrape_status',
            'scrape_timestamp'
        ]
        
        for col in new_columns:
            if col not in self.organizations_df.columns:
                self.organizations_df[col] = None
                
        # Restore processed data from checkpoint
        if self.checkpoint_data.get('processed_organizations'):
            for org_data in self.checkpoint_data['processed_organizations']:
                index = org_data.get('index')
                if index is not None and index < len(self.organizations_df):
                    for key, value in org_data.items():
                        if key != 'index' and key in self.organizations_df.columns:
                            self.organizations_df.at[index, key] = value
    
    def make_request_with_retry(self, url: str) -> Tuple[Optional[requests.Response], str]:
        """
        Make HTTP request with progressive retry delays
        
        Returns:
            Tuple of (response, status_message)
        """
        for attempt, delay in enumerate(self.retry_delays):
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return response, "success"
                elif response.status_code == 429:  # Rate limited
                    self.logger.warning(f"Rate limited on {url}. Waiting {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.RequestException as e:
                self.logger.warning(f"Request failed for {url} (attempt {attempt + 1}): {e}")
                
                if attempt < len(self.retry_delays) - 1:
                    self.logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
        
        return None, "failed_after_retries"
    
    def extract_links_by_pattern(self, soup: BeautifulSoup, patterns: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Extract links based on patterns"""
        results = {}
        
        for link_type, pattern_list in patterns.items():
            found_links = []
            
            # Look for links in href attributes
            for pattern in pattern_list:
                links = soup.find_all('a', href=re.compile(pattern, re.I))
                for link in links:
                    href = link.get('href', '')
                    if href and href not in found_links:
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            href = 'https://huggingface.co' + href
                        found_links.append(href)
            
            results[link_type] = found_links if found_links else ['Null']
        
        return results
    
    def extract_text_content(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract text content using CSS selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return "Null"
    
    def extract_organization_details(self, org_url: str) -> Dict[str, any]:
        """
        Extract detailed information from organization page
        
        Returns:
            Dictionary with extracted information
        """
        self.logger.info(f"Scraping details for: {org_url}")
        
        response, status = self.make_request_with_retry(org_url)
        
        if not response:
            self.logger.error(f"Failed to fetch {org_url}: {status}")
            return {
                'github_links': 'Null',
                'website_links': 'Null',
                'social_media_links': 'Null',
                'location': 'Null',
                'description': 'Null',
                'member_count': 'Null',
                'model_count': 'Null',
                'dataset_count': 'Null',
                'last_updated': 'Null',
                'scrape_status': status,
                'scrape_timestamp': datetime.now().isoformat()
            }
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Define patterns for different types of links
        link_patterns = {
            'github': [r'github\.com', r'gitlab\.com'],
            'website': [r'http[s]?://(?!.*huggingface\.co)(?!.*github\.com)(?!.*twitter\.com)(?!.*linkedin\.com).*'],
            'social_media': [r'twitter\.com', r'linkedin\.com', r'facebook\.com', r'instagram\.com', r'youtube\.com']
        }
        
        # Extract links
        extracted_links = self.extract_links_by_pattern(soup, link_patterns)
        
        # Extract organization details
        try:
            # Description - look for various description elements
            description_selectors = [
                'meta[name="description"]',
                '.organization-description',
                '.prose p',
                'article p:first-of-type'
            ]
            description = self.extract_text_content(soup, description_selectors)
            if description == "Null":
                # Try meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', 'Null') if meta_desc else 'Null'
            
            # Location - look for location information
            location_selectors = [
                '.location',
                '.organization-location',
                '[data-testid="location"]',
                '.prose .location'
            ]
            location = self.extract_text_content(soup, location_selectors)
            
            # Count statistics
            stats = {'member_count': 'Null', 'model_count': 'Null', 'dataset_count': 'Null'}
            
            # Look for counts in various places
            count_elements = soup.find_all(['span', 'div', 'p'], string=re.compile(r'\d+\s*(member|model|dataset)', re.I))
            for elem in count_elements:
                text = elem.get_text().lower()
                numbers = re.findall(r'\d+', text)
                if numbers:
                    if 'member' in text:
                        stats['member_count'] = numbers[0]
                    elif 'model' in text:
                        stats['model_count'] = numbers[0]
                    elif 'dataset' in text:
                        stats['dataset_count'] = numbers[0]
            
            return {
                'github_links': ', '.join(extracted_links['github']),
                'website_links': ', '.join(extracted_links['website']),
                'social_media_links': ', '.join(extracted_links['social_media']),
                'location': location,
                'description': description,
                'member_count': stats['member_count'],
                'model_count': stats['model_count'],
                'dataset_count': stats['dataset_count'],
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'scrape_status': 'success',
                'scrape_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting details from {org_url}: {e}")
            return {
                'github_links': 'Null',
                'website_links': 'Null', 
                'social_media_links': 'Null',
                'location': 'Null',
                'description': 'Null',
                'member_count': 'Null',
                'model_count': 'Null',
                'dataset_count': 'Null',
                'last_updated': 'Null',
                'scrape_status': f'error: {str(e)}',
                'scrape_timestamp': datetime.now().isoformat()
            }
    
    def save_progress(self):
        """Save current progress to CSV"""
        try:
            self.organizations_df.to_csv(self.output_csv_path, index=False)
            self.logger.info(f"Progress saved to {self.output_csv_path}")
        except Exception as e:
            self.logger.error(f"Failed to save progress: {e}")
    
    def run_phase2_scraping(self):
        """Run the Phase 2 scraping process"""
        self.logger.info("Starting Phase 2 scraping...")
        
        total_orgs = len(self.organizations_df)
        start_index = self.checkpoint_data.get('last_processed_index', 0)
        
        self.logger.info(f"Total organizations: {total_orgs}")
        self.logger.info(f"Starting from index: {start_index}")
        
        for index in range(start_index, total_orgs):
            row = self.organizations_df.iloc[index]
            org_name = row['organization_name']
            org_url = row['organization_url']
            
            # Skip if already processed successfully
            if pd.notna(row.get('scrape_status')) and row.get('scrape_status') == 'success':
                self.logger.info(f"Skipping already processed: {org_name}")
                continue
            
            self.logger.info(f"Processing {index + 1}/{total_orgs}: {org_name}")
            
            # Extract details
            details = self.extract_organization_details(org_url)
            
            # Update dataframe
            for key, value in details.items():
                self.organizations_df.at[index, key] = value
            
            # Log results
            status = details.get('scrape_status', 'unknown')
            if status == 'success':
                github = details.get('github_links', 'Null')
                website = details.get('website_links', 'Null') 
                social = details.get('social_media_links', 'Null')
                location = details.get('location', 'Null')
                
                self.logger.info(f"✓ {org_name}: GitHub={github[:50]}{'...' if len(github) > 50 else ''}, "
                               f"Website={website[:50]}{'...' if len(website) > 50 else ''}, "
                               f"Social={social[:50]}{'...' if len(social) > 50 else ''}, "
                               f"Location={location}")
            else:
                self.logger.warning(f"✗ {org_name}: {status}")
                
                if any(field == 'Null' for field in [details.get('github_links'), details.get('website_links'), 
                                                   details.get('social_media_links'), details.get('location')]):
                    self.logger.info("Some fields not findable - marked as Null")
            
            # Save checkpoint and progress
            checkpoint_data = {'index': index, **details}
            self.save_checkpoint(index, checkpoint_data)
            
            # Save progress every 10 organizations
            if (index + 1) % 10 == 0:
                self.save_progress()
                self.logger.info(f"Progress saved. Completed {index + 1}/{total_orgs} organizations")
            
            # Small delay to be respectful
            time.sleep(1)
        
        # Final save
        self.save_progress()
        self.logger.info("Phase 2 scraping completed!")
        self.logger.info(f"Enhanced data saved to: {self.output_csv_path}")


def main():
    """Main function to run Phase 2 scraper"""
    input_csv = "output/huggingface_organizations.csv"
    output_csv = "output/huggingface_organizations_detailed.csv"
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"Error: Input file {input_csv} not found!")
        print("Please run Phase 1 scraper first.")
        return
    
    print("="*80)
    print("HUGGINGFACE ORGANIZATION SCRAPER - PHASE 2")
    print("Extracting detailed organization information...")
    print("="*80)
    
    try:
        scraper = Phase2OrganizationScraper(input_csv, output_csv)
        scraper.run_phase2_scraping()
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user. Progress has been saved.")
        print("You can resume by running the script again.")
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Please check the log file for details.")

if __name__ == "__main__":
    main()