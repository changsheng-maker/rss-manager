"""RSSHub routes module."""

# Popular RSSHub routes organized by platform
RSSHUB_ROUTES = {
    "social": {
        "name": "Social Media",
        "routes": [
            {"path": "/twitter/user/:id", "desc": "Twitter/X user timeline", "example": "/twitter/user/elonmusk"},
            {"path": "/twitter/list/:id/:name", "desc": "Twitter/X list", "example": "/twitter/list/123/members"},
            {"path": "/twitter/followings/:id", "desc": "Twitter/X user followings", "example": "/twitter/followings/elonmusk"},
            {"path": "/twitter/likes/:id", "desc": "Twitter/X user likes", "example": "/twitter/likes/elonmusk"},
            {"path": "/bsky/user/:handle", "desc": "Bluesky user posts", "example": "/bsky/user/bbc.co"},
            {"path": "/mastodon/acct/:acct/statuses/:only_media?", "desc": "Mastodon user timeline", "example": "/mastodon/acct/Gargron@mastodon.social/statuses"},
        ]
    },
    "video": {
        "name": "Video Platforms",
        "routes": [
            {"path": "/youtube/user/:username", "desc": "YouTube user channel", "example": "/youtube/user/@MrBeast"},
            {"path": "/youtube/channel/:id", "desc": "YouTube channel by ID", "example": "/youtube/channel/UCXuqSBlHAE6Xw-yeJA0Tunw"},
            {"path": "/youtube/playlist/:id", "desc": "YouTube playlist", "example": "/youtube/playlist/PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"},
            {"path": "/bilibili/user/video/:uid", "desc": "Bilibili user videos", "example": "/bilibili/user/video/208259"},
            {"path": "/bilibili/user/dynamic/:uid", "desc": "Bilibili user dynamics", "example": "/bilibili/user/dynamic/208259"},
            {"path": "/douyin/user/:uid", "desc": "Douyin user", "example": "/douyin/user/MS4wLjABAAAAVVXOtU-"},
        ]
    },
    "news": {
        "name": "News & Media",
        "routes": [
            {"path": "/reddit/:sort?/:sid?/:route?", "desc": "Reddit", "example": "/reddit/hot/pics"},
            {"path": "/hackernews/:section?/:type?/:user?", "desc": "Hacker News", "example": "/hackernews/top"},
            {"path": "/github/trending/:since/:language?", "desc": "GitHub Trending", "example": "/github/trending/daily/python"},
            {"path": "/github/repos/:user", "desc": "GitHub user repos", "example": "/github/repos/torvalds"},
            {"path": "/github/starred_repos/:user", "desc": "GitHub user starred repos", "example": "/github/starred_repos/torvalds"},
        ]
    },
    "blogs": {
        "name": "Blogs & Articles",
        "routes": [
            {"path": "/medium/user/:uid", "desc": "Medium user articles", "example": "/medium/user/@medium"},
            {"path": "/medium/list/:uid/:listId", "desc": "Medium list", "example": "/medium/list/@medium/123"},
            {"path": "/substack/:username", "desc": "Substack newsletter", "example": "/substack/paulgraham"},
            {"path": "/dev.to/:username", "desc": "Dev.to user articles", "example": "/dev.to/ben"},
            {"path": "/hashnode/:username", "desc": "Hashnode user blog", "example": "/hashnode/johndoe"},
        ]
    },
    "tech": {
        "name": "Tech & Dev",
        "routes": [
            {"path": "/github/issue/:user/:repo/:state?/:labels?", "desc": "GitHub repo issues", "example": "/github/issue/facebook/react/all/bug"},
            {"path": "/github/pull/:user/:repo", "desc": "GitHub repo pull requests", "example": "/github/pull/facebook/react"},
            {"path": "/github/comments/:user/:repo/:type/:number", "desc": "GitHub issue/PR comments", "example": "/github/comments/facebook/react/issue/123"},
            {"path": "/stackoverflow/questions/:query?/:sort?/:tags?", "desc": "Stack Overflow questions", "example": "/stackoverflow/questions/python/newest"},
            {"path": "/producthunt/today", "desc": "Product Hunt today", "example": "/producthunt/today"},
        ]
    },
    "misc": {
        "name": "Miscellaneous",
        "routes": [
            {"path": "/rss/:disableEmbed?/:filter?/:filterout?/:limit?", "desc": "RSSHub transfrom", "example": "/rss/https://example.com/feed"},
            {"path": "/telegram/channel/:username/:routeParams?", "desc": "Telegram channel", "example": "/telegram/channel/durov"},
            {"path": "/telegram/search/:username/:query", "desc": "Telegram channel search", "example": "/telegram/search/durov/announcement"},
            {"path": "/spotify/artist/:id", "desc": "Spotify artist", "example": "/spotify/artist/0TnOYISbd1XYRBk9myaseg"},
            {"path": "/spotify/show/:id", "desc": "Spotify podcast show", "example": "/spotify/show/5CfCWKI5pZ28U0uOzXkDHe"},
            {"path": "/spotify/playlist/:id", "desc": "Spotify playlist", "example": "/spotify/playlist/37i9dQZF1DXcBWIGoYBM5M"},
        ]
    }
}

RSSHUB_BASE_URL = "https://rsshub.app"


def get_all_routes():
    """Get all RSSHub routes."""
    return RSSHUB_ROUTES


def search_routes(query: str) -> list:
    """Search routes by platform name or description."""
    query = query.lower()
    results = []

    for category, data in RSSHUB_ROUTES.items():
        # Search category name
        if query in data["name"].lower():
            results.append({
                "category": category,
                "category_name": data["name"],
                "routes": data["routes"]
            })
            continue

        # Search individual routes
        matching_routes = []
        for route in data["routes"]:
            if query in route["desc"].lower() or query in route["path"].lower():
                matching_routes.append(route)

        if matching_routes:
            results.append({
                "category": category,
                "category_name": data["name"],
                "routes": matching_routes
            })

    return results


def build_rsshub_url(route_path: str, base_url: str = RSSHUB_BASE_URL) -> str:
    """Build a full RSSHub URL from a route path."""
    return f"{base_url}{route_path}"


def get_route_by_platform(platform: str) -> dict:
    """Get routes for a specific platform."""
    platform = platform.lower()

    # Direct category match
    if platform in RSSHUB_ROUTES:
        return {
            "success": True,
            "category": platform,
            "name": RSSHUB_ROUTES[platform]["name"],
            "routes": RSSHUB_ROUTES[platform]["routes"]
        }

    # Search for matching category
    for category, data in RSSHUB_ROUTES.items():
        if platform in data["name"].lower():
            return {
                "success": True,
                "category": category,
                "name": data["name"],
                "routes": data["routes"]
            }

    return {"success": False, "error": f"Platform '{platform}' not found"}


def list_all_platforms() -> list:
    """List all available platforms/categories."""
    return [
        {"id": k, "name": v["name"], "route_count": len(v["routes"])}
        for k, v in RSSHUB_ROUTES.items()
    ]
