"""OPML Import/Export Module.

This module provides functionality to parse OPML (Outline Processor Markup Language)
files commonly used for RSS feed lists, and to generate OPML files from feed lists.
It supports nested categories and standard OPML 2.0 format.

Example:
    >>> from opml import OPMLManager
    >>> # Parse an OPML file
    >>> manager = OPMLManager()
    >>> feeds = manager.parse("feeds.opml")
    >>> # Generate OPML from feed list
    >>> opml_content = manager.generate(feeds, title="My Feeds")
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import re


@dataclass
class OPMLFeed:
    """Represents a feed in an OPML file.

    Attributes:
        title: Feed title.
        xml_url: Feed URL (xmlUrl attribute).
        html_url: Website URL (htmlUrl attribute).
        description: Feed description.
        language: Feed language.
        version: Feed type (RSS, Atom, etc.).
        category: Category path (for nested categories, use '/').
        custom_attrs: Additional custom attributes.
    """
    title: str = ""
    xml_url: str = ""
    html_url: str = ""
    description: str = ""
    language: str = ""
    version: str = ""
    category: str = ""
    custom_attrs: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"OPMLFeed(title={self.title!r}, xml_url={self.xml_url!r})"


@dataclass
class OPMLCategory:
    """Represents a category in an OPML outline.

    Attributes:
        title: Category title.
        feeds: List of feeds in this category.
        categories: List of nested sub-categories.
    """
    title: str = ""
    feeds: List[OPMLFeed] = field(default_factory=list)
    categories: List["OPMLCategory"] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"OPMLCategory(title={self.title!r}, feeds={len(self.feeds)}, subcategories={len(self.categories)})"

    def add_feed(self, feed: OPMLFeed) -> None:
        """Add a feed to this category."""
        self.feeds.append(feed)

    def add_category(self, category: "OPMLCategory") -> None:
        """Add a sub-category."""
        self.categories.append(category)


@dataclass
class OPMLDocument:
    """Represents a complete OPML document.

    Attributes:
        title: Document title.
        date_created: Creation date.
        date_modified: Last modification date.
        owner_name: Owner/creator name.
        owner_email: Owner email.
        owner_id: Owner ID/URL.
        docs: URL to OPML documentation.
        expansion_state: Comma-separated list of expanded node IDs.
        vert_scroll_state: Vertical scroll position.
        window_top: Window position (top).
        window_left: Window position (left).
        window_bottom: Window position (bottom).
        window_right: Window position (right).
        feeds: List of top-level feeds (not in categories).
        categories: List of top-level categories.
    """
    title: str = "Subscriptions"
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    owner_name: str = ""
    owner_email: str = ""
    owner_id: str = ""
    docs: str = "http://dev.opml.org/spec2.html"
    expansion_state: str = ""
    vert_scroll_state: int = 0
    window_top: int = 0
    window_left: int = 0
    window_bottom: int = 0
    window_right: int = 0
    feeds: List[OPMLFeed] = field(default_factory=list)
    categories: List[OPMLCategory] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"OPMLDocument(title={self.title!r}, feeds={len(self.feeds)}, categories={len(self.categories)})"

    def get_all_feeds(self) -> List[OPMLFeed]:
        """Get all feeds including those in categories."""
        all_feeds = list(self.feeds)

        def collect_from_category(cat: OPMLCategory) -> None:
            all_feeds.extend(cat.feeds)
            for subcat in cat.categories:
                collect_from_category(subcat)

        for category in self.categories:
            collect_from_category(category)

        return all_feeds


class OPMLParseError(Exception):
    """Exception raised when OPML parsing fails."""
    pass


class OPMLManager:
    """Manage OPML files for RSS feed import/export.

    This class provides methods to parse OPML files and generate OPML content
    from feed lists. It supports nested categories and standard OPML 2.0 format.

    Attributes:
        default_title: Default title for generated OPML documents.
    """

    # Feed type mapping
    FEED_TYPES = {
        "rss": "rss",
        "atom": "atom",
        "rdf": "rdf",
        "json": "json",
        "feed": "rss",
    }

    def __init__(self, default_title: str = "My RSS Feeds"):
        """Initialize the OPMLManager instance.

        Args:
            default_title: Default title for generated OPML documents.
        """
        self.default_title = default_title

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse RFC 822 date string to datetime.

        Args:
            date_str: RFC 822 formatted date string.

        Returns:
            datetime object or None.
        """
        if not date_str:
            return None

        # Try various common formats
        formats = [
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _format_date(self, dt: Optional[datetime]) -> str:
        """Format datetime to RFC 822 string.

        Args:
            dt: datetime object.

        Returns:
            RFC 822 formatted date string.
        """
        if not dt:
            return ""
        return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _parse_outline(
        self,
        element: ET.Element,
        parent_category: Optional[OPMLCategory] = None
    ) -> Union[OPMLFeed, OPMLCategory, None]:
        """Parse an outline element recursively.

        Args:
            element: XML outline element.
            parent_category: Parent category for nested structure.

        Returns:
            OPMLFeed, OPMLCategory, or None.
        """
        # Get attributes
        attrs = element.attrib
        text = attrs.get("text", "")
        title = attrs.get("title", text)
        xml_url = attrs.get("xmlUrl", "")
        html_url = attrs.get("htmlUrl", "")
        feed_type = attrs.get("type", "")
        description = attrs.get("description", "")
        language = attrs.get("language", "")
        version = attrs.get("version", "")

        # Collect custom attributes
        standard_attrs = {
            "text", "title", "xmlUrl", "htmlUrl", "type",
            "description", "language", "version"
        }
        custom_attrs = {k: v for k, v in attrs.items() if k not in standard_attrs}

        # Check if this is a feed (has xmlUrl) or a category
        if xml_url:
            # This is a feed
            return OPMLFeed(
                title=title,
                xml_url=xml_url,
                html_url=html_url,
                description=description,
                language=language,
                version=version or feed_type,
                category=parent_category.title if parent_category else "",
                custom_attrs=custom_attrs,
            )
        else:
            # This is a category
            category = OPMLCategory(title=title)

            # Process child outlines
            for child in element.findall("outline"):
                result = self._parse_outline(child, category)
                if isinstance(result, OPMLFeed):
                    category.add_feed(result)
                elif isinstance(result, OPMLCategory):
                    category.add_category(result)

            return category

    def parse(self, filepath: str) -> OPMLDocument:
        """Parse an OPML file.

        Args:
            filepath: Path to the OPML file.

        Returns:
            OPMLDocument object with all feeds and categories.

        Raises:
            OPMLParseError: If parsing fails.
            FileNotFoundError: If file doesn't exist.
        """
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except ET.ParseError as e:
            raise OPMLParseError(f"Failed to parse OPML file: {e}")
        except FileNotFoundError:
            raise

        # Get head section
        head = root.find("head")
        doc = OPMLDocument()

        if head is not None:
            doc.title = self._get_text(head, "title") or self.default_title
            doc.date_created = self._parse_date(self._get_text(head, "dateCreated"))
            doc.date_modified = self._parse_date(self._get_text(head, "dateModified"))
            doc.owner_name = self._get_text(head, "ownerName") or ""
            doc.owner_email = self._get_text(head, "ownerEmail") or ""
            doc.owner_id = self._get_text(head, "ownerId") or ""
            doc.docs = self._get_text(head, "docs") or doc.docs
            doc.expansion_state = self._get_text(head, "expansionState") or ""

            # Window settings
            try:
                doc.vert_scroll_state = int(self._get_text(head, "vertScrollState") or 0)
                doc.window_top = int(self._get_text(head, "windowTop") or 0)
                doc.window_left = int(self._get_text(head, "windowLeft") or 0)
                doc.window_bottom = int(self._get_text(head, "windowBottom") or 0)
                doc.window_right = int(self._get_text(head, "windowRight") or 0)
            except ValueError:
                pass

        # Get body/outlines
        body = root.find("body")
        if body is not None:
            for outline in body.findall("outline"):
                result = self._parse_outline(outline)
                if isinstance(result, OPMLFeed):
                    doc.feeds.append(result)
                elif isinstance(result, OPMLCategory):
                    doc.categories.append(result)

        return doc

    def _get_text(self, element: ET.Element, tag: str) -> Optional[str]:
        """Get text content of a child element.

        Args:
            element: Parent XML element.
            tag: Child tag name.

        Returns:
            Text content or None.
        """
        child = element.find(tag)
        if child is not None:
            return child.text
        return None

    def parse_string(self, content: str) -> OPMLDocument:
        """Parse OPML content from a string.

        Args:
            content: OPML XML content as string.

        Returns:
            OPMLDocument object.

        Raises:
            OPMLParseError: If parsing fails.
        """
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            raise OPMLParseError(f"Failed to parse OPML content: {e}")

        # Get head section
        head = root.find("head")
        doc = OPMLDocument()

        if head is not None:
            doc.title = self._get_text(head, "title") or self.default_title
            doc.date_created = self._parse_date(self._get_text(head, "dateCreated"))
            doc.date_modified = self._parse_date(self._get_text(head, "dateModified"))
            doc.owner_name = self._get_text(head, "ownerName") or ""
            doc.owner_email = self._get_text(head, "ownerEmail") or ""
            doc.owner_id = self._get_text(head, "ownerId") or ""
            doc.docs = self._get_text(head, "docs") or doc.docs

        body = root.find("body")
        if body is not None:
            for outline in body.findall("outline"):
                result = self._parse_outline(outline)
                if isinstance(result, OPMLFeed):
                    doc.feeds.append(result)
                elif isinstance(result, OPMLCategory):
                    doc.categories.append(result)

        return doc

    def _create_outline_element(
        self,
        parent: ET.Element,
        item: Union[OPMLFeed, OPMLCategory]
    ) -> ET.Element:
        """Create an outline element for a feed or category.

        Args:
            parent: Parent XML element.
            item: Feed or category to add.

        Returns:
            Created outline element.
        """
        outline = ET.SubElement(parent, "outline")

        if isinstance(item, OPMLFeed):
            outline.set("text", item.title)
            if item.title:
                outline.set("title", item.title)
            if item.xml_url:
                outline.set("xmlUrl", item.xml_url)
            if item.html_url:
                outline.set("htmlUrl", item.html_url)
            if item.description:
                outline.set("description", item.description)
            if item.language:
                outline.set("language", item.language)
            if item.version:
                outline.set("version", item.version)
                outline.set("type", item.version)

            # Add custom attributes
            for key, value in item.custom_attrs.items():
                outline.set(key, value)

        elif isinstance(item, OPMLCategory):
            outline.set("text", item.title)
            outline.set("title", item.title)

            # Add nested feeds and categories
            for feed in item.feeds:
                self._create_outline_element(outline, feed)
            for cat in item.categories:
                self._create_outline_element(outline, cat)

        return outline

    def generate(
        self,
        feeds: List[Union[OPMLFeed, OPMLCategory]],
        title: Optional[str] = None,
        owner_name: str = "",
        owner_email: str = "",
        **kwargs: Any
    ) -> str:
        """Generate OPML XML from feed list.

        Args:
            feeds: List of OPMLFeed or OPMLCategory objects.
            title: Document title.
            owner_name: Owner name.
            owner_email: Owner email.
            **kwargs: Additional OPML head attributes.

        Returns:
            OPML XML string.
        """
        # Create root element
        root = ET.Element("opml", version="2.0")

        # Create head section
        head = ET.SubElement(root, "head")
        ET.SubElement(head, "title").text = title or self.default_title
        ET.SubElement(head, "dateCreated").text = self._format_date(datetime.utcnow())
        ET.SubElement(head, "dateModified").text = self._format_date(datetime.utcnow())
        ET.SubElement(head, "docs").text = "http://dev.opml.org/spec2.html"

        if owner_name:
            ET.SubElement(head, "ownerName").text = owner_name
        if owner_email:
            ET.SubElement(head, "ownerEmail").text = owner_email

        # Add optional head elements
        for key, value in kwargs.items():
            if value and key not in ("title", "dateCreated", "dateModified", "docs"):
                ET.SubElement(head, key).text = str(value)

        # Create body section
        body = ET.SubElement(root, "body")

        # Add feeds and categories
        for item in feeds:
            self._create_outline_element(body, item)

        # Convert to string with pretty printing
        rough_string = ET.tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")

        # Remove empty lines from pretty printing
        lines = [line for line in pretty.split("\n") if line.strip()]
        return "\n".join(lines)

    def export(
        self,
        filepath: str,
        feeds: List[Union[OPMLFeed, OPMLCategory]],
        title: Optional[str] = None,
        owner_name: str = "",
        owner_email: str = "",
        **kwargs: Any
    ) -> None:
        """Export feeds to an OPML file.

        Args:
            filepath: Output file path.
            feeds: List of feeds or categories.
            title: Document title.
            owner_name: Owner name.
            owner_email: Owner email.
            **kwargs: Additional OPML head attributes.

        Raises:
            IOError: If file writing fails.
        """
        content = self.generate(
            feeds=feeds,
            title=title,
            owner_name=owner_name,
            owner_email=owner_email,
            **kwargs
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def flatten_categories(self, doc: OPMLDocument) -> List[OPMLFeed]:
        """Flatten all feeds from a document, preserving category info.

        Args:
            doc: OPMLDocument to flatten.

        Returns:
            List of all feeds with category information.
        """
        return doc.get_all_feeds()

    def categorize_feeds(
        self,
        feeds: List[OPMLFeed],
        category_separator: str = "/"
    ) -> List[Union[OPMLFeed, OPMLCategory]]:
        """Organize flat feed list into categories based on category field.

        Args:
            feeds: List of OPMLFeed objects.
            category_separator: Separator for nested categories.

        Returns:
            List of categorized feeds and categories.
        """
        # Group feeds by category
        category_map: Dict[str, List[OPMLFeed]] = {}
        uncategorized: List[OPMLFeed] = []

        for feed in feeds:
            if feed.category:
                if feed.category not in category_map:
                    category_map[feed.category] = []
                category_map[feed.category].append(feed)
            else:
                uncategorized.append(feed)

        # Build category hierarchy
        result: List[Union[OPMLFeed, OPMLCategory]] = list(uncategorized)

        for cat_path, cat_feeds in category_map.items():
            parts = cat_path.split(category_separator)
            current_level = result

            for i, part in enumerate(parts):
                # Find or create category at this level
                category = None
                for item in current_level:
                    if isinstance(item, OPMLCategory) and item.title == part:
                        category = item
                        break

                if category is None:
                    category = OPMLCategory(title=part)
                    current_level.append(category)

                if i == len(parts) - 1:
                    # Last part - add feeds here
                    category.feeds.extend(cat_feeds)
                else:
                    # Navigate to next level
                    current_level = category.categories

        return result

    def merge_documents(self, *documents: OPMLDocument) -> OPMLDocument:
        """Merge multiple OPML documents into one.

        Args:
            *documents: OPMLDocument objects to merge.

        Returns:
            Merged OPMLDocument.
        """
        merged = OPMLDocument(
            title=self.default_title,
            date_modified=datetime.utcnow(),
        )

        seen_urls: set = set()

        for doc in documents:
            # Merge uncategorized feeds
            for feed in doc.feeds:
                if feed.xml_url not in seen_urls:
                    merged.feeds.append(feed)
                    seen_urls.add(feed.xml_url)

            # Merge categories
            for category in doc.categories:
                self._merge_category(merged, category, seen_urls)

        return merged

    def _merge_category(
        self,
        target: OPMLDocument,
        source: OPMLCategory,
        seen_urls: set
    ) -> None:
        """Merge a category into the target document.

        Args:
            target: Target document.
            source: Source category.
            seen_urls: Set of already added feed URLs.
        """
        # Find or create matching category
        target_cat = None
        for cat in target.categories:
            if cat.title == source.title:
                target_cat = cat
                break

        if target_cat is None:
            target_cat = OPMLCategory(title=source.title)
            target.categories.append(target_cat)

        # Add feeds
        for feed in source.feeds:
            if feed.xml_url not in seen_urls:
                target_cat.feeds.append(feed)
                seen_urls.add(feed.xml_url)

        # Recursively merge sub-categories
        for subcat in source.categories:
            self._merge_category_subcat(target_cat, subcat, seen_urls)

    def _merge_category_subcat(
        self,
        target: OPMLCategory,
        source: OPMLCategory,
        seen_urls: set
    ) -> None:
        """Recursively merge sub-categories.

        Args:
            target: Target category.
            source: Source category.
            seen_urls: Set of already added feed URLs.
        """
        # Find or create matching sub-category
        target_sub = None
        for cat in target.categories:
            if cat.title == source.title:
                target_sub = cat
                break

        if target_sub is None:
            target_sub = OPMLCategory(title=source.title)
            target.categories.append(target_sub)

        # Add feeds
        for feed in source.feeds:
            if feed.xml_url not in seen_urls:
                target_sub.feeds.append(feed)
                seen_urls.add(feed.xml_url)

        # Recursively merge deeper
        for subcat in source.categories:
            self._merge_category_subcat(target_sub, subcat, seen_urls)
