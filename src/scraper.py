"""Firecrawl-based web scraper."""

from firecrawl import FirecrawlApp
import json
import os
from pathlib import Path


class FirecrawlScraper:
    """A web scraper using Firecrawl API."""
    
    def __init__(self, api_key):
        """Initialize the scraper with Firecrawl API key.
        
        Args:
            api_key (str): Firecrawl API key
        """
        self.app = FirecrawlApp(api_key=api_key)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def scrape_url(self, url, **kwargs):
        """Scrape a single URL using Firecrawl.
        
        Args:
            url (str): URL to scrape
            **kwargs: Additional parameters to pass to Firecrawl
            
        Returns:
            dict: Scraped content from Firecrawl
        """
        try:
            print(f"Scraping: {url}")
            result = self.app.scrape_url(url, **kwargs)
            print(f"Successfully scraped: {url}")
            return result
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def scrape_urls(self, urls, **kwargs):
        """Scrape multiple URLs.
        
        Args:
            urls (list): List of URLs to scrape
            **kwargs: Additional parameters for scraping
            
        Returns:
            list: List of scraping results
        """
        results = []
        for url in urls:
            result = self.scrape_url(url, **kwargs)
            if result:
                results.append(result)
        return results
    
    def save_result(self, result, filename):
        """Save scraping result to a JSON file.
        
        Args:
            result (dict): Scraping result to save
            filename (str): Output filename
        """
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Result saved to: {output_path}")
    
    def scrape_and_save(self, url, output_filename=None, **kwargs):
        """Scrape a URL and save the result.
        
        Args:
            url (str): URL to scrape
            output_filename (str, optional): Custom output filename
            **kwargs: Additional parameters for scraping
            
        Returns:
            dict: Scraping result
        """
        result = self.scrape_url(url, **kwargs)
        
        if result:
            if output_filename is None:
                output_filename = f"scraped_{hash(url)}.json"
            self.save_result(result, output_filename)
        
        return result


def main():
    """Example usage of FirecrawlScraper."""
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('FIRECRAWL_API_KEY')
    
    if not api_key:
        print("Error: FIRECRAWL_API_KEY not found in .env file")
        return
    
    scraper = FirecrawlScraper(api_key)
    
    # Example: Scrape a URL
    url = "https://example.com"
    result = scraper.scrape_url(url)
    
    if result:
        print("\nScrape Result:")
        print(json.dumps(result, indent=2)[:500])  # Print first 500 chars


if __name__ == "__main__":
    main()
