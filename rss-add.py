#!/usr/bin/env python3
"""RSS feed add command."""
import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from storage import FeedStorage, StorageError

def add_feed(url, title="", category="uncategorized"):
    """Add a feed to storage.

    Returns:
        dict: {"success": bool, "feed": dict, "error": str}
    """
    storage = FeedStorage()
    try:
        feed = storage.add_feed(url, title, category)
        return {
            "success": True,
            "feed": {
                "url": feed.url,
                "title": feed.title,
                "category": feed.category
            }
        }
    except StorageError as e:
        return {"success": False, "error": str(e)}
from lib.discovery import discover_feeds, parse_feed, HAS_DEPS

if HAS_DEPS:
    import requests


def fetch_feed_title(url: str) -> str:
    """Try to fetch the title from a feed URL."""
    if not HAS_DEPS:
        return "Untitled"
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response.raise_for_status()
        feed_info = parse_feed(response.text)
        if feed_info and feed_info.get("title"):
            return feed_info["title"]
    except Exception:
        pass
    return "Untitled"


def main():
    parser = argparse.ArgumentParser(
        description="Add an RSS feed to your subscription list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rss-add.py https://example.com/feed.xml
  python rss-add.py https://example.com/feed.xml --category tech
  python rss-add.py "News Feed" --from-discover
        """
    )
    parser.add_argument(
        "source",
        help="Feed URL or name from discover results"
    )
    parser.add_argument(
        "-c", "--category",
        default="uncategorized",
        help="Category for the feed (default: uncategorized)"
    )
    parser.add_argument(
        "-t", "--title",
        help="Custom title for the feed (auto-detected if not provided)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Determine if source is a URL or needs discovery
    url = args.source
    if not url.startswith(("http://", "https://", "feed://")):
        # Try to discover
        if not args.json:
            print(f"'{url}' doesn't look like a URL. Attempting discovery...")
        result = discover_feeds(url)
        if result["success"] and result["feeds"]:
            url = result["feeds"][0]["url"]
            title = args.title or result["feeds"][0].get("title", "Untitled")
        else:
            error = {"success": False, "error": f"Could not discover feed for: {args.source}"}
            if args.json:
                print(json.dumps(error))
            else:
                print(f"Error: {error['error']}")
            sys.exit(1)
    else:
        # Clean up the URL
        url = url.replace("feed://", "https://")
        title = args.title

    # Get title if not provided
    if not title:
        title = fetch_feed_title(url)

    # Add the feed
    result = add_feed(url, title, args.category)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if result["success"]:
        feed = result["feed"]
        print(f"Successfully added feed:")
        print(f"  Title: {feed['title']}")
        print(f"  URL: {feed['url']}")
        print(f"  Category: {feed['category']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if result.get("feed"):
            print(f"Feed already exists: {result['feed']['url']}")
        sys.exit(1)

    return result


if __name__ == "__main__":
    main()
