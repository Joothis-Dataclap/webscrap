# Web Scraping with Firecrawl

This project is set up for web scraping using Python and Firecrawl.

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
- Copy `.env.example` to `.env`
- Add your Firecrawl API key to the `.env` file:
  ```
  FIRECRAWL_API_KEY=your_actual_api_key_here
  ```

Get your API key from: https://www.firecrawl.dev/

## Project Structure
```
webscrap/
├── venv/                    # Virtual environment
├── src/                     # Source code
│   ├── __init__.py
│   └── scraper.py          # Main scraping logic
├── output/                 # Output data directory
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── requirements.txt        # Project dependencies
└── README.md              # This file
```

## Usage

### Basic Scraping Example
```python
from src.scraper import FirecrawlScraper
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('FIRECRAWL_API_KEY')

scraper = FirecrawlScraper(api_key)
result = scraper.scrape_url('https://example.com')
print(result)
```

## Features
- Firecrawl integration for intelligent web scraping
- Environment variable configuration
- Modular scraper class
- Output directory for saving results

## Notes
- Always respect robots.txt and website terms of service
- Use appropriate delays between requests
- Handle errors gracefully
"# webscrap" 
