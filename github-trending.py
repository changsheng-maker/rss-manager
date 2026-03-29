#!/usr/bin/env python3
"""GitHub Trending Report - Generate HTML report of GitHub trending repositories."""

import argparse
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

import feedparser
from html_generator import HTMLReportGenerator


# GitHub language colors
LANGUAGE_COLORS = {
    "python": "#3572A5", "javascript": "#f1e05a", "typescript": "#2b7489",
    "java": "#b07219", "go": "#00ADD8", "rust": "#dea584", "c++": "#f34b7d",
    "c": "#555555", "c#": "#178600", "ruby": "#701516", "php": "#4F5D95",
    "swift": "#F05138", "kotlin": "#A97BFF", "scala": "#c22d40", "r": "#198CE7",
    "shell": "#89e051", "html": "#e34c26", "css": "#563d7c", "vue": "#41b883",
    "dart": "#00B4AB", "elixir": "#6e4a7e", "haskell": "#5e5086",
    "jupyter notebook": "#DA5B0B", "zig": "#ec915c",
}

TRANSLATIONS = {
    "en": {
        "title": "GitHub Trending",
        "subtitle": "Today's hottest repositories",
        "stars": "stars",
        "daily": "Today",
        "weekly": "This Week",
        "monthly": "This Month",
        "projects": "repositories",
        "generated": "Generated at",
        "language": "Language",
        "no_description": "No description available",
    },
    "zh": {
        "title": "GitHub 排行榜",
        "subtitle": "今日最热门的开源项目",
        "stars": "星",
        "daily": "今日",
        "weekly": "本周",
        "monthly": "本月",
        "projects": "个仓库",
        "generated": "生成于",
        "language": "语言",
        "no_description": "暂无描述",
    }
}


def get_language_color(lang):
    if not lang:
        return "#8b949e"
    return LANGUAGE_COLORS.get(lang.lower(), "#8b949e")


def fetch_github_trending(language: str = "", since: str = "daily") -> list:
    """Fetch GitHub trending via RSSHub or fallback to search API."""
    # Try RSSHub first for actual trending
    if language:
        url = f"https://rsshub.app/github/trending/{since}/{language}"
    else:
        url = f"https://rsshub.app/github/trending/{since}"

    print(f"Fetching GitHub trending: {language or 'all'} ({since})...")

    try:
        feed = feedparser.parse(url, timeout=10)
        if feed.entries and len(feed.entries) > 0:
            return parse_rsshub_entries(feed.entries)
    except Exception as e:
        print(f"RSSHub unavailable: {e}", file=sys.stderr)

    # Fallback: use search API with star velocity
    return fetch_with_star_velocity(language, since)


def parse_rsshub_entries(entries: list) -> list:
    """Parse RSSHub trending entries."""
    items = []
    for i, entry in enumerate(entries, 1):
        # RSSHub provides: title, link, summary, author
        # Title format: "owner/repo: description"
        title = entry.get('title', '')
        parts = title.split(':', 1)
        full_name = parts[0].strip() if parts else title
        name_parts = full_name.split('/')
        owner = name_parts[0] if name_parts else ''
        repo = name_parts[1] if len(name_parts) > 1 else ''

        # Extract stars from summary if available
        stars = 0
        summary = entry.get('summary', entry.get('description', ''))
        import re
        star_match = re.search(r'([\d,]+)\s*⭐|([\d,]+)\s*stars?', summary, re.I)
        if star_match:
            stars = int(star_match.group(1).replace(',', '')) if star_match.group(1) else 0

        # Extract language
        lang_match = re.search(r'\(([^)]+)\)', title)
        language = lang_match.group(1) if lang_match else ''

        items.append({
            'rank': i,
            'name': full_name,
            'owner': owner,
            'repo': repo,
            'url': entry.get('link', ''),
            'description': parts[1].strip() if len(parts) > 1 else '',
            'stars': stars,
            'stars_formatted': f"{stars:,}",
            'stars_growth': '',
            'language': language,
            'language_color': get_language_color(language),
            'topics': [],
        })
    return items


def fetch_with_star_velocity(language: str = "", since: str = "daily") -> list:
    """Fallback: calculate star velocity from search API."""
    now = datetime.now()

    # For daily, get repos created/pushed recently
    if since == "daily":
        date_from = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    elif since == "weekly":
        date_from = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    else:
        date_from = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    # Query for recently active repos
    query_parts = [f"pushed:>{date_from}", "stars:>100"]
    if language:
        query_parts.append(f"language:{language}")

    query = " ".join(query_parts)
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=50"

    print("Using GitHub API fallback (star velocity)...")

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "RSS-Manager"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = []

            for repo in data.get('items', []):
                # Calculate star velocity (stars per day since creation)
                created = repo.get('created_at', '')
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        days = max(1, (now - created_dt.replace(tzinfo=None)).days)
                        velocity = repo['stargazers_count'] / days
                    except:
                        velocity = repo['stargazers_count'] / 30
                else:
                    velocity = repo['stargazers_count'] / 30

                items.append({
                    'rank': 0,  # Will be set after sorting
                    'name': repo['full_name'],
                    'owner': repo['owner']['login'],
                    'repo': repo['name'],
                    'url': repo['html_url'],
                    'description': repo.get('description') or '',
                    'stars': repo['stargazers_count'],
                    'stars_formatted': f"{repo['stargazers_count']:,}",
                    'stars_growth': f"{int(velocity)}",
                    'language': repo.get('language') or 'Unknown',
                    'language_color': get_language_color(repo.get('language')),
                    'topics': repo.get('topics', [])[:3],
                })

            # Sort by star velocity (growth rate)
            items.sort(key=lambda x: int(x['stars_growth']) if x['stars_growth'] else 0, reverse=True)

            # Assign ranks
            for i, item in enumerate(items, 1):
                item['rank'] = i

            return items[:25]

    except Exception as e:
        print(f"API fallback failed: {e}", file=sys.stderr)
        return []


def generate_html(items: list, language: str, since: str, lang: str = "zh") -> str:
    """Generate HTML report with i18n."""
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    period_labels = {
        "daily": t["daily"],
        "weekly": t["weekly"],
        "monthly": t["monthly"]
    }

    title = f"{t['title']} {language or t.get('all', 'All')}"
    subtitle = f"{period_labels.get(since, since)} - {t['subtitle']}"

    generator = HTMLReportGenerator()
    return generator.generate_github_trending_html(
        title=title,
        subtitle=subtitle,
        items=items,
        lang=lang
    )


def main():
    parser = argparse.ArgumentParser(description="GitHub Trending Report Generator")
    parser.add_argument("-l", "--language", default="", help="Programming language filter")
    parser.add_argument("-s", "--since", choices=["daily", "weekly", "monthly"], default="daily", help="Time period")
    parser.add_argument("-n", "--limit", type=int, default=20, help="Number of repos")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--lang", choices=["en", "zh"], default="zh", help="Language: en or zh")

    args = parser.parse_args()

    entries = fetch_github_trending(args.language, args.since)

    if not entries:
        print("❌ No trending repositories found")
        sys.exit(1)

    entries = entries[:args.limit]

    report = generate_html(entries, args.language, args.since, args.lang)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Saved to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()