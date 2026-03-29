#!/usr/bin/env python3
"""GitHub Trending Report v2 - Generate HTML report of GitHub trending repositories with curation."""

import argparse
import sys
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent / "lib"))

import feedparser
from html_generator import HTMLReportGenerator


# GitHub language colors (official GitHub colors)
LANGUAGE_COLORS = {
    "python": "#3572A5",
    "javascript": "#f1e05a",
    "typescript": "#2b7489",
    "java": "#b07219",
    "go": "#00ADD8",
    "rust": "#dea584",
    "c++": "#f34b7d",
    "c": "#555555",
    "c#": "#178600",
    "ruby": "#701516",
    "php": "#4F5D95",
    "swift": "#F05138",
    "kotlin": "#A97BFF",
    "scala": "#c22d40",
    "r": "#198CE7",
    "shell": "#89e051",
    "html": "#e34c26",
    "css": "#563d7c",
    "vue": "#41b883",
    "dart": "#00B4AB",
    "elixir": "#6e4a7e",
    "haskell": "#5e5086",
    "julia": "#a270ba",
    "lua": "#000080",
    "perl": "#0298c3",
    "clojure": "#db5855",
    "erlang": "#B83998",
    "ocaml": "#3be133",
    "objective-c": "#438eff",
    "jupyter notebook": "#DA5B0B",
    "solidity": "#AA6746",
    "zig": "#ec915c",
}


def get_language_color(language: str) -> str:
    """Get the GitHub color for a programming language."""
    if not language:
        return "#8b949e"  # GitHub's default gray
    return LANGUAGE_COLORS.get(language.lower(), "#8b949e")


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

    # Fallback: Use GitHub Search API for actively maintained repos
    return fetch_github_trending_fallback(language, since)


def fetch_github_trending_fallback(language: str = "", since: str = "daily") -> list:
    """Fallback using GitHub Search API - find actively maintained trending repos.

    Changes from v1:
    - Uses 'pushed:>' instead of 'created:>' to find actively maintained repos
    - Adds secondary sorting by updated date
    - Extracts topics, language color, and more metadata
    - Calculates star velocity when possible
    """
    # Calculate date thresholds for activity filtering
    now = datetime.now()
    if since == "daily":
        pushed_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        min_stars_threshold = 50
    elif since == "weekly":
        pushed_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        min_stars_threshold = 100
    else:  # monthly
        pushed_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        min_stars_threshold = 200

    # Build query: actively pushed repos with stars (not just recently created)
    query_parts = [f"pushed:>{pushed_date}", "stars:>50"]
    if language:
        query_parts.append(f"language:{language}")

    query = " ".join(query_parts)
    # Sort by stars primarily, but we could also use 'updated' for recent activity
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=50"

    print(f"Using GitHub Search API fallback (actively maintained repos)...")

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
            # Convert to feed-like entries with enhanced metadata
            entries = []
            for repo in data.get('items', []):
                # Calculate star velocity if created_at is available
                star_velocity = None
                created_at = repo.get('created_at')
                if created_at:
                    try:
                        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        days_since_creation = (now - created_dt.replace(tzinfo=None)).days
                        if days_since_creation > 0:
                            star_velocity = repo['stargazers_count'] // days_since_creation
                    except:
                        pass

                # Build enhanced entry with all metadata
                entry = {
                    'title': f"{repo['full_name']}: {repo['description'] or 'No description'} ({repo['language'] or 'Unknown'}) ⭐ {repo['stargazers_count']:,}",
                    'link': repo['html_url'],
                    'description': repo['description'] or '',
                    # Additional metadata for v2
                    '_api_metadata': {
                        'full_name': repo['full_name'],
                        'owner': repo['owner']['login'],
                        'repo': repo['name'],
                        'stars': repo['stargazers_count'],
                        'language': repo['language'] or 'Unknown',
                        'topics': repo.get('topics', []),
                        'updated_at': repo.get('pushed_at', repo.get('updated_at')),
                        'created_at': repo.get('created_at'),
                        'star_velocity': star_velocity,
                        'forks': repo.get('forks_count', 0),
                        'open_issues': repo.get('open_issues_count', 0),
                        'is_api_response': True,
                    }
                }
                entries.append(entry)
            return entries
    except Exception as e:
        print(f"GitHub API fallback also failed: {e}", file=sys.stderr)
        return []


