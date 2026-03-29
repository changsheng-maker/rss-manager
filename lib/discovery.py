"""RSS feed discovery module."""
import re
import urllib.parse
from typing import Optional
from xml.etree import ElementTree as ET

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    requests = None
    BeautifulSoup = None


def fetch_url(url: str, timeout: int = 10):
    """Fetch a URL with proper headers."""
    if not HAS_DEPS:
        return None
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response
    except Exception:
        return None


def parse_feed(content: str) -> Optional[dict]:
    """Parse feed content to extract metadata."""
    try:
        root = ET.fromstring(content)
        ns = {"atom": "http://www.w3.org/2005/Atom", "rss": "http://purl.org/rss/1.0/"}

        feed_type = None
        title = None
        description = None

        # Check for Atom
        if root.tag.endswith("feed"):
            feed_type = "Atom"
            title_elem = root.find("atom:title", ns) or root.find("title")
            if title_elem is not None:
                title = title_elem.text
            desc_elem = root.find("atom:subtitle", ns) or root.find("subtitle")
            if desc_elem is not None:
                description = desc_elem.text

        # Check for RSS
        elif root.tag == "rss" or root.tag.endswith("RDF"):
            feed_type = "RSS"
            channel = root.find("channel")
            if channel is not None:
                title_elem = channel.find("title")
                if title_elem is not None:
                    title = title_elem.text
                desc_elem = channel.find("description")
                if desc_elem is not None:
                    description = desc_elem.text

        if title:
            return {
                "type": feed_type,
                "title": title.strip() if title else "Untitled",
                "description": description.strip() if description else ""
            }
    except ET.ParseError:
        pass
    return None


def discover_feeds_in_html(url: str, html_content: str) -> list:
    """Discover RSS/Atom feeds in HTML content."""
    if not HAS_DEPS:
        return []
    feeds = []
    soup = BeautifulSoup(html_content, "html.parser")

    # Look for link tags
    feed_types = [
        ("application/rss+xml", "RSS"),
        ("application/atom+xml", "Atom"),
        ("application/feed+json", "JSON Feed"),
        ("application/rdf+xml", "RDF"),
        ("text/xml", "XML"),
        ("application/xml", "XML"),
    ]

    base_url = url
    base_tag = soup.find("base", href=True)
    if base_tag:
        base_url = urllib.parse.urljoin(url, base_tag["href"])

    for mime_type, feed_type in feed_types:
        links = soup.find_all("link", rel="alternate", type=mime_type)
        for link in links:
            href = link.get("href")
            title = link.get("title", "Untitled")
            if href:
                absolute_url = urllib.parse.urljoin(base_url, href)
                feeds.append({
                    "url": absolute_url,
                    "title": title.strip() if title else "Untitled",
                    "type": feed_type
                })

    # Remove duplicates
    seen = set()
    unique_feeds = []
    for feed in feeds:
        if feed["url"] not in seen:
            seen.add(feed["url"])
            unique_feeds.append(feed)

    return unique_feeds


def discover_feeds(url: str, verbose: bool = False) -> dict:
    """Discover RSS feeds from a URL."""
    if not HAS_DEPS:
        return {"success": False, "error": "Missing dependencies: pip install requests beautifulsoup4", "feeds": []}

    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # First, try if the URL is directly a feed
    response = fetch_url(url)
    if response is None:
        return {"success": False, "error": "Failed to fetch URL", "feeds": []}

    content_type = response.headers.get("content-type", "").lower()

    # Check if it's a feed directly
    if any(x in content_type for x in ["xml", "atom", "rss", "feed"]):
        feed_info = parse_feed(response.text)
        if feed_info:
            return {
                "success": True,
                "feeds": [{
                    "url": url,
                    "title": feed_info.get("title", "Untitled"),
                    "type": feed_info.get("type", "Unknown"),
                    "description": feed_info.get("description", "")
                }]
            }

    # Discover feeds in HTML
    feeds = discover_feeds_in_html(url, response.text)

    # Validate discovered feeds
    valid_feeds = []
    for feed in feeds:
        if verbose:
            print(f"Validating: {feed['url']}")
        feed_response = fetch_url(feed["url"], timeout=5)
        if feed_response:
            feed_info = parse_feed(feed_response.text)
            if feed_info:
                feed["title"] = feed_info.get("title") or feed["title"]
                feed["description"] = feed_info.get("description", "")
                feed["type"] = feed_info.get("type", feed["type"])
            valid_feeds.append(feed)

    if valid_feeds:
        return {"success": True, "feeds": valid_feeds}

    # Common feed patterns to try
    common_paths = ["/feed", "/rss", "/atom.xml", "/feed.xml", "/index.xml", "/rss.xml"]
    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    for path in common_paths:
        test_url = base + path
        if verbose:
            print(f"Trying common path: {test_url}")
        feed_response = fetch_url(test_url, timeout=5)
        if feed_response:
            feed_info = parse_feed(feed_response.text)
            if feed_info:
                valid_feeds.append({
                    "url": test_url,
                    "title": feed_info.get("title", "Untitled"),
                    "type": feed_info.get("type", "Unknown"),
                    "description": feed_info.get("description", "")
                })

    if valid_feeds:
        return {"success": True, "feeds": valid_feeds}

    return {"success": False, "error": "No feeds found", "feeds": []}
