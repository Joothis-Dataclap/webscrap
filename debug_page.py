"""
Debug script to test page 1047 organization parsing
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_page_1047():
    url = "https://huggingface.co/organizations?p=1047"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    
    response = session.get(url, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    print(f"=== DEBUG: Page 1047 ===")
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    
    # Find all links
    all_links = soup.find_all('a', href=True)
    print(f"Total links found: {len(all_links)}")
    
    # Current filtering logic
    org_candidates = []
    for link in all_links:
        href = link.get('href', '')
        
        # Filter for organization profile links
        if (href.startswith('/') and 
            href.count('/') == 1 and 
            len(href) > 1 and
            not href.startswith('/#') and
            href not in ['/models', '/datasets', '/spaces', '/docs', '/pricing', 
                        '/terms-of-service', '/privacy', '/users', '/login',
                        '/join', '/settings', '/new', '/organizations']):
            
            link_text = link.get_text(strip=True)
            org_candidates.append((href, link_text))
    
    print(f"\nOrg candidates (before 'followers' filter): {len(org_candidates)}")
    for href, text in org_candidates[:10]:  # Show first 10
        print(f"  {href} -> {text[:100]}...")
    
    # Apply current 'followers' filter
    organizations_current = []
    for href, link_text in org_candidates:
        if 'followers' in link_text.lower():
            organizations_current.append((href, link_text))
    
    print(f"\nOrganizations with 'followers' filter: {len(organizations_current)}")
    
    # Try alternative approach - look for different patterns
    organizations_alt = []
    for href, link_text in org_candidates:
        # Alternative patterns that might indicate organization
        if any(pattern in link_text.lower() for pattern in [
            'follower', 'company', 'university', 'non-profit', 'team', 'enterprise'
        ]):
            organizations_alt.append((href, link_text))
    
    print(f"Organizations with alternative patterns: {len(organizations_alt)}")
    
    # Show some examples
    if organizations_alt:
        print("\nFirst 10 organizations found:")
        for i, (href, text) in enumerate(organizations_alt[:10]):
            print(f"{i+1}. {href} -> {text}")

if __name__ == "__main__":
    debug_page_1047()