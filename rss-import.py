#!/usr/bin/env python3
"""RSS OPML import command."""
import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib.opml import parse_opml
from lib.storage import add_feed


def main():
    parser = argparse.ArgumentParser(
        description="Import RSS feeds from an OPML file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rss-import.py subscriptions.opml
  python rss-import.py ~/Downloads/feeds.opml --json
        """
    )
    parser.add_argument(
        "file",
        help="Path to OPML file to import"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without adding"
    )

    args = parser.parse_args()

    # Parse OPML
    result = parse_opml(args.file)

    if not result["success"]:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result.get('error', 'Failed to parse OPML')}")
        sys.exit(1)

    feeds = result["feeds"]

    if not feeds:
        msg = {"success": False, "error": "No feeds found in OPML file"}
        if args.json:
            print(json.dumps(msg, indent=2))
        else:
            print(msg["error"])
        sys.exit(1)

    if args.dry_run:
        output = {
            "success": True,
            "dry_run": True,
            "would_import": len(feeds),
            "feeds": feeds
        }
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print(f"Would import {len(feeds)} feeds:")
            for feed in feeds:
                print(f"  - {feed['title']} ({feed['category']})")
                print(f"    URL: {feed['url']}")
        return

    # Import feeds
    imported = []
    duplicates = []
    errors = []

    for feed in feeds:
        add_result = add_feed(
            feed["url"],
            feed["title"],
            feed.get("category", "uncategorized")
        )
        if add_result["success"]:
            imported.append(feed)
        elif "already exists" in add_result.get("error", "").lower():
            duplicates.append(feed)
        else:
            errors.append({"feed": feed, "error": add_result.get("error", "Unknown error")})

    output = {
        "success": True,
        "imported": len(imported),
        "duplicates": len(duplicates),
        "errors": len(errors),
        "imported_feeds": imported,
        "duplicate_feeds": duplicates,
        "error_details": errors
    }

    if args.json:
        print(json.dumps(output, indent=2))
        return

    # Human-readable output
    print(f"Import complete!")
    print(f"  Imported: {len(imported)}")
    print(f"  Duplicates (skipped): {len(duplicates)}")
    print(f"  Errors: {len(errors)}")

    if imported:
        print("\nImported feeds:")
        for feed in imported:
            print(f"  + {feed['title']} [{feed['category']}]")

    if duplicates:
        print("\nDuplicates (already exist):")
        for feed in duplicates:
            print(f"  = {feed['title']}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  ! {err['feed']['title']}: {err['error']}")

    return output


if __name__ == "__main__":
    main()
