#!/usr/bin/env python3
"""RSS OPML export command."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from storage import FeedStorage

def get_feeds():
    """Get all feeds from storage."""
    storage = FeedStorage()
    feeds = storage.get_all_feeds()
    # Convert to dictionaries
    return [vars(feed) for feed in feeds]
from lib.opml import export_opml


def main():
    parser = argparse.ArgumentParser(
        description="Export RSS feeds to an OPML file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rss-export.py my-feeds.opml
  python rss-export.py backup.opml --category tech
  python rss-export.py export.opml --title "My Subscriptions"
        """
    )
    parser.add_argument(
        "output",
        help="Output file path for OPML"
    )
    parser.add_argument(
        "-c", "--category",
        help="Export only feeds from this category"
    )
    parser.add_argument(
        "-t", "--title",
        help="Title for the OPML file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Get feeds
    feeds = get_feeds(args.category)

    if not feeds:
        msg = {"success": False, "error": "No feeds to export"}
        if args.json:
            print(json.dumps(msg, indent=2))
        else:
            print(msg["error"])
        sys.exit(1)

    # Export to OPML
    title = args.title or f"RSS Subscriptions ({datetime.now().strftime('%Y-%m-%d')})"
    result = export_opml(feeds, args.output, title)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if result["success"]:
        print(f"Successfully exported {result['count']} feeds to:")
        print(f"  {result['path']}")
        if args.category:
            print(f"  Category: {args.category}")
    else:
        print(f"Error: {result.get('error', 'Export failed')}")
        sys.exit(1)

    return result


if __name__ == "__main__":
    main()
