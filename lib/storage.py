"""Feed Storage Management Module.

This module provides JSON-based storage for RSS feeds with category management,
feed CRUD operations, and data persistence.

Example:
    >>> from storage import FeedStorage
    >>> storage = FeedStorage()
    >>> storage.add_feed("https://example.com/feed.xml", "Example Blog", "Tech")
    >>> feeds = storage.get_feeds_by_category("Tech")
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from copy import deepcopy


@dataclass
class FeedEntry:
    """Represents a stored RSS feed.

    Attributes:
        url: Feed URL (unique identifier).
        title: Feed title.
        category: Category name.
        description: Feed description.
        html_url: Website URL.
        added_at: When the feed was added (ISO format).
        last_updated: Last update timestamp.
        last_fetched: Last fetch timestamp.
        fetch_count: Number of times fetched.
        error_count: Number of consecutive errors.
        last_error: Last error message.
        is_active: Whether the feed is active.
        custom_data: Additional custom data.
        tags: List of tags.
    """
    url: str
    title: str = ""
    category: str = "uncategorized"
    description: str = ""
    html_url: str = ""
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: Optional[str] = None
    last_fetched: Optional[str] = None
    fetch_count: int = 0
    error_count: int = 0
    last_error: str = ""
    is_active: bool = True
    custom_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedEntry":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Category:
    """Represents a feed category.

    Attributes:
        name: Category name (unique).
        description: Category description.
        created_at: When the category was created.
        parent: Parent category name for nested categories.
        sort_order: Sort order (lower = first).
        custom_data: Additional custom data.
    """
    name: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    parent: str = ""
    sort_order: int = 0
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class StorageError(Exception):
    """Exception raised for storage-related errors."""
    pass


class FeedNotFoundError(StorageError):
    """Exception raised when a feed is not found."""
    pass


class CategoryNotFoundError(StorageError):
    """Exception raised when a category is not found."""
    pass


class FeedStorage:
    """JSON-based storage for RSS feeds.

    This class provides methods to add, remove, update, and query feeds
    and categories with persistent storage.

    Attributes:
        data_dir: Directory for data files.
        feeds_file: Path to feeds JSON file.
        categories_file: Path to categories JSON file.
        auto_save: Whether to auto-save on changes.
    """

    DEFAULT_DATA_DIR = Path.home() / ".config" / "rss-manager"
    CURRENT_VERSION = "2.0"

    def __init__(
        self,
        data_dir: Optional[Union[str, Path]] = None,
        auto_save: bool = True,
        encoding: str = "utf-8"
    ):
        """Initialize the FeedStorage instance.

        Args:
            data_dir: Directory for data files. Defaults to ~/.config/rss-manager.
            auto_save: Whether to automatically save on changes.
            encoding: File encoding.
        """
        self.data_dir = Path(data_dir) if data_dir else self.DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.auto_save = auto_save
        self.encoding = encoding

        self.feeds_file = self.data_dir / "feeds.json"
        self.categories_file = self.data_dir / "categories.json"

        self._feeds: Dict[str, FeedEntry] = {}
        self._categories: Dict[str, Category] = {}

        self._load()

    def _load(self) -> None:
        """Load data from storage files."""
        # Load feeds
        if self.feeds_file.exists():
            try:
                with open(self.feeds_file, "r", encoding=self.encoding) as f:
                    data = json.load(f)

                # Check version
                version = data.get("version", "1.0")
                feeds_data = data.get("feeds", [])

                for feed_dict in feeds_data:
                    try:
                        feed = FeedEntry.from_dict(feed_dict)
                        self._feeds[feed.url] = feed
                    except (TypeError, ValueError):
                        continue
            except (json.JSONDecodeError, IOError):
                pass

        # Load categories
        if self.categories_file.exists():
            try:
                with open(self.categories_file, "r", encoding=self.encoding) as f:
                    data = json.load(f)

                categories_data = data.get("categories", [])
                for cat_dict in categories_data:
                    try:
                        cat = Category.from_dict(cat_dict)
                        self._categories[cat.name] = cat
                    except (TypeError, ValueError):
                        continue
            except (json.JSONDecodeError, IOError):
                pass

        # Ensure default category exists
        if "uncategorized" not in self._categories:
            self._categories["uncategorized"] = Category(name="uncategorized")

    def _save(self) -> None:
        """Save data to storage files."""
        # Save feeds
        feeds_data = {
            "version": self.CURRENT_VERSION,
            "updated_at": datetime.now().isoformat(),
            "feeds": [feed.to_dict() for feed in self._feeds.values()],
        }

        try:
            with open(self.feeds_file, "w", encoding=self.encoding) as f:
                json.dump(feeds_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise StorageError(f"Failed to save feeds: {e}")

        # Save categories
        categories_data = {
            "version": self.CURRENT_VERSION,
            "updated_at": datetime.now().isoformat(),
            "categories": [cat.to_dict() for cat in self._categories.values()],
        }

        try:
            with open(self.categories_file, "w", encoding=self.encoding) as f:
                json.dump(categories_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise StorageError(f"Failed to save categories: {e}")

    def _maybe_save(self) -> None:
        """Save if auto_save is enabled."""
        if self.auto_save:
            self._save()

    # Feed Operations

    def add_feed(
        self,
        url: str,
        title: str = "",
        category: str = "uncategorized",
        **kwargs: Any
    ) -> FeedEntry:
        """Add a new feed.

        Args:
            url: Feed URL (must be unique).
            title: Feed title.
            category: Category name.
            **kwargs: Additional feed attributes.

        Returns:
            The created FeedEntry.

        Raises:
            StorageError: If feed already exists.
        """
        url = url.strip()
        if url in self._feeds:
            raise StorageError(f"Feed already exists: {url}")

        # Ensure category exists
        if category not in self._categories:
            category = "uncategorized"

        feed = FeedEntry(
            url=url,
            title=title or url,
            category=category,
            **{k: v for k, v in kwargs.items() if k in FeedEntry.__dataclass_fields__}
        )

        self._feeds[url] = feed
        self._maybe_save()
        return feed

    def get_feed(self, url: str) -> Optional[FeedEntry]:
        """Get a feed by URL.

        Args:
            url: Feed URL.

        Returns:
            FeedEntry or None if not found.
        """
        return self._feeds.get(url)

    def get_feeds(
        self,
        category: Optional[str] = None,
        active_only: bool = False,
        tag: Optional[str] = None
    ) -> List[FeedEntry]:
        """Get feeds with optional filtering.

        Args:
            category: Filter by category.
            active_only: Only return active feeds.
            tag: Filter by tag.

        Returns:
            List of FeedEntry objects.
        """
        feeds = list(self._feeds.values())

        if category:
            feeds = [f for f in feeds if f.category == category]

        if active_only:
            feeds = [f for f in feeds if f.is_active]

        if tag:
            feeds = [f for f in feeds if tag in f.tags]

        return feeds

    def get_all_feeds(self) -> List[FeedEntry]:
        """Get all feeds.

        Returns:
            List of all FeedEntry objects.
        """
        return list(self._feeds.values())

    def update_feed(self, url: str, **kwargs: Any) -> FeedEntry:
        """Update feed attributes.

        Args:
            url: Feed URL to update.
            **kwargs: Attributes to update.

        Returns:
            Updated FeedEntry.

        Raises:
            FeedNotFoundError: If feed doesn't exist.
        """
        feed = self._feeds.get(url)
        if not feed:
            raise FeedNotFoundError(f"Feed not found: {url}")

        for key, value in kwargs.items():
            if key in FeedEntry.__dataclass_fields__ and key != "url":
                setattr(feed, key, value)

        feed.last_updated = datetime.now().isoformat()
        self._maybe_save()
        return feed

    def remove_feed(self, url: str) -> bool:
        """Remove a feed.

        Args:
            url: Feed URL to remove.

        Returns:
            True if removed, False if not found.
        """
        if url in self._feeds:
            del self._feeds[url]
            self._maybe_save()
            return True
        return False

    def feed_exists(self, url: str) -> bool:
        """Check if a feed exists.

        Args:
            url: Feed URL.

        Returns:
            True if feed exists.
        """
        return url in self._feeds

    def record_feed_fetch(self, url: str, success: bool = True, error: str = "") -> None:
        """Record a feed fetch attempt.

        Args:
            url: Feed URL.
            success: Whether the fetch was successful.
            error: Error message if not successful.
        """
        feed = self._feeds.get(url)
        if not feed:
            return

        feed.last_fetched = datetime.now().isoformat()
        feed.fetch_count += 1

        if success:
            feed.error_count = 0
            feed.last_error = ""
        else:
            feed.error_count += 1
            feed.last_error = error

        self._maybe_save()

    def search_feeds(self, query: str) -> List[FeedEntry]:
        """Search feeds by title, URL, or description.

        Args:
            query: Search query string.

        Returns:
            List of matching feeds.
        """
        query = query.lower()
        results = []

        for feed in self._feeds.values():
            if (
                query in feed.title.lower()
                or query in feed.url.lower()
                or query in feed.description.lower()
                or any(query in tag.lower() for tag in feed.tags)
            ):
                results.append(feed)

        return results

    def get_feed_count(self, category: Optional[str] = None) -> int:
        """Get the number of feeds.

        Args:
            category: Optional category to count.

        Returns:
            Number of feeds.
        """
        if category:
            return len([f for f in self._feeds.values() if f.category == category])
        return len(self._feeds)

    # Category Operations

    def add_category(
        self,
        name: str,
        description: str = "",
        parent: str = "",
        **kwargs: Any
    ) -> Category:
        """Add a new category.

        Args:
            name: Category name (must be unique).
            description: Category description.
            parent: Parent category name.
            **kwargs: Additional category attributes.

        Returns:
            The created Category.

        Raises:
            StorageError: If category already exists.
        """
        name = name.strip()
        if not name:
            raise StorageError("Category name cannot be empty")

        if name in self._categories:
            raise StorageError(f"Category already exists: {name}")

        # Validate parent
        if parent and parent not in self._categories:
            raise CategoryNotFoundError(f"Parent category not found: {parent}")

        category = Category(
            name=name,
            description=description,
            parent=parent,
            **{k: v for k, v in kwargs.items() if k in Category.__dataclass_fields__}
        )

        self._categories[name] = category
        self._maybe_save()
        return category

    def get_category(self, name: str) -> Optional[Category]:
        """Get a category by name.

        Args:
            name: Category name.

        Returns:
            Category or None if not found.
        """
        return self._categories.get(name)

    def get_categories(self, parent: Optional[str] = None) -> List[Category]:
        """Get all categories, optionally filtered by parent.

        Args:
            parent: Filter by parent category.

        Returns:
            List of Category objects.
        """
        categories = list(self._categories.values())

        if parent is not None:
            categories = [c for c in categories if c.parent == parent]

        return sorted(categories, key=lambda c: (c.sort_order, c.name))

    def update_category(self, name: str, **kwargs: Any) -> Category:
        """Update category attributes.

        Args:
            name: Category name to update.
            **kwargs: Attributes to update.

        Returns:
            Updated Category.

        Raises:
            CategoryNotFoundError: If category doesn't exist.
        """
        category = self._categories.get(name)
        if not category:
            raise CategoryNotFoundError(f"Category not found: {name}")

        for key, value in kwargs.items():
            if key in Category.__dataclass_fields__ and key != "name":
                setattr(category, key, value)

        self._maybe_save()
        return category

    def remove_category(self, name: str, move_to: str = "uncategorized") -> bool:
        """Remove a category and move its feeds to another category.

        Args:
            name: Category name to remove.
            move_to: Category to move feeds to.

        Returns:
            True if removed, False if not found.

        Raises:
            CategoryNotFoundError: If move_to category doesn't exist.
        """
        if name not in self._categories:
            return False

        if move_to not in self._categories:
            raise CategoryNotFoundError(f"Target category not found: {move_to}")

        # Move feeds
        for feed in self._feeds.values():
            if feed.category == name:
                feed.category = move_to

        # Update child categories
        for cat in self._categories.values():
            if cat.parent == name:
                cat.parent = ""

        del self._categories[name]
        self._maybe_save()
        return True

    def category_exists(self, name: str) -> bool:
        """Check if a category exists.

        Args:
            name: Category name.

        Returns:
            True if category exists.
        """
        return name in self._categories

    def get_category_tree(self) -> Dict[str, Any]:
        """Get categories as a nested tree structure.

        Returns:
            Dictionary representing the category tree.
        """
        tree: Dict[str, Any] = {}
        children: Dict[str, List[str]] = {}

        # Build parent-child relationships
        for name, cat in self._categories.items():
            if cat.parent:
                if cat.parent not in children:
                    children[cat.parent] = []
                children[cat.parent].append(name)

        def build_branch(name: str) -> Dict[str, Any]:
            cat = self._categories.get(name)
            if not cat:
                return {}

            branch = {
                "name": name,
                "description": cat.description,
                "data": cat,
                "children": [],
            }

            for child_name in children.get(name, []):
                branch["children"].append(build_branch(child_name))

            return branch

        # Find root categories
        roots = [name for name, cat in self._categories.items() if not cat.parent]

        return {"categories": [build_branch(name) for name in sorted(roots)]}

    def get_feeds_by_category(self) -> Dict[str, List[FeedEntry]]:
        """Get feeds grouped by category.

        Returns:
            Dictionary mapping category names to feed lists.
        """
        result: Dict[str, List[FeedEntry]] = {}

        for feed in self._feeds.values():
            cat = feed.category or "uncategorized"
            if cat not in result:
                result[cat] = []
            result[cat].append(feed)

        return result

    # Import/Export

    def export_to_dict(self) -> Dict[str, Any]:
        """Export all data as a dictionary.

        Returns:
            Dictionary with feeds and categories.
        """
        return {
            "version": self.CURRENT_VERSION,
            "exported_at": datetime.now().isoformat(),
            "feeds": [feed.to_dict() for feed in self._feeds.values()],
            "categories": [cat.to_dict() for cat in self._categories.values()],
        }

    def import_from_dict(
        self,
        data: Dict[str, Any],
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """Import data from a dictionary.

        Args:
            data: Dictionary with feeds and categories.
            skip_existing: Skip feeds that already exist.

        Returns:
            Dictionary with import counts.
        """
        imported = {"feeds": 0, "categories": 0, "skipped": 0, "errors": 0}

        # Import categories first
        for cat_dict in data.get("categories", []):
            try:
                name = cat_dict.get("name", "")
                if name and name not in self._categories:
                    cat = Category.from_dict(cat_dict)
                    self._categories[cat.name] = cat
                    imported["categories"] += 1
            except Exception:
                imported["errors"] += 1

        # Ensure uncategorized exists
        if "uncategorized" not in self._categories:
            self._categories["uncategorized"] = Category(name="uncategorized")

        # Import feeds
        for feed_dict in data.get("feeds", []):
            try:
                url = feed_dict.get("url", "")
                if not url:
                    imported["errors"] += 1
                    continue

                if url in self._feeds:
                    if skip_existing:
                        imported["skipped"] += 1
                        continue

                feed = FeedEntry.from_dict(feed_dict)
                self._feeds[feed.url] = feed
                imported["feeds"] += 1
            except Exception:
                imported["errors"] += 1

        self._maybe_save()
        return imported

    def export_to_json(self, filepath: Optional[str] = None) -> str:
        """Export all data to a JSON file.

        Args:
            filepath: Output file path. Defaults to data_dir/export.json.

        Returns:
            Path to the exported file.
        """
        if filepath is None:
            filepath = self.data_dir / "export.json"
        else:
            filepath = Path(filepath)

        data = self.export_to_dict()

        with open(filepath, "w", encoding=self.encoding) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def import_from_json(
        self,
        filepath: str,
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """Import data from a JSON file.

        Args:
            filepath: Input file path.
            skip_existing: Skip feeds that already exist.

        Returns:
            Dictionary with import counts.
        """
        with open(filepath, "r", encoding=self.encoding) as f:
            data = json.load(f)

        return self.import_from_dict(data, skip_existing)

    # Statistics

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with statistics.
        """
        feeds = list(self._feeds.values())
        active_feeds = [f for f in feeds if f.is_active]

        return {
            "total_feeds": len(feeds),
            "active_feeds": len(active_feeds),
            "inactive_feeds": len(feeds) - len(active_feeds),
            "total_categories": len(self._categories),
            "feeds_with_errors": len([f for f in feeds if f.error_count > 0]),
            "total_fetch_count": sum(f.fetch_count for f in feeds),
            "categories_with_feeds": len(set(f.category for f in feeds)),
        }

    def get_error_feeds(self, min_errors: int = 1) -> List[FeedEntry]:
        """Get feeds with errors.

        Args:
            min_errors: Minimum error count.

        Returns:
            List of feeds with errors.
        """
        return [f for f in self._feeds.values() if f.error_count >= min_errors]

    def cleanup_errors(self, reset: bool = True) -> int:
        """Clean up error counts.

        Args:
            reset: Reset error counts to 0.

        Returns:
            Number of feeds cleaned up.
        """
        count = 0
        for feed in self._feeds.values():
            if feed.error_count > 0:
                if reset:
                    feed.error_count = 0
                    feed.last_error = ""
                count += 1

        self._maybe_save()
        return count

    # Persistence

    def save(self) -> None:
        """Manually save all data to storage."""
        self._save()

    def reload(self) -> None:
        """Reload data from storage."""
        self._feeds.clear()
        self._categories.clear()
        self._load()

    def clear_all(self) -> None:
        """Clear all feeds and categories (dangerous!)."""
        self._feeds.clear()
        self._categories.clear()
        self._categories["uncategorized"] = Category(name="uncategorized")
        self._maybe_save()
