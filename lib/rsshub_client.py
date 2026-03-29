"""RSSHub Client Module.

This module provides integration with RSSHub, an open-source RSS feed generator
that can create RSS feeds from various websites. It supports listing popular
routes by category, building RSSHub URLs from templates, and caching route
definitions.

Example:
    >>> from rsshub_client import RSSHubClient
    >>> client = RSSHubClient()
    >>> # Build URL for GitHub trending
    >>> url = client.build_url("github/trending", language="python")
    >>> # List available categories
    >>> categories = client.list_categories()
"""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, urljoin

import requests


@dataclass
class RSSHubRoute:
    """Represents an RSSHub route definition.

    Attributes:
        path: Route path (e.g., 'github/trending/:language').
        name: Human-readable name of the route.
        description: Route description.
        parameters: Dict of parameter definitions.
        example: Example URL or parameters.
        categories: List of categories this route belongs to.
    """
    path: str
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    example: str = ""
    categories: List[str] = field(default_factory=list)

    def get_required_params(self) -> List[str]:
        """Get list of required parameters for this route."""
        required = []
        for param, config in self.parameters.items():
            if isinstance(config, dict) and config.get("required", False):
                required.append(param)
        return required

    def get_optional_params(self) -> List[str]:
        """Get list of optional parameters for this route."""
        optional = []
        for param, config in self.parameters.items():
            if isinstance(config, dict) and not config.get("required", False):
                optional.append(param)
            elif not isinstance(config, dict):
                optional.append(param)
        return optional


