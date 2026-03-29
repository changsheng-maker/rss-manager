#!/usr/bin/env python3
"""RSS feed list command."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from storage import FeedStorage

def get_feeds(category=None):
    """Get all feeds from storage, optionally filtered by category."""
    storage = FeedStorage()
    if category:
        feeds = storage.get_feeds_by_category(category)
    else:
        feeds = storage.get_all_feeds()
    # Convert FeedEntry objects to dictionaries
    return [vars(feed) for feed in feeds]


def format_time_ago(iso_time: str) -> str:
    """Format ISO time as human-readable 'time ago'."""
    if not iso_time:
        return "Never"
    try:
        dt = datetime.fromisoformat(iso_time)
        now = datetime.now()
        diff = now - dt

        if diff.days > 365:
            return f"{diff.days // 365}y ago"
        elif diff.days > 30:
            return f"{diff.days // 30}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"
    except Exception:
        return "Unknown"


def truncate(s: str, length: int) -> str:
    """Truncate string to specified length."""
    if len(s) <= length:
        return s
    return s[:length-3] + "..."


def main():
    parser = argparse.ArgumentParser(
        description="List all subscribed RSS feeds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rss-list.py
  python rss-list.py --category tech
  python rss-list.py -c news --json
        """
    )
    parser.add_argument(
        "-c", "--category",
        help="Filter by category"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Don't truncate long titles/URLs in table output"
    )

    args = parser.parse_args()

    feeds = get_feeds(args.category)

    if args.json:
        output = {
            "success": True,
            "count": len(feeds),
            "category_filter": args.category,
            "feeds": feeds
        }
        print(json.dumps(output, indent=2))
        return

    if not feeds:
        if args.category:
            print(f"No feeds found in category: {args.category}")
        else:
            print("No feeds found. Add some with 'rss-add.py'")
        return

    # Group by category
    categories = {}
    for feed in feeds:
        cat = feed.get("category", "uncategorized")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(feed)

    # Print summary
    print(f"Total feeds: {len(feeds)}")
    if args.category:
        print(f"Category: {args.category}")
    print()

    # Print feeds grouped by category
    for category in sorted(categories.keys()):
        cat_feeds = categories[category]
        print(f"\n[{category}] ({len(cat_feeds)} feeds)")
        print("-" * 80)

        # Header
        print(f"{'#':<4} {'Title':<35} {'Last Updated':<12} {'URL':<30}")
        print("-" * 80)

        for i, feed in enumerate(cat_feeds, 1):
            title = feed.get("title", "Untitled")
            url = feed["url"]
            last_updated = format_time_ago(feed.get("last_updated"))

            if not args.no_truncate:
                title = truncate(title, 35)
                url = truncate(url, 30)

            print(f"{i:<4} {title:<35} {last_updated:<12} {url:<30}")

    print()


if __name__ == "__main__":
    main()
