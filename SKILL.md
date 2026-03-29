# RSS Manager

A comprehensive RSS feed management skill for Claude Code. Discover, organize, and maintain your RSS feed subscriptions with automatic feed detection, RSSHub integration, and OPML import/export support.

## Installation

This skill is automatically available once placed in your `~/.claude/skills/` directory. No additional dependencies required.

### Setup

1. Ensure the skill is installed at `~/.claude/skills/rss-manager/`
2. The skill will be automatically detected by Claude Code on next startup
3. Data is stored in `~/.claude/skills/rss-manager/data/feeds.json`

## Commands

### `rss-discover <url>`

Discover RSS feeds from any website. Automatically detects RSS, Atom, and JSON feeds.

**Examples:**
```
/rss-discover https://example.com
/rss-discover https://news.ycombinator.com
/rss-discover https://github.com/microsoft/vscode
```

**Output:** List of discovered feeds with titles, URLs, and feed types.

### `rss-add <url> [name]`

Add a feed to your personal collection. Optionally provide a custom name.

**Examples:**
```
/rss-add https://news.ycombinator.com/rss "Hacker News"
/rss-add https://feeds.arstechnica.com/arstechnica/index
/rss-add https://rsshub.app/github/repos/microsoft
```

**Features:**
- Auto-validates feed before adding
- Fetches feed metadata (title, description)
- Checks for duplicates
- Assigns unique ID for management

### `rss-list`

Display all subscribed feeds with metadata.

**Output:**
- Feed ID
- Title
- URL
- Last checked date
- Status (active/error)
- Item count

**Options:**
- Filter by category
- Sort by name or date added
- Show only error feeds

### `rss-remove <id-or-url>`

Remove a feed by its ID or URL.

**Examples:**
```
/rss-remove 5
/rss-remove https://example.com/feed.xml
```

**Safety:** Confirmation prompt before deletion. Option to export before removing.

### `rss-import <filepath>`

Import feeds from an OPML file.

**Examples:**
```
/rss-import ~/Downloads/feeds.opml
/rss-import ~/backup/my-feeds.opml
```

**Features:**
- Preserves folder structure as categories
- Skips duplicates
- Reports import statistics
- Validates feed URLs

### `rss-export [filepath]`

Export your feed collection to OPML format.

**Examples:**
```
/rss-export
/rss-export ~/backups/feeds-2024.opml
```

**Output:** Standard OPML 2.0 file compatible with most RSS readers.

### `rss-rsshub [query]`

Browse and discover RSSHub routes. Search for specific services or platforms.

**Examples:**
```
/rss-rsshub
/rss-rsshub github
/rss-rsshub twitter
/rss-rsshub youtube
```

**Features:**
- Browse by category (Social Media, Development, Multimedia, etc.)
- Shows route parameters
- Generates ready-to-use RSSHub URLs
- Links to full RSSHub documentation

## Configuration

Configuration file: `~/.claude/skills/rss-manager/config.json`

```json
{
  "dataDirectory": "~/.claude/skills/rss-manager/data",
  "defaultFeedLimit": 100,
  "autoRefresh": false,
  "refreshInterval": 3600,
  "userAgent": "RSS-Manager/1.0",
  "rsshub": {
    "instance": "https://rsshub.app",
    "accessKey": null
  }
}
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `dataDirectory` | Where feed data is stored | `~/.claude/skills/rss-manager/data` |
| `defaultFeedLimit` | Max items to fetch per feed | 100 |
| `autoRefresh` | Auto-refresh feeds on startup | false |
| `refreshInterval` | Seconds between refreshes | 3600 (1 hour) |
| `userAgent` | HTTP User-Agent string | RSS-Manager/1.0 |
| `rsshub.instance` | RSSHub instance URL | https://rsshub.app |
| `rsshub.accessKey` | API key for private RSSHub | null |

## Troubleshooting

### Feed Discovery Fails

**Problem:** URL returns no feeds found

**Solutions:**
1. Verify the URL is accessible: `curl -I <url>`
2. Some sites block automated requests - try adding trailing slash
3. Check if site requires JavaScript (feeds may be dynamically loaded)
4. Manually inspect page source for `application/rss+xml` or `application/atom+xml`

### Feed Validation Errors

**Problem:** Feed adds but shows error status

**Solutions:**
1. Verify feed URL is directly accessible
2. Check if feed requires authentication
3. Some feeds use non-standard formats - try Feed Validator: https://validator.w3.org/feed/
4. Check for Cloudflare or bot protection

### OPML Import Issues

**Problem:** OPML import fails or imports zero feeds

**Solutions:**
1. Verify OPML file format: should be OPML 1.0 or 2.0
2. Check XML is well-formed: `xmllint --noout file.opml`
3. Ensure outline elements have `xmlUrl` attributes
4. Try opening in another RSS reader to verify file integrity

### RSSHub Routes Not Working

**Problem:** RSSHub route returns 404 or error

**Solutions:**
1. Check route exists at https://docs.rsshub.app
2. Some routes require parameters (username, channel ID, etc.)
3. Route may require authentication - check docs.rsshub.app for access key setup
4. RSSHub instance may be rate-limited - consider self-hosting

### Data Location

All data stored in:
```
~/.claude/skills/rss-manager/
├── data/
│   ├── feeds.json       # Feed subscriptions
│   ├── categories.json  # Category definitions
│   └── cache/           # Cached feed content
├── config.json          # User configuration
└── exports/             # Default export location
```

### Backup and Restore

**Backup:**
```
/rss-export ~/.claude/skills/rss-manager/backup/feeds-$(date +%Y%m%d).opml
```

**Restore:**
```
/rss-import ~/.claude/skills/rss-manager/backup/feeds-YYYYMMDD.opml
```

## Supported Feed Types

- **RSS 0.90 / 0.91 / 0.92 / 1.0 / 2.0**
- **Atom 0.3 / 1.0**
- **JSON Feed 1.0 / 1.1**

## RSSHub Integration

RSSHub is an open-source RSS feed generator that creates RSS feeds for websites lacking native support.

**Popular Routes:**
- GitHub: `/github/repos/:user`, `/github/trending/:since`
- Twitter/X: `/twitter/user/:id`, `/twitter/list/:id/:name`
- YouTube: `/youtube/channel/:id`, `/youtube/playlist/:id`
- Reddit: `/reddit/r/:subreddit`
- Hacker News: `/hackernews/:section?`

Full route documentation: https://docs.rsshub.app

## Tips and Best Practices

1. **Organize with Categories**: Use OPML folders or tags to categorize feeds
2. **Regular Exports**: Export your feeds monthly as backup
3. **Feed Health**: Run `rss-list` periodically to identify broken feeds
4. **RSSHub Rate Limits**: Public instance has rate limits; self-host for heavy usage
5. **Feed URLs**: Save original source URLs in feed notes for reference

## Related Resources

- [RSSHub Documentation](https://docs.rsshub.app)
- [OPML Specification](http://opml.org/spec2.opml)
- [Feed Validator](https://validator.w3.org/feed/)
- [JSON Feed Spec](https://www.jsonfeed.org/)
