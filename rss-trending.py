#!/usr/bin/env python3
"""
RSS Trending - View trending content across multiple platforms
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

import feedparser

def load_trending_sources():
    """Load trending sources configuration."""
    config_path = Path(__file__).parent / "data" / "trending-sources.json"
    with open(config_path) as f:
        return json.load(f)

def fetch_feed(url, limit=5):
    """Fetch and parse RSS feed."""
    try:
        feed = feedparser.parse(url)
        return feed.entries[:limit]
    except Exception as e:
        print(f"⚠️  Error fetching {url}: {e}", file=sys.stderr)
        return []

def format_entry(entry, source_name):
    """Format a feed entry."""
    title = entry.get('title', 'No title')
    link = entry.get('link', '')
    return {
        'title': title[:80] + '...' if len(title) > 80 else title,
        'url': link,
        'source': source_name
    }

def main():
    parser = argparse.ArgumentParser(
        description="View trending content across platforms",
        epilog="""
Examples:
  python rss-trending.py              # Show all trending
  python rss-trending.py --category ai    # AI trending only
  python rss-trending.py --category startups  # Startup trending
  python rss-trending.py --limit 10     # Show 10 items per source
        """
    )
    parser.add_argument(
        "--category", "-c",
        choices=["ai", "startups", "tech", "dev", "all"],
        default="all",
        help="Category to show"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=5,
        help="Items per source (default: 5)"
    )
    parser.add_argument(
        "--sources",
        action="store_true",
        help="List available sources"
    )

    args = parser.parse_args()

    # Load configuration
    config = load_trending_sources()

    if args.sources:
        print("\n📊 Available Trending Sources:")
        print("=" * 60)
        for cat_id, cat_data in config['categories'].items():
            print(f"\n🔥 {cat_data['name']} ({cat_id})")
            for src in cat_data['sources']:
                print(f"   • {src['name']}: {src['url']}")
        return

    # Determine categories to show
    if args.category == "all":
        categories = list(config['categories'].keys())
    else:
        categories = [args.category]

    print(f"\n📈 Trending Content - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)

    total_items = 0

    for cat_id in categories:
        if cat_id not in config['categories']:
            continue

        cat_data = config['categories'][cat_id]
        print(f"\n🔥 {cat_data['name']}")
        print("-" * 80)

        for source in cat_data['sources']:
            print(f"\n  📌 {source['name']}")
            entries = fetch_feed(source['url'], args.limit)

            if not entries:
                print("     (No items fetched)")
                continue

            for i, entry in enumerate(entries, 1):
                formatted = format_entry(entry, source['name'])
                print(f"     {i}. {formatted['title']}")
                print(f"        {formatted['url']}")
                total_items += 1

    print(f"\n{'=' * 80}")
    print(f"📊 Total: {total_items} trending items from {len(categories)} categories")
    print("=" * 80)

if __name__ == "__main__":
    main()
