#!/usr/bin/env python3
"""GitHub Trending Report - Generate HTML report of GitHub trending repositories."""

import argparse
import sys
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

import feedparser
from html_generator import HTMLReportGenerator


def fetch_github_trending(language: str = "", since: str = "daily") -> list:
    """Fetch GitHub trending repositories via RSSHub or fallback to search API."""
    # Try RSSHub first
    if language:
        url = f"https://rsshub.app/github/trending/{since}/{language}"
    else:
        url = f"https://rsshub.app/github/trending/{since}"

    print(f"Fetching GitHub trending: {language or 'all languages'} ({since})...")

    try:
        # Set timeout for RSSHub
        feed = feedparser.parse(url, timeout=10)
        if feed.entries and len(feed.entries) > 0:
            return feed.entries
    except Exception as e:
        print(f"RSSHub unavailable, trying fallback...", file=sys.stderr)

    # Fallback: Use GitHub Search API for recently starred repos
    return fetch_github_trending_fallback(language, since)


def fetch_github_trending_fallback(language: str = "", since: str = "daily") -> list:
    """Fallback using GitHub Search API - sort by recently starred."""
    if since == "daily":
        created_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif since == "weekly":
        created_date = (datetime.now() - timedelta(weeks=1)).strftime("%Y-%m-%d")
    else:  # monthly
        created_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # Build query: recently created/pushed repos with stars
    query_parts = [f"created:>{created_date}"]
    if language:
        query_parts.append(f"language:{language}")

    query = " ".join(query_parts)
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=25"

    print(f"Using GitHub Search API fallback...")

    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "RSS-Manager/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            # Convert to feed-like entries
            entries = []
            for repo in data.get('items', []):
                entry = {
                    'title': f"{repo['full_name']}: {repo['description'] or 'No description'} ({repo['language'] or 'Unknown'}) ⭐ {repo['stargazers_count']:,}",
                    'link': repo['html_url'],
                    'description': repo['description'] or ''
                }
                entries.append(entry)
            return entries
    except Exception as e:
        print(f"GitHub API fallback also failed: {e}", file=sys.stderr)
        return []


def parse_github_entry(entry) -> dict:
    """Parse GitHub trending entry into structured data."""
    title = entry.get('title', '')
    link = entry.get('link', '')
    description = entry.get('description', '')

    # Extract language and stars from title if available
    # Format usually: "user/repo: Description (Language) ⭐ Stars"
    data = {
        'title': title,
        'url': link,
        'description': description,
        'language': 'Unknown',
        'stars': '',
        'category': 'GitHub Trending'
    }

    # Try to extract language
    lang_match = re.search(r'\(([^)]+)\)', title)
    if lang_match:
        data['language'] = lang_match.group(1)

    # Try to extract stars
    stars_match = re.search(r'[\d,]+', title.split('⭐')[-1] if '⭐' in title else '')
    if stars_match:
        data['stars'] = stars_match.group()

    return data


def generate_html_report(items: list, language: str, since: str) -> str:
    """Generate HTML report."""
    generator = HTMLReportGenerator(
        title=f"GitHub Trending {language or 'All Languages'} - {since.capitalize()}"
    )

    # Convert items to standard format
    formatted_items = []
    for item in items:
        formatted_item = {
            'title': item.get('title', 'No title'),
            'url': item.get('url', ''),
            'summary': item.get('description', '')[:200] + '...' if len(item.get('description', '')) > 200 else item.get('description', ''),
            'source': f"⭐ {item.get('stars', 'N/A')} stars",
            'published': item.get('language', 'Unknown'),
            'category': item.get('category', 'GitHub Trending')
        }
        formatted_items.append(formatted_item)

    return generator.generate(formatted_items)


def main():
    parser = argparse.ArgumentParser(
        description="Generate GitHub trending report",
        epilog="""
Examples:
  python github-trending.py                    # Today's trending
  python github-trending.py --language python  # Python trending
  python github-trending.py --since weekly     # Weekly trending
  python github-trending.py --language javascript --since monthly
  python github-trending.py --output ~/github-trending.html
        """
    )

    parser.add_argument(
        "--language", "-l",
        default="",
        help="Programming language filter (python, javascript, typescript, go, rust, etc.)"
    )
    parser.add_argument(
        "--since", "-s",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Time period (default: daily)"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=25,
        help="Number of repositories to show (default: 25)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output HTML file path"
    )
    parser.add_argument(
        "--format",
        choices=["html", "json", "markdown"],
        default="html",
        help="Output format (default: html)"
    )

    args = parser.parse_args()

    # Fetch trending repos
    entries = fetch_github_trending(args.language, args.since)

    if not entries:
        print("❌ No trending repositories found or RSSHub unavailable.")
        print("💡 Try using native GitHub trending instead:")
        print("   https://github.com/trending")
        sys.exit(1)

    # Limit entries
    entries = entries[:args.limit]

    # Parse entries
    items = [parse_github_entry(e) for e in entries]

    # Generate report
    if args.format == "html":
        report = generate_html_report(items, args.language, args.since)
    elif args.format == "json":
        report = json.dumps(items, indent=2, ensure_ascii=False)
    else:  # markdown
        report = generate_markdown_report(items, args.language, args.since)

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Report saved to: {args.output}")

        # Auto-open if HTML
        if args.format == "html":
            print(f"🌐 Open in browser: file://{Path(args.output).absolute()}")
    else:
        print(report)


def generate_markdown_report(items: list, language: str, since: str) -> str:
    """Generate Markdown report."""
    lines = [
        f"# 🔥 GitHub Trending {language or 'All Languages'} ({since.capitalize()})",
        f"",
        f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"---",
        f"",
    ]

    for i, item in enumerate(items, 1):
        lines.extend([
            f"### {i}. {item['title']}",
            f"",
            f"**Language**: {item['language']} | **Stars**: ⭐ {item['stars']}",
            f"",
            f"{item['description'][:300]}..." if len(item['description']) > 300 else item['description'],            f"",
            f"🔗 [View on GitHub]({item['url']})",
            f"",
            f"---",
            f"",
        ])

    return '\n'.join(lines)


if __name__ == "__main__":
    main()
