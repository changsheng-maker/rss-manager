"""RSS/Atom/JSON Feed Parser Module.

This module provides functionality to parse RSS, Atom, and JSON feeds using
feedparser library. It extracts feed metadata, entries, and dates with proper
error handling.

Example:
    >>> from feed_parser import FeedParser
    >>> parser = FeedParser()
    >>> feed = parser.parse("https://example.com/feed.xml")
    >>> print(feed.title)
    >>> for entry in feed.entries:
    ...     print(entry.title, entry.published)
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import feedparser
import requests


@dataclass
class FeedEntry:
    """Represents a single feed entry (article/post).

    Attributes:
        title: Entry title.
        link: URL to the full content.
        id: Unique identifier for the entry.
        published: Published datetime.
        updated: Last updated datetime.
        summary: Brief summary or description.
        content: Full content if available.
        author: Author name.
        author_email: Author email.
        tags: List of tags/categories.
        enclosures: List of media enclosures (podcasts, images, etc.).
    """
    title: str = ""
    link: str = ""
    id: str = ""
    published: Optional[datetime] = None
    updated: Optional[datetime] = None
    summary: str = ""
    content: str = ""
    author: str = ""
    author_email: str = ""
    tags: List[str] = field(default_factory=list)
    enclosures: List[Dict[str, Any]] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"FeedEntry(title={self.title!r}, published={self.published})"


@dataclass
class ParsedFeed:
    """Represents a parsed feed with all metadata and entries.

    Attributes:
        title: Feed title.
        link: URL to the source website.
        description: Feed description/subtitle.
        language: Feed language code.
        updated: Last update datetime.
        published: Published datetime.
        entries: List of feed entries.
        feed_url: The feed URL that was parsed.
        version: Feed format version (rss20, atom10, etc.).
        image: Feed image/logo URL.
        author: Feed author/creator.
        rights: Copyright/rights information.
    """
    title: str = ""
    link: str = ""
    description: str = ""
    language: str = ""
    updated: Optional[datetime] = None
    published: Optional[datetime] = None
    entries: List[FeedEntry] = field(default_factory=list)
    feed_url: str = ""
    version: str = ""
    image: str = ""
    author: str = ""
    rights: str = ""

    @property
    def entry_count(self) -> int:
        """Return the number of entries in the feed."""
        return len(self.entries)

    def __repr__(self) -> str:
        return f"ParsedFeed(title={self.title!r}, entries={self.entry_count})"


class FeedParseError(Exception):
    """Exception raised when feed parsing fails."""
    pass


class FeedParser:
    """Parse RSS, Atom, and JSON feeds.

    This class provides methods to parse various feed formats and extract
    structured data with proper error handling.

    Attributes:
        timeout: Request timeout in seconds.
        user_agent: User-Agent string for HTTP requests.
        session: Requests session for connection pooling.
    """

    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        """Initialize the FeedParser instance.

        Args:
            timeout: Request timeout in seconds.
            user_agent: Custom User-Agent string.
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object.

        Args:
            date_string: Date string in various formats.

        Returns:
            datetime object or None if parsing fails.
        """
        if not date_string:
            return None

        # feedparser returns time.struct_time, convert to datetime
        try:
            parsed = feedparser._parse_date(date_string)
            if parsed:
                return datetime.fromtimestamp(time.mktime(parsed))
        except (ValueError, TypeError):
            pass

        return None

    def _get_entry_content(self, entry: Dict[str, Any]) -> str:
        """Extract full content from an entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            Full content string or empty string.
        """
        # Try content field first (Atom format)
        if "content" in entry and entry["content"]:
            for content in entry["content"]:
                if content.get("value"):
                    return content["value"]

        # Try content_encoded (RSS with content:encoded)
        if "content_encoded" in entry:
            return entry["content_encoded"]

        return ""

    def _get_summary(self, entry: Dict[str, Any]) -> str:
        """Extract summary/description from an entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            Summary string or empty string.
        """
        # Try various common fields
        for field in ["summary", "summary_detail", "description"]:
            if field in entry:
                if isinstance(entry[field], dict):
                    return entry[field].get("value", "")
                elif isinstance(entry[field], str):
                    return entry[field]
        return ""

    def _parse_entry(self, entry: Dict[str, Any]) -> FeedEntry:
        """Parse a single feed entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            FeedEntry object.
        """
        # Get tags
        tags = []
        if "tags" in entry:
            tags = [tag.get("term", "") for tag in entry["tags"]]

        # Get enclosures
        enclosures = []
        if "enclosures" in entry:
            for enc in entry["enclosures"]:
                enclosures.append(dict(enc))
        elif "links" in entry:
            for link in entry["links"]:
                if link.get("rel") == "enclosure":
                    enclosures.append({
                        "url": link.get("href", ""),
                        "type": link.get("type", ""),
                        "length": link.get("length", 0),
                    })

        # Get published date
        published = None
        if "published_parsed" in entry and entry["published_parsed"]:
            try:
                published = datetime.fromtimestamp(
                    time.mktime(entry["published_parsed"])
                )
            except (ValueError, TypeError):
                pass
        if not published and "published" in entry:
            published = self._parse_date(entry["published"])

        # Get updated date
        updated = None
        if "updated_parsed" in entry and entry["updated_parsed"]:
            try:
                updated = datetime.fromtimestamp(
                    time.mktime(entry["updated_parsed"])
                )
            except (ValueError, TypeError):
                pass
        if not updated and "updated" in entry:
            updated = self._parse_date(entry["updated"])

        # Get author
        author = ""
        if "author" in entry:
            author = entry["author"]
        elif "author_detail" in entry:
            author = entry["author_detail"].get("name", "")

        return FeedEntry(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            id=entry.get("id", entry.get("guid", "")),
            published=published,
            updated=updated,
            summary=self._get_summary(entry),
            content=self._get_entry_content(entry),
            author=author,
            author_email=entry.get("author_detail", {}).get("email", "")
            if "author_detail" in entry else "",
            tags=tags,
            enclosures=enclosures,
        )

    def _parse_feed(self, parsed: Dict[str, Any], feed_url: str) -> ParsedFeed:
        """Parse feed structure from feedparser result.

        Args:
            parsed: feedparser.parse result dict.
            feed_url: Original feed URL.

        Returns:
            ParsedFeed object.
        """
        feed = parsed.get("feed", {})

        # Get feed image
        image = ""
        if "image" in feed:
            if isinstance(feed["image"], dict):
                image = feed["image"].get("href", "")
            else:
                image = str(feed["image"])

        # Get feed author
        author = ""
        if "author" in feed:
            author = feed["author"]
        elif "author_detail" in feed:
            author = feed["author_detail"].get("name", "")

        # Get updated date
        updated = None
        if "updated_parsed" in feed and feed["updated_parsed"]:
            try:
                updated = datetime.fromtimestamp(
                    time.mktime(feed["updated_parsed"])
                )
            except (ValueError, TypeError):
                pass

        # Get published date
        published = None
        if "published_parsed" in feed and feed["published_parsed"]:
            try:
                published = datetime.fromtimestamp(
                    time.mktime(feed["published_parsed"])
                )
            except (ValueError, TypeError):
                pass

        # Parse entries
        entries = [self._parse_entry(entry) for entry in parsed.get("entries", [])]

        return ParsedFeed(
            title=feed.get("title", ""),
            link=feed.get("link", ""),
            description=feed.get("subtitle", feed.get("description", "")),
            language=feed.get("language", ""),
            updated=updated,
            published=published,
            entries=entries,
            feed_url=feed_url,
            version=parsed.get("version", ""),
            image=image,
            author=author,
            rights=feed.get("rights", feed.get("copyright", "")),
        )

    def _parse_json_feed(self, data: Dict[str, Any], feed_url: str) -> ParsedFeed:
        """Parse JSON Feed format.

        Args:
            data: Parsed JSON data.
            feed_url: Original feed URL.

        Returns:
            ParsedFeed object.
        """
        # Parse JSON Feed items
        entries = []
        for item in data.get("items", []):
            # Parse date
            published = None
            if "date_published" in item:
                try:
                    published = datetime.fromisoformat(
                        item["date_published"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            updated = None
            if "date_modified" in item:
                try:
                    updated = datetime.fromisoformat(
                        item["date_modified"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            # Get content
            content = item.get("content_html", item.get("content_text", ""))

            # Get author
            author = ""
            if "author" in item and isinstance(item["author"], dict):
                author = item["author"].get("name", "")

            entry = FeedEntry(
                title=item.get("title", ""),
                link=item.get("url", ""),
                id=item.get("id", item.get("url", "")),
                published=published,
                updated=updated,
                summary=item.get("summary", ""),
                content=content,
                author=author,
                tags=item.get("tags", []),
                enclosures=item.get("attachments", []),
            )
            entries.append(entry)

        # Get feed author
        author = ""
        if "author" in data and isinstance(data["author"], dict):
            author = data["author"].get("name", "")

        # Get icon/image
        image = data.get("icon", data.get("favicon", ""))

        return ParsedFeed(
            title=data.get("title", ""),
            link=data.get("home_page_url", ""),
            description=data.get("description", ""),
            language="",
            updated=datetime.now(),
            entries=entries,
            feed_url=feed_url,
            version="json1",
            image=image,
            author=author,
        )

    def parse(self, url: str) -> ParsedFeed:
        """Parse a feed from URL.

        Args:
            url: URL of the RSS/Atom/JSON feed.

        Returns:
            ParsedFeed object with all metadata and entries.

        Raises:
            FeedParseError: If parsing fails.
        """
        try:
            # Fetch the feed content
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Check if it's JSON Feed
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" in content_type:
                try:
                    data = response.json()
                    if "version" in data and "jsonfeed" in data["version"].lower():
                        return self._parse_json_feed(data, url)
                except json.JSONDecodeError:
                    pass

            # Use feedparser for RSS/Atom
            parsed = feedparser.parse(response.content)

            if parsed.get("bozo"):
                # Warning: may be malformed but still parsable
                pass

            if not parsed.get("feed"):
                raise FeedParseError(f"No feed found at {url}")

            return self._parse_feed(parsed, url)

        except requests.RequestException as e:
            raise FeedParseError(f"Failed to fetch feed: {e}")
        except Exception as e:
            raise FeedParseError(f"Failed to parse feed: {e}")

    def parse_file(self, filepath: str) -> ParsedFeed:
        """Parse a feed from a local file.

        Args:
            filepath: Path to the feed file.

        Returns:
            ParsedFeed object with all metadata and entries.

        Raises:
            FeedParseError: If parsing fails.
            FileNotFoundError: If file doesn't exist.
        """
        try:
            with open(filepath, "rb") as f:
                content = f.read()

            # Check if it's JSON
            try:
                data = json.loads(content)
                if "version" in data and "jsonfeed" in data["version"].lower():
                    return self._parse_json_feed(data, filepath)
            except json.JSONDecodeError:
                pass

            # Use feedparser
            parsed = feedparser.parse(content)

            if not parsed.get("feed"):
                raise FeedParseError(f"No feed found in {filepath}")

            return self._parse_feed(parsed, filepath)

        except Exception as e:
            raise FeedParseError(f"Failed to parse file: {e}")

    def parse_string(self, content: str, content_type: str = "") -> ParsedFeed:
        """Parse a feed from a string.

        Args:
            content: Feed content as string.
            content_type: Optional content type hint.

        Returns:
            ParsedFeed object with all metadata and entries.

        Raises:
            FeedParseError: If parsing fails.
        """
        try:
            # Check if it's JSON
            if "json" in content_type.lower() or content.strip().startswith("{"):
                try:
                    data = json.loads(content)
                    if "version" in data and "jsonfeed" in data["version"].lower():
                        return self._parse_json_feed(data, "string://")
                except json.JSONDecodeError:
                    pass

            # Use feedparser
            parsed = feedparser.parse(content)

            if not parsed.get("feed"):
                raise FeedParseError("No feed found in content")

            return self._parse_feed(parsed, "string://")

        except Exception as e:
            raise FeedParseError(f"Failed to parse content: {e}")

    def get_latest_entries(self, url: str, count: int = 10) -> List[FeedEntry]:
        """Get the latest N entries from a feed.

        Args:
            url: Feed URL.
            count: Number of entries to return.

        Returns:
            List of FeedEntry objects sorted by date (newest first).
        """
        feed = self.parse(url)

        # Sort entries by published date (newest first)
        sorted_entries = sorted(
            feed.entries,
            key=lambda e: e.published or datetime.min,
            reverse=True
        )

        return sorted_entries[:count]

    def get_feed_info(self, url: str) -> Dict[str, Any]:
        """Get basic feed information.

        Args:
            url: Feed URL.

        Returns:
            Dictionary with feed metadata.
        """
        feed = self.parse(url)
        return {
            "title": feed.title,
            "link": feed.link,
            "description": feed.description,
            "entry_count": feed.entry_count,
            "language": feed.language,
            "author": feed.author,
            "version": feed.version,
        }