class RSSHubClient:
    """Client for RSSHub RSS feed generator.

    This class provides methods to interact with RSSHub instances, build URLs
    from route templates, and manage cached route definitions.

    Attributes:
        base_url: Base URL of the RSSHub instance.
        timeout: Request timeout in seconds.
        cache_dir: Directory for caching route definitions.
        cache_ttl: Cache time-to-live in seconds.
    """

    # Default RSSHub instance
    DEFAULT_INSTANCE = "https://rsshub.app"

    # Common RSSHub routes organized by category
    COMMON_ROUTES = {
        "social": {
            "twitter/user": {
                "name": "Twitter User Timeline",
                "description": "Get tweets from a specific Twitter/X user",
                "parameters": {
                    "id": {"required": True, "description": "Twitter username"},
                    "filter": {"required": False, "description": "Filter tweets by keywords"},
                },
                "example": "/twitter/user/elonmusk",
            },
            "telegram/channel": {
                "name": "Telegram Channel",
                "description": "Get messages from a Telegram channel",
                "parameters": {
                    "username": {"required": True, "description": "Channel username"},
                },
                "example": "/telegram/channel/durov",
            },
            "mastodon/account": {
                "name": "Mastodon Account",
                "description": "Get toots from a Mastodon account",
                "parameters": {
                    "site": {"required": True, "description": "Mastodon instance domain"},
                    "account_id": {"required": True, "description": "Account ID"},
                },
                "example": "/mastodon/account/mastodon.social/12345",
            },
        },
        "news": {
            "hackernews": {
                "name": "Hacker News",
                "description": "Hacker News stories",
                "parameters": {
                    "section": {"required": False, "description": "hot, new, best, ask, show, jobs"},
                },
                "example": "/hackernews/best",
            },
            "reddit": {
                "name": "Reddit",
                "description": "Reddit posts from a subreddit",
                "parameters": {
                    "subreddit": {"required": True, "description": "Subreddit name"},
                    "sort": {"required": False, "description": "hot, new, top, rising"},
                },
                "example": "/reddit/r/programming",
            },
        },
        "dev": {
            "github/trending": {
                "name": "GitHub Trending",
                "description": "Trending repositories on GitHub",
                "parameters": {
                    "language": {"required": False, "description": "Programming language"},
                    "since": {"required": False, "description": "daily, weekly, monthly"},
                },
                "example": "/github/trending/python/weekly",
            },
            "github/repos": {
                "name": "GitHub Repository Releases",
                "description": "Get releases from a GitHub repository",
                "parameters": {
                    "user": {"required": True, "description": "Repository owner"},
                    "repo": {"required": True, "description": "Repository name"},
                },
                "example": "/github/repos/microsoft/vscode",
            },
            "github/issues": {
                "name": "GitHub Repository Issues",
                "description": "Get issues from a GitHub repository",
                "parameters": {
                    "user": {"required": True, "description": "Repository owner"},
                    "repo": {"required": True, "description": "Repository name"},
                    "state": {"required": False, "description": "open, closed, all"},
                },
                "example": "/github/issues/facebook/react/open",
            },
        },
        "video": {
            "youtube/user": {
                "name": "YouTube User",
                "description": "Get videos from a YouTube user",
                "parameters": {
                    "username": {"required": True, "description": "YouTube username or channel ID"},
                },
                "example": "/youtube/user/GoogleDevelopers",
            },
            "youtube/playlist": {
                "name": "YouTube Playlist",
                "description": "Get videos from a YouTube playlist",
                "parameters": {
                    "id": {"required": True, "description": "Playlist ID"},
                },
                "example": "/youtube/playlist/PL...",
            },
            "bilibili/user": {
                "name": "Bilibili User",
                "description": "Get videos from a Bilibili user",
                "parameters": {
                    "uid": {"required": True, "description": "User ID"},
                },
                "example": "/bilibili/user/208259",
            },
        },
        "blog": {
            "medium/user": {
                "name": "Medium User",
                "description": "Get articles from a Medium user",
                "parameters": {
                    "username": {"required": True, "description": "Medium username"},
                },
                "example": "/medium/user/@username",
            },
            "medium/tag": {
                "name": "Medium Tag",
                "description": "Get articles by Medium tag",
                "parameters": {
                    "tag": {"required": True, "description": "Tag name"},
                },
                "example": "/medium/tag/programming",
            },
        },
        "live": {
            "twitch/live": {
                "name": "Twitch Live Streams",
                "description": "Get live streams from Twitch users",
                "parameters": {
                    "login": {"required": True, "description": "Streamer login name"},
                },
                "example": "/twitch/live/shroud",
            },
        },
        "shopping": {
            "amazon/price": {
                "name": "Amazon Price Tracker",
                "description": "Track price changes on Amazon products",
                "parameters": {
                    "id": {"required": True, "description": "Product ASIN"},
                },
                "example": "/amazon/price/B08N5WRWNW",
            },
        },
        "finance": {
            "bilibili/blackboard": {
                "name": "Bilibili Blackboard",
                "description": "Bilibili official announcements",
                "parameters": {},
                "example": "/bilibili/blackboard",
            },
        },
    }

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours
    ):
        """Initialize the RSSHubClient instance.

        Args:
            base_url: Base URL of the RSSHub instance.
            timeout: Request timeout in seconds.
            cache_dir: Directory for caching route definitions.
            cache_ttl: Cache time-to-live in seconds.
        """
        self.base_url = (base_url or self.DEFAULT_INSTANCE).rstrip("/")
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        })

        # Setup cache directory
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = os.path.expanduser("~/.cache/rss-manager/rsshub")
        os.makedirs(self.cache_dir, exist_ok=True)

        self._routes_cache: Optional[Dict[str, Any]] = None

    def _get_cache_path(self) -> str:
        """Get path to routes cache file."""
        return os.path.join(self.cache_dir, "routes.json")

    def _load_cached_routes(self) -> Optional[Dict[str, Any]]:
        """Load routes from cache if valid.

        Returns:
            Cached routes dict or None if expired/missing.
        """
        cache_path = self._get_cache_path()

        if not os.path.exists(cache_path):
            return None

        # Check if cache is expired
        mtime = os.path.getmtime(cache_path)
        if time.time() - mtime > self.cache_ttl:
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _save_cached_routes(self, routes: Dict[str, Any]) -> None:
        """Save routes to cache.

        Args:
            routes: Routes dictionary to cache.
        """
        cache_path = self._get_cache_path()
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(routes, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def fetch_routes(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch route definitions from RSSHub instance.

        Args:
            force_refresh: Force refresh cache from server.

        Returns:
            Dictionary of route definitions by category.
        """
        if not force_refresh:
            cached = self._load_cached_routes()
            if cached is not None:
                self._routes_cache = cached
                return cached

        # Try to fetch from RSSHub API
        try:
            response = self.session.get(
                f"{self.base_url}/api/routes",
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    self._save_cached_routes(data["data"])
                    self._routes_cache = data["data"]
                    return data["data"]
        except requests.RequestException:
            pass

        # Fall back to common routes
        self._routes_cache = self.COMMON_ROUTES
        return self.COMMON_ROUTES

    def list_categories(self) -> List[str]:
        """List all available route categories.

        Returns:
            List of category names.
        """
        routes = self.fetch_routes()
        return sorted(routes.keys())

    def list_routes(self, category: Optional[str] = None) -> List[RSSHubRoute]:
        """List available routes, optionally filtered by category.

        Args:
            category: Optional category to filter by.

        Returns:
            List of RSSHubRoute objects.
        """
        routes = self.fetch_routes()
        result = []

        if category:
            if category in routes:
                for path, config in routes[category].items():
                    route = RSSHubRoute(
                        path=path,
                        name=config.get("name", ""),
                        description=config.get("description", ""),
                        parameters=config.get("parameters", {}),
                        example=config.get("example", ""),
                        categories=[category],
                    )
                    result.append(route)
        else:
            for cat, cat_routes in routes.items():
                for path, config in cat_routes.items():
                    route = RSSHubRoute(
                        path=path,
                        name=config.get("name", ""),
                        description=config.get("description", ""),
                        parameters=config.get("parameters", {}),
                        example=config.get("example", ""),
                        categories=[cat],
                    )
                    result.append(route)

        return sorted(result, key=lambda r: r.name)

    def get_route(self, path: str) -> Optional[RSSHubRoute]:
        """Get a specific route by path.

        Args:
            path: Route path (e.g., 'github/trending').

        Returns:
            RSSHubRoute object or None if not found.
        """
        routes = self.fetch_routes()

        for category, cat_routes in routes.items():
            if path in cat_routes:
                config = cat_routes[path]
                return RSSHubRoute(
                    path=path,
                    name=config.get("name", ""),
                    description=config.get("description", ""),
                    parameters=config.get("parameters", {}),
                    example=config.get("example", ""),
                    categories=[category],
                )

        return None

    def build_url(
        self,
        route: str,
        **kwargs: Union[str, int, float, bool]
    ) -> str:
        """Build RSSHub URL from route and parameters.

        Args:
            route: Route path (e.g., 'github/trending').
            **kwargs: Route parameters.

        Returns:
            Full RSSHub URL.

        Example:
            >>> client.build_url("github/trending", language="python", since="weekly")
            "https://rsshub.app/github/trending/python/weekly"
        """
        # Split route path and build URL
        path_parts = route.strip("/").split("/")

        # Build path with parameters
        result_path = []
        param_values = list(kwargs.values())
        param_idx = 0

        for part in path_parts:
            if part.startswith(":"):
                # This is a parameter placeholder
                if param_idx < len(param_values):
                    result_path.append(str(param_values[param_idx]))
                    param_idx += 1
            else:
                result_path.append(part)

        # Add remaining parameters as query string
        remaining_params = {}
        route_def = self.get_route(route)

        if route_def:
            required = route_def.get_required_params()
            optional = route_def.get_optional_params()

            for key, value in kwargs.items():
                if key in required or key in optional:
                    # Check if already used in path
                    if key not in route or f":{key}" not in route:
                        remaining_params[key] = value

        path = "/".join(result_path)
        url = f"{self.base_url}/{path}"

        if remaining_params:
            url += "?" + urlencode(remaining_params)

        return url

    def search_routes(self, query: str) -> List[RSSHubRoute]:
        """Search routes by keyword.

        Args:
            query: Search query string.

        Returns:
            List of matching RSSHubRoute objects.
        """
        query_lower = query.lower()
        all_routes = self.list_routes()
        matches = []

        for route in all_routes:
            # Search in name, description, and path
            if (
                query_lower in route.name.lower()
                or query_lower in route.description.lower()
                or query_lower in route.path.lower()
            ):
                matches.append(route)

        return matches

    def clear_cache(self) -> bool:
        """Clear the routes cache.

        Returns:
            True if cache was cleared, False otherwise.
        """
        cache_path = self._get_cache_path()
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
            self._routes_cache = None
            return True
        except IOError:
            return False

    def get_popular_routes(self, limit: int = 20) -> List[RSSHubRoute]:
        """Get list of popular/most-used routes.

        Args:
            limit: Maximum number of routes to return.

        Returns:
            List of popular RSSHubRoute objects.
        """
        popular_paths = [
            "twitter/user",
            "youtube/user",
            "github/trending",
            "hackernews",
            "reddit",
            "telegram/channel",
            "medium/user",
            "github/repos",
        ]

        routes = []
        for path in popular_paths[:limit]:
            route = self.get_route(path)
            if route:
                routes.append(route)

        return routes
