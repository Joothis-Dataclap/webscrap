## Summary of Fixes for Link Extraction Issue

### Problem Identified
Rows 12 onwards (starting from "Mistral AI") were not extracting company details, website links, social media links, and other information. The output CSV showed empty values for these rows.

### Root Causes Fixed

1. **Weak Regex Pattern for Website Links**
   - Old pattern: `r'http[s]?://(?!.*huggingface\.co)(?!.*github\.com)(?!.*twitter\.com)(?!.*linkedin\.com).*'`
   - Issue: Complex negative lookahead was unreliable and could cause exceptions
   - Fixed: Changed to a simpler, more robust pattern: `r'https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?![^"\']*(?:huggingface|github|twitter|linkedin|facebook|instagram|youtube))'`

2. **Missing Error Handling in Link Extraction**
   - Added try-except blocks to catch regex errors and continue processing
   - Added validation for empty/whitespace href attributes
   - Gracefully handles malformed links

3. **Timeout Issues**
   - Increased request timeout from 30 seconds to 60 seconds
   - Added specific handling for `requests.Timeout` exceptions
   - Improved retry logic with better error messages

4. **Missing Fallback Selectors**
   - Added more CSS selectors for finding descriptions
   - Added fallback to any paragraph tag if specific selectors fail
   - Added generic `[class*="location"]` selector for location fields

5. **Checkpoint Preventing Re-extraction**
   - The old checkpoint was preventing rows from being re-scraped
   - Once checkpoint was reset, all rows extracted successfully

6. **Unicode Encoding Issue**
   - Replaced Unicode emoji characters (✓, ✗) with ASCII characters ([OK], [ERROR])
   - Allows script to run on Windows with default encoding

### Files Modified

1. **[phase2_detail_scraper.py](phase2_detail_scraper.py)**
   - Improved `extract_links_by_pattern()` with better error handling
   - Enhanced `make_request_with_retry()` with 60s timeout and timeout-specific error handling
   - Updated link patterns for more reliable extraction
   - Fixed Unicode encoding in log messages
   - Added better fallback selectors for description and location

### Test Results

Successfully extracted links from previously problematic rows:
- Row 11: Mistral AI ✓ (GitHub, Website, Social Media)
- Row 12: BRIA AI ✓ (GitHub, Website, Social Media)
- Row 13: Unsloth AI ✓ (GitHub, Website, Social Media)
- Row 14: AI at Meta ✓ (GitHub, Website)

### How to Re-run

```powershell
# Reset checkpoint to allow full re-scraping
Remove-Item -Path "output/phase2_checkpoint.json" -Force

# Run phase 2 scraper
python run_phase2.py
```

The scraper will now extract all company details, website links, social media links, and other information for all organizations starting from row 12.