def parse_github_entry(entry) -> dict:
    """Parse GitHub trending entry into structured data.

    Handles both RSSHub format (v1) and enhanced GitHub API format (v2).
    Returns a standardized data structure with all metadata fields.
    """
    title = entry.get('title', '')
    link = entry.get('link', '')
    description = entry.get('description', '')

    # Check if this is an API response with enhanced metadata
    api_meta = entry.get('_api_metadata', {})

    if api_meta.get('is_api_response'):
        # Enhanced API format
        owner = api_meta['owner']
        repo = api_meta['repo']
        full_name = api_meta['full_name']
        stars = api_meta['stars']
        language = api_meta['language']
        topics = api_meta.get('topics', [])
        star_velocity = api_meta.get('star_velocity')
        updated_at = api_meta.get('updated_at')
    else:
        # RSSHub format - parse from title
        # Format: "user/repo: Description (Language) ⭐ Stars"
        full_name_match = re.match(r'^([^:]+):', title)
        full_name = full_name_match.group(1) if full_name_match else ''

        if '/' in full_name:
            parts = full_name.split('/')
            owner = parts[0]
            repo = parts[1] if len(parts) > 1 else ''
        else:
            owner = ''
            repo = full_name

        # Extract language
        lang_match = re.search(r'\(([^)]+)\)', title)
        language = lang_match.group(1) if lang_match else 'Unknown'

        # Extract stars
        stars_match = re.search(r'[\d,]+', title.split('⭐')[-1] if '⭐' in title else '')
        stars_str = stars_match.group().replace(',', '') if stars_match else '0'
        try:
            stars = int(stars_str)
        except:
            stars = 0

        topics = []
        star_velocity = None
        updated_at = None

    # Build standardized data structure
    data = {
        'rank': 0,  # Will be set by curate_trending_items
        'name': full_name,
        'owner': owner,
        'repo': repo,
        'url': link,
        'description': description,
        'stars': stars,
        'stars_formatted': f"{stars:,}",
        'stars_growth': star_velocity,
        'language': language,
        'language_color': get_language_color(language),
        'topics': topics,
        'updated_at': updated_at,
        'category': 'GitHub Trending',
        # Legacy fields for backward compatibility
        'title': title,
    }

    return data


def calculate_repo_score(item: dict) -> float:
    """Calculate a curation score for a repository.

    Scoring factors:
    - Star count (weighted logarithmically to avoid mega-repos dominating)
    - Star velocity (stars per day) - high growth potential
    - Has description (quality signal)
    - Has topics (maintained, categorized)
    - Recent activity (based on updated_at)
    """
    score = 0.0

    # Star count (logarithmic scale to prevent mega-repos from dominating)
    stars = item.get('stars', 0)
    score += min(30, (stars ** 0.5) * 2)  # Cap at 30 points

    # Star velocity bonus (high growth potential is interesting)
    velocity = item.get('stars_growth')
    if velocity:
        score += min(25, velocity * 0.5)  # Cap at 25 points
    elif stars < 500:
        # Small repos without velocity data get a small boost
        score += 5

    # Quality signals
    description = item.get('description', '')
    if description and len(description) > 20:
        score += 10  # Good description

    topics = item.get('topics', [])
    if topics:
        score += 5 * min(3, len(topics))  # Up to 15 points for having topics

    # Language diversity bonus (slight preference for interesting languages)
    language = item.get('language', '').lower()
    interesting_langs = {'rust', 'go', 'zig', 'elixir', 'kotlin', 'swift', 'dart'}
    if language in interesting_langs:
        score += 3

    # Recency bonus if we have updated_at
    updated_at = item.get('updated_at')
    if updated_at:
        try:
            # Parse ISO format
            updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00').replace('+00:00', ''))
            days_since_update = (datetime.now() - updated_dt).days
            if days_since_update < 1:
                score += 10  # Updated today
            elif days_since_update < 3:
                score += 5   # Updated in last 3 days
        except:
            pass

    return score


def curate_trending_items(items: list, limit: int = 25) -> list:
    """Curate and rank trending items based on multiple quality signals.

    Instead of just sorting by star count, this function:
    1. Filters out very small repos (< 50 stars) unless high growth
    2. Scores repos based on multiple factors
    3. Returns the top N most interesting repos
    """
    if not items:
        return []

    # Filter out very small repos that aren't growing fast
    filtered = []
    for item in items:
        stars = item.get('stars', 0)
        velocity = item.get('stars_growth')

        # Keep if:
        # - Has 50+ stars, OR
        # - Has 20+ stars with velocity > 5/day, OR
        # - Has any velocity data showing growth
        if stars >= 50:
            filtered.append(item)
        elif stars >= 20 and velocity and velocity >= 5:
            filtered.append(item)
        elif velocity and velocity >= 10:
            filtered.append(item)

    # If filtering removed too many, relax constraints
    if len(filtered) < min(limit, len(items)):
        filtered = items

    # Score and sort
    scored_items = [(item, calculate_repo_score(item)) for item in filtered]
    scored_items.sort(key=lambda x: x[1], reverse=True)

    # Take top N and assign ranks
    result = []
    for rank, (item, score) in enumerate(scored_items[:limit], 1):
        item['rank'] = rank
        item['_curation_score'] = round(score, 1)  # Debug info
        result.append(item)

    return result


def generate_html_report(items: list, language: str, since: str) -> str:
    """Generate HTML report with enhanced metadata display."""
    generator = HTMLReportGenerator(
        title=f"GitHub Trending {language or 'All Languages'} - {since.capitalize()}"
    )

    # Convert items to standard format with enhanced display
    formatted_items = []
    for item in items:
        # Build rich source field with metadata
        source_parts = [f"⭐ {item.get('stars_formatted', 'N/A')} stars"]

        if item.get('stars_growth'):
            source_parts.append(f"+{item['stars_growth']}/day")

        if item.get('topics'):
            topic_str = ', '.join(item['topics'][:3])  # Top 3 topics
            source_parts.append(f"#{topic_str}")

        formatted_item = {
            'title': f"#{item.get('rank', 0)} {item.get('name', 'No title')}",
            'url': item.get('url', ''),
            'summary': item.get('description', '')[:200] + '...' if len(item.get('description', '')) > 200 else item.get('description', ''),
            'source': ' | '.join(source_parts),
            'published': f"<span style='color:{item.get('language_color', '#8b949e')}'>{item.get('language', 'Unknown')}</span>",
            'category': item.get('category', 'GitHub Trending')
        }
        formatted_items.append(formatted_item)

    return generator.generate_github_trending_html(
        title=f"GitHub Trending {language or 'All Languages'} - {since.capitalize()}",
        subtitle="Discover the most interesting open source projects",
        items=items
    )


def generate_json_output(items: list) -> str:
    """Generate JSON output with full metadata."""
    # Clean up internal fields
    output_items = []
    for item in items:
        clean_item = {
            'rank': item.get('rank'),
            'name': item.get('name'),
            'owner': item.get('owner'),
            'repo': item.get('repo'),
            'url': item.get('url'),
            'description': item.get('description'),
            'stars': item.get('stars'),
            'stars_formatted': item.get('stars_formatted'),
            'stars_growth': item.get('stars_growth'),
            'language': item.get('language'),
            'language_color': item.get('language_color'),
            'topics': item.get('topics'),
            'updated_at': item.get('updated_at'),
        }
        output_items.append(clean_item)

    return json.dumps(output_items, indent=2, ensure_ascii=False)


def generate_markdown_report(items: list, language: str, since: str) -> str:
    """Generate Markdown report with enhanced formatting."""
    lines = [
        f"# 🔥 GitHub Trending {language or 'All Languages'} ({since.capitalize()})",
        f"",
        f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"---",
        f"",
    ]

    for item in items:
        # Build metadata line
        meta_parts = [f"**Language**: {item.get('language', 'Unknown')}"]
        meta_parts.append(f"**Stars**: ⭐ {item.get('stars_formatted', 'N/A')}")

        if item.get('stars_growth'):
            meta_parts.append(f"**Growth**: +{item['stars_growth']} stars/day")

        if item.get('topics'):
            topics_str = ' | '.join([f"`{t}`" for t in item['topics'][:5]])
            meta_parts.append(f"**Topics**: {topics_str}")

        lines.extend([
            f"### #{item.get('rank', 0)}. {item['name']}",
            f"",
            ' | '.join(meta_parts),
            f"",
            f"{item['description'][:300]}..." if len(item.get('description', '')) > 300 else item.get('description', ''),
            f"",
            f"🔗 [View on GitHub]({item['url']})",
            f"",
            f"---",
            f"",
        ])

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate GitHub trending report with curation (v2)",
        epilog="""
Examples:
  python github-trending-v2.py                    # Today's trending (curated)
  python github-trending-v2.py --language python  # Python trending
  python github-trending-v2.py --since weekly     # Weekly trending
  python github-trending-v2.py --language rust --limit 10
  python github-trending-v2.py --output ~/github-trending.html --format html
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
        help="Output file path"
    )
    parser.add_argument(
        "--format",
        choices=["html", "json", "markdown"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--no-curation",
        action="store_true",
        help="Disable curation, sort by stars only"
    )

    args = parser.parse_args()

    # Fetch trending repos
    entries = fetch_github_trending(args.language, args.since)

    if not entries:
        print("❌ No trending repositories found or RSSHub unavailable.")
        print("💡 Try using native GitHub trending instead:")
        print("   https://github.com/trending")
        sys.exit(1)

    # Parse entries into structured data
    items = [parse_github_entry(e) for e in entries]

    # Apply curation if enabled (default)
    if args.no_curation:
        # Sort by stars only, assign ranks
        items.sort(key=lambda x: x.get('stars', 0), reverse=True)
        for rank, item in enumerate(items[:args.limit], 1):
            item['rank'] = rank
        items = items[:args.limit]
    else:
        items = curate_trending_items(items, limit=args.limit)

    # Generate report
    if args.format == "html":
        report = generate_html_report(items, args.language, args.since)
    elif args.format == "json":
        report = generate_json_output(items)
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


if __name__ == "__main__":
    main()
