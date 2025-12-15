#!/usr/bin/env python3
"""
Run the complete Phase 2 scraping process
"""

import os
from phase2_detail_scraper import main

def run_full_phase2():
    """Run the full Phase 2 scraping on all organizations"""
    print("\n" + "="*80)
    print("HUGGINGFACE ORGANIZATION SCRAPER - PHASE 2 (FULL)")
    print("Extracting detailed information for ALL organizations...")
    print("="*80)
    print()
    
    # Check if Phase 1 data exists
    if not os.path.exists("output/huggingface_organizations.csv"):
        print("❌ Error: Phase 1 data not found!")
        print("Please run 'python hf_org_scraper.py' first to complete Phase 1.")
        return
    
    print("✅ Phase 1 data found")
    print("🚀 Starting Phase 2...")
    print()
    
    print("📋 FEATURES:")
    print("   • Extracts GitHub links, website links, social media links")
    print("   • Finds company location and description")
    print("   • Counts members, models, datasets")
    print("   • Progressive retry logic (30s → 60s → 3min)")
    print("   • Checkpoint system for resume capability")
    print("   • Continuous logging to file")
    print("   • Handles missing data gracefully")
    print()
    
    input("Press Enter to start Phase 2 scraping...")
    
    # Run the main scraper
    main()

if __name__ == "__main__":
    run_full_phase2()