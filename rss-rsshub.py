#!/usr/bin/env python3
"""RSSHub browser command."""
import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib.rsshub import (
    get_all_routes,
    search_routes,
    get_route_by_platform,
    list_all_platforms,
    build_rsshub_url,
    RSSHUB_BASE_URL
)


def main():
    parser = argparse.ArgumentParser(
        description="Browse and discover RSSHub routes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rss-rsshub.py --list
  python rss-rsshub.py --platform social
  python rss-rsshub.py --search twitter
  python rss-rsshub.py --build /twitter/user/elonmusk
        """
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available platforms"
    )
    parser.add_argument(
        "-p", "--platform",
        help="Show routes for a specific platform (e.g., social, youtube, github)"
    )
    parser.add_argument(
        "-s", "--search",
        help="Search routes by keyword"
    )
    parser.add_argument(
        "-b", "--build",
        help="Build full RSSHub URL from route path"
    )
    parser.add_argument(
        "--base-url",
        default=RSSHUB_BASE_URL,
        help=f"RSSHub base URL (default: {RSSHUB_BASE_URL})"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Default to list if no args
    if not any([args.list, args.platform, args.search, args.build]):
        args.list = True

    if args.list:
        platforms = list_all_platforms()
        if args.json:
            print(json.dumps({"success": True, "platforms": platforms}, indent=2))
            return

        print("Available RSSHub Platforms:")
        print("-" * 50)
        for p in platforms:
            print(f"  {p['id']:<15} {p['name']:<20} ({p['route_count']} routes)")
        print(f"\nUse --platform <id> to see routes for a specific platform")
        return

    if args.platform:
        result = get_route_by_platform(args.platform)
        if args.json:
            print(json.dumps(result, indent=2))
            return

        if not result["success"]:
            print(f"Error: {result.get('error', 'Platform not found')}")
            print(f"\nUse --list to see available platforms")
            sys.exit(1)

        print(f"\n{result['name']} Routes:")
        print("-" * 80)
        for route in result["routes"]:
            print(f"\n  Path: {route['path']}")
            print(f"  Description: {route['desc']}")
            print(f"  Example: {args.base_url}{route['example']}")
        return

    if args.search:
        results = search_routes(args.search)
        if args.json:
            print(json.dumps({"success": True, "query": args.search, "results": results}, indent=2))
            return

        if not results:
            print(f"No routes found matching '{args.search}'")
            return

        print(f"Search results for '{args.search}':")
        print("-" * 80)
        for r in results:
            print(f"\n[{r['category_name']}]")
            for route in r["routes"]:
                print(f"  {route['path']}")
                print(f"    {route['desc']}")
                print(f"    Example: {args.base_url}{route['example']}")
        return

    if args.build:
        url = build_rsshub_url(args.build, args.base_url)
        result = {"success": True, "route": args.build, "url": url}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"RSSHub URL: {url}")
        return


if __name__ == "__main__":
    main()
