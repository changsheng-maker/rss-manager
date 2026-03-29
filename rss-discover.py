#!/usr/bin/env python3
"""RSS feed discovery command."""
import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib.discovery import discover_feeds


def main():
    parser = argparse.ArgumentParser(
        description="Discover RSS feeds from a URL or website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rss-discover.py https://example.com
  python rss-discover.py example.com --verbose
  python rss-discover.py https://news.ycombinator.com -v
        """
    )
    parser.add_argument(
        "url",
        help="URL or website to discover feeds from"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output including validation"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    if args.verbose and not args.json:
        print(f"Discovering feeds from: {args.url}")
        print("-" * 50)

    result = discover_feeds(args.url, verbose=args.verbose)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if not result["success"]:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if result["feeds"]:
            print("\nHowever, some feeds were found:")
        else:
            sys.exit(1)

    feeds = result.get("feeds", [])

    if not feeds:
        print("No feeds found.")
        sys.exit(1)

    print(f"\nFound {len(feeds)} feed(s):\n")

    for i, feed in enumerate(feeds, 1):
        print(f"{i}. {feed.get('title', 'Untitled')}")
        print(f"   URL: {feed['url']}")
        print(f"   Type: {feed.get('type', 'Unknown')}")
        if feed.get('description') and args.verbose:
            print(f"   Description: {feed['description'][:100]}...")
        print()

    # Also output as JSON for programmatic use
    output = {
        "success": True,
        "count": len(feeds),
        "feeds": feeds
    }
    return output


if __name__ == "__main__":
    main()
