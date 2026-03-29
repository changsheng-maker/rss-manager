"""RSS Feed Discovery Module.

This module provides functionality to auto-discover RSS feeds from any URL
by checking common paths, parsing HTML for feed links, and detecting
CMS-specific patterns.

Example:
    >>> from feed_discovery import FeedDiscovery
    >>> discovery = FeedDiscovery()
    >>> feeds = discovery.discover("https://example.com")
    >>> for feed in feeds:
    ...     print(f"{feed.title}: {feed.url}")
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


@dataclass
class DiscoveredFeed:
    """Represents a discovered RSS feed with metadata.

    Attributes:
        url: The absolute URL of the feed.
        title: Optional title of the feed.
        content_type: Content type (e.g., 'application/rss+xml').
        method: How the feed was discovered ('common_path', 'link_tag', 'cms_pattern').
        confidence: Confidence level (0-1) about the feed validity.
    """
    url: str
    title: Optional[str] = None
    content_type: Optional[str] = None
    method: str = "unknown"
    confidence: float = 0.5


class FeedDiscovery:
    """Auto-discover RSS feeds from websites.

    This class provides multiple strategies for finding RSS feeds:
    1. Checking common RSS feed paths
    2. Parsing HTML <link> tags with rel="alternate"
    3. Detecting CMS-specific patterns (WordPress, Ghost, etc.)

    Attributes:
        timeout: Request timeout in seconds.
        headers: HTTP headers for requests.
        session: Requests session for connection pooling.
    """

    # Common RSS feed paths to check
    COMMON_PATHS = [
        "/feed",
        "/feed.xml",
        "/rss",
        "/rss.xml",
        "/atom.xml",
        "/feeds",
        "/index.xml",
        "/posts.xml",
        "/blog/feed",
        "/blog/rss",
        "/blog/atom.xml",
        "/feed/atom",
        "/feed/rss",
        "/?feed=rss2",
        "/?feed=atom",
        "/feed.rss",
        "/feed.atom",
        "/rss2.xml",
        "/atom",
        "/rss/",
        "/feed/",
        "/feeds/all.atom.xml",
        "/feeds/all.rss.xml",
    ]

    # CMS-specific patterns
    CMS_PATTERNS = {
        "wordpress": {
            "paths": ["/feed", "/?feed=rss2", "/?feed=atom"],
            "indicators": ["/wp-content/", "wordpress", "wp-json"],
        },
        "ghost": {
            "paths": ["/rss/", "/atom.xml"],
            "indicators": ["/ghost/", "content=\"Ghost"],
        },
        "medium": {
            "paths": ["/feed"],
            "indicators": ["medium.com", "data-medium-"],
        },
        "bearblog": {
            "paths": ["/atom.xml", "/rss.xml", "/feed/"],
            "indicators": ["bearblog.dev", "Powered by Bear"],
        },
        "substack": {
            "paths": ["/feed"],
            "indicators": [".substack.com", "substackcdn"],
        },
        "devto": {
            "paths": ["/feed"],
            "indicators": ["dev.to", "DEV Community"],
        },
        "hashnode": {
            "paths": ["/rss.xml"],
            "indicators": ["hashnode.dev", "hashnode.com"],
        },
        "blogger": {
            "paths": ["/feeds/posts/default", "/atom.xml"],
            "indicators": ["blogger.com", "blogspot.com"],
        },
        "tumblr": {
            "paths": ["/rss"],
            "indicators": [".tumblr.com", "tumblr assets"],
        },
        "squarespace": {
            "paths": ["/?format=rss", "/?format=atom"],
            "indicators": ["squarespace.com", "static.squarespace.com"],
        },
        "webflow": {
            "paths": ["/rss.xml"],
            "indicators": ["webflow.io", "webflow.com", "data-wf-"],
        },
        "jekyll": {
            "paths": ["/feed.xml", "/feed.atom"],
            "indicators": ["jekyll", "/assets/"],
        },
        "hugo": {
            "paths": ["/index.xml", "/atom.xml", "/rss.xml"],
            "indicators": ["hugo", "powered by Hugo"],
        },
        "gatsby": {
            "paths": ["/rss.xml", "/atom.xml"],
            "indicators": ["gatsby", "___gatsby"],
        },
        "nextjs": {
            "paths": ["/api/rss", "/rss.xml", "/feed.xml"],
            "indicators": ["__next", "_next/"],
        },
    }

    # Content types that indicate RSS feeds
    FEED_CONTENT_TYPES = [
        "application/rss+xml",
        "application/atom+xml",
        "application/xml",
        "text/xml",
        "application/json",
        "application/feed+json",
    ]

    def __init__(self, timeout: int = 10, user_agent: Optional[str] = None):
        """Initialize the FeedDiscovery instance.

        Args:
            timeout: Request timeout in seconds.
            user_agent: Custom User-Agent string.
        """
        self.timeout = timeout
        self.headers = {
            "User-Agent": user_agent or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "application/rss+xml,application/atom+xml;q=0.8,*/*;q=0.7"
            ),
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by adding scheme if missing.

        Args:
            url: Input URL string.

        Returns:
            Normalized URL with scheme.
        """
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    def _is_feed_content(self, response: requests.Response) -> bool:
        """Check if response contains feed content.

        Args:
            response: HTTP response object.

        Returns:
            True if response appears to be a feed.
        """
        content_type = response.headers.get("Content-Type", "").lower()

        # Check content type header
        for feed_type in self.FEED_CONTENT_TYPES:
            if feed_type in content_type:
                return True

        # Check content body for RSS/Atom markers
        content = response.text[:2000]  # Check first 2KB
        rss_markers = ["<rss", "<feed", "<rdf:RDF", "<?xml", "<channel>", "<opml"]
        if any(marker in content for marker in rss_markers):
            return True

        return False

    def _check_common_paths(self, base_url: str) -> List[DiscoveredFeed]:
        """Check common RSS feed paths.

        Args:
            base_url: Base URL to check.

        Returns:
            List of discovered feeds from common paths.
        """
        feeds = []
        parsed = urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for path in self.COMMON_PATHS:
            try:
                url = urljoin(base, path)
                response = self.session.head(url, timeout=self.timeout, allow_redirects=True)

                if response.status_code == 200:
                    # Try GET request to verify it's a feed
                    response = self.session.get(url, timeout=self.timeout)
                    if response.status_code == 200 and self._is_feed_content(response):
                        content_type = response.headers.get("Content-Type", "")
                        feeds.append(DiscoveredFeed(
                            url=url,
                            content_type=content_type,
                            method="common_path",
                            confidence=0.8
                        ))
            except requests.RequestException:
                continue

        return feeds

    def _parse_html_feed_links(self, url: str, html: str) -> List[DiscoveredFeed]:
        """Parse HTML for feed links in <link> tags.

        Args:
            url: Source URL for resolving relative URLs.
            html: HTML content to parse.

        Returns:
            List of discovered feeds from HTML link tags.
        """
        feeds = []
        soup = BeautifulSoup(html, "html.parser")

        # Find all link tags with rel="alternate" and type indicating a feed
        for link in soup.find_all("link", rel="alternate"):
            link_type = link.get("type", "").lower()
            href = link.get("href")
            title = link.get("title")

            if href and any(t in link_type for t in ["rss", "atom", "feed"]):
                feed_url = urljoin(url, href)
                feeds.append(DiscoveredFeed(
                    url=feed_url,
                    title=title,
                    content_type=link_type,
                    method="link_tag",
                    confidence=0.95
                ))

        return feeds

    def _detect_cms(self, url: str, html: str) -> Optional[str]:
        """Detect CMS from HTML content.

        Args:
            url: Page URL.
            html: HTML content to analyze.

        Returns:
            Detected CMS name or None.
        """
        url_lower = url.lower()
        html_lower = html.lower()

        for cms, patterns in self.CMS_PATTERNS.items():
            # Check URL indicators
            for indicator in patterns["indicators"]:
                if indicator.lower() in url_lower or indicator.lower() in html_lower:
                    return cms

        return None

    def _check_cms_patterns(self, url: str, html: str) -> List[DiscoveredFeed]:
        """Check CMS-specific feed paths.

        Args:
            url: Base URL.
            html: HTML content for CMS detection.

        Returns:
            List of discovered feeds from CMS patterns.
        """
        feeds = []
        cms = self._detect_cms(url, html)

        if cms and cms in self.CMS_PATTERNS:
            parsed = urlparse(url)
            base = f"{parsed.scheme}://{parsed.netloc}"

            for path in self.CMS_PATTERNS[cms]["paths"]:
                try:
                    feed_url = urljoin(base, path)
                    response = self.session.get(feed_url, timeout=self.timeout)

                    if response.status_code == 200 and self._is_feed_content(response):
                        content_type = response.headers.get("Content-Type", "")
                        feeds.append(DiscoveredFeed(
                            url=feed_url,
                            content_type=content_type,
                            method=f"cms_pattern:{cms}",
                            confidence=0.85
                        ))
                except requests.RequestException:
                    continue

        return feeds

    def discover(self, url: str, check_common: bool = True,
                 parse_html: bool = True, check_cms: bool = True) -> List[DiscoveredFeed]:
        """Discover RSS feeds from a URL.

        This is the main method that orchestrates all discovery strategies.

        Args:
            url: Website URL to check.
            check_common: Whether to check common RSS paths.
            parse_html: Whether to parse HTML for feed links.
            check_cms: Whether to check CMS-specific patterns.

        Returns:
            List of discovered feeds sorted by confidence.

        Raises:
            requests.RequestException: If the initial request fails.
        """
        url = self._normalize_url(url)
        feeds: List[DiscoveredFeed] = []
        seen_urls: Set[str] = set()

        # Fetch the main page
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            html = response.text
        except requests.RequestException:
            # If main page fails, still try common paths
            html = ""

        # Parse HTML for link tags (highest confidence)
        if parse_html and html:
            for feed in self._parse_html_feed_links(url, html):
                if feed.url not in seen_urls:
                    feeds.append(feed)
                    seen_urls.add(feed.url)

        # Check CMS-specific patterns
        if check_cms:
            for feed in self._check_cms_patterns(url, html):
                if feed.url not in seen_urls:
                    feeds.append(feed)
                    seen_urls.add(feed.url)

        # Check common paths (lowest priority)
        if check_common:
            for feed in self._check_common_paths(url):
                if feed.url not in seen_urls:
                    feeds.append(feed)
                    seen_urls.add(feed.url)

        # Sort by confidence (highest first)
        feeds.sort(key=lambda f: f.confidence, reverse=True)

        return feeds

    def discover_single(self, url: str, min_confidence: float = 0.5) -> Optional[DiscoveredFeed]:
        """Discover a single best feed from a URL.

        Args:
            url: Website URL to check.
            min_confidence: Minimum confidence threshold.

        Returns:
            Best discovered feed or None.
        """
        feeds = self.discover(url)
        for feed in feeds:
            if feed.confidence >= min_confidence:
                return feed
        return feeds[0] if feeds else None

    def validate_feed(self, url: str) -> bool:
        """Validate if a URL is a valid feed.

        Args:
            url: Feed URL to validate.

        Returns:
            True if URL returns valid feed content.
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            return response.status_code == 200 and self._is_feed_content(response)
        except requests.RequestException:
            return False
