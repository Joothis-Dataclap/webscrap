#!/usr/bin/env python3
"""
Test script to verify link extraction from row 12 onwards
"""

import pandas as pd
from phase2_detail_scraper import Phase2OrganizationScraper
import os

def test_problematic_rows():
    """Test scraping of rows that had missing data (row 12 onwards)"""
    
    input_csv = "output/huggingface_organizations.csv"
    output_csv = "output/huggingface_organizations_detailed.csv"
    
    if not os.path.exists(input_csv):
        print(f"Error: Input file {input_csv} not found!")
        return
    
    print("="*80)
    print("TESTING LINK EXTRACTION FROM ROW 12 ONWARDS")
    print("="*80)
    
    # Read the CSV
    df = pd.read_csv(input_csv)
    
    # Test rows 11-14 (indices for rows 12-15 in UI)
    test_indices = range(11, min(15, len(df)))
    
    scraper = Phase2OrganizationScraper(input_csv, output_csv)
    
    print(f"\nTesting organizations at indices {list(test_indices)}:\n")
    
    for idx in test_indices:
        row = df.iloc[idx]
        org_name = row['organization_name']
        org_url = row['organization_url']
        
        print(f"[Row {idx + 1}] Testing: {org_name}")
        print(f"URL: {org_url}")
        
        try:
            details = scraper.extract_organization_details(org_url)
            
            print(f"  Status: {details.get('scrape_status', 'unknown')}")
            print(f"  GitHub Links: {details.get('github_links', 'Null')[:60]}...")
            print(f"  Website Links: {details.get('website_links', 'Null')[:60]}...")
            print(f"  Social Media: {details.get('social_media_links', 'Null')[:60]}...")
            print(f"  Location: {details.get('location', 'Null')}")
            print()
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            print()

if __name__ == "__main__":
    test_problematic_rows()
