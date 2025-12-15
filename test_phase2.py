#!/usr/bin/env python3
"""
Test script for Phase 2 scraper - tests with a small sample
"""

import pandas as pd
import os

def create_test_csv():
    """Create a small test CSV for Phase 2 testing"""
    test_data = [
        {
            'organization_name': 'Hugging Face',
            'organization_url': 'https://huggingface.co/huggingface',
            'page_number': 0
        },
        {
            'organization_name': 'Meta Llama',
            'organization_url': 'https://huggingface.co/meta-llama',
            'page_number': 0
        },
        {
            'organization_name': 'NVIDIA',
            'organization_url': 'https://huggingface.co/nvidia',
            'page_number': 0
        }
    ]
    
    df = pd.DataFrame(test_data)
    test_file = "output/test_organizations.csv"
    
    os.makedirs("output", exist_ok=True)
    df.to_csv(test_file, index=False)
    print(f"Test CSV created: {test_file}")
    return test_file

def run_test():
    """Run Phase 2 scraper with test data"""
    from phase2_detail_scraper import Phase2OrganizationScraper
    
    input_csv = create_test_csv()
    output_csv = "output/test_organizations_detailed.csv"
    
    print("\n" + "="*60)
    print("TESTING PHASE 2 SCRAPER")
    print("="*60)
    
    scraper = Phase2OrganizationScraper(input_csv, output_csv, "output/test_checkpoint.json")
    scraper.run_phase2_scraping()
    
    print("\n" + "="*60)
    print("TEST COMPLETED!")
    print(f"Results saved to: {output_csv}")
    print("="*60)

if __name__ == "__main__":
    run_test()