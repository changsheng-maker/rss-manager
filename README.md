# RSS Manager

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/anthropics/claude-code)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Discover, manage, and organize RSS feeds with Claude Code. Auto-detect feeds, RSSHub integration, OPML import/export, and AI-powered content reports.

## ✨ Features

- 🔍 **Auto Discovery** - Automatically find RSS/Atom/JSON feeds on any website
- 📚 **RSSHub Integration** - Access 800+ platforms via RSSHub routes
- 📥📤 **OPML Support** - Import/export with Feedly, Inoreader, etc.
- 🤖 **AI Reports** - Generate AI-powered reading summaries
- 📁 **Category Management** - Organize feeds with tags and categories
- 🔗 **Native RSS** - Direct feeds from GitHub, YouTube, Reddit, Medium

## 🚀 Quick Start

### Installation

```bash
# Clone to your Claude Code skills directory
cd ~/.claude/skills
git clone https://github.com/YOUR_USERNAME/rss-manager.git

# Install dependencies
pip install -r rss-manager/requirements.txt
```

### Basic Usage

```bash
# 1. Discover RSS feeds on a website
python3 rss-discover.py https://karpathy.ai

# 2. Add feeds to your collection
python3 rss-add.py "https://karpathy.bearblog.dev/feed/" --category blogs

# 3. List all feeds
python3 rss-list.py

# 4. Browse RSSHub routes
python3 rss-rsshub.py --platform social

# 5. Import from OPML
python3 rss-import.py ~/Downloads/feedly.opml

# 6. Export to OPML
python3 rss-export.py ~/Desktop/my-feeds.opml
```

## 📖 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `rss-discover` | Discover RSS feeds from URL | `python3 rss-discover.py github.blog` |
| `rss-add` | Add feed to collection | `python3 rss-add.py URL --category tech` |
| `rss-list` | List all subscribed feeds | `python3 rss-list.py` |
| `rss-remove` | Remove a feed | `python3 rss-remove.py FEED_ID` |
| `rss-import` | Import OPML file | `python3 rss-import.py file.opml` |
| `rss-export` | Export to OPML | `python3 rss-export.py file.opml` |
| `rss-rsshub` | Browse RSSHub routes | `python3 rss-rsshub.py --platform blogs` |

## 📂 Included Data

- **50+ AI Leader RSS Feeds** - Andrej Karpathy, OpenAI, DeepMind, etc.
- **RSSHub Routes Database** - 800+ platforms with examples
- **Common Feed Patterns** - WordPress, Ghost, Medium, etc.

## 🏗️ Project Structure

```
rss-manager/
├── cli.py                 # Main CLI dispatcher
├── rss-discover.py        # Feed discovery
├── rss-add.py            # Add feeds
├── rss-list.py           # List feeds
├── rss-remove.py         # Remove feeds
├── rss-import.py         # OPML import
├── rss-export.py         # OPML export
├── rss-rsshub.py         # RSSHub browser
├── lib/
│   ├── feed_discovery.py # Auto-discovery engine
│   ├── feed_parser.py    # RSS/Atom/JSON parser
│   ├── storage.py        # Feed storage
│   ├── opml.py          # OPML handling
│   └── rsshub_client.py  # RSSHub integration
├── data/
│   ├── ai-leaders.opml   # 50+ AI RSS feeds
│   ├── rsshub-routes.json # RSSHub routes
│   ├── common-feeds.json  # Feed patterns
│   └── categories.json    # Default categories
└── SKILL.md              # Full documentation
```

## 🔗 Supported RSS Sources

### Native RSS (Most Reliable)
- **Blogs**: WordPress, Ghost, Medium, Bear Blog, Substack
- **Code**: GitHub releases/commits, GitLab
- **Video**: YouTube channels, Bilibili
- **Social**: Reddit, Hacker News, Mastodon
- **News**: arXiv, Distill.pub, Papers with Code

### Via RSSHub
- Twitter/X, Instagram, TikTok, Telegram
- Weibo, 知乎, 小红书, 公众号
- LinkedIn, Facebook (limited)

## 📊 AI Leaders Collection

Pre-configured OPML with 50+ top AI sources:

- 🏆 **AI Godfathers**: Yann LeCun, Geoffrey Hinton, Yoshua Bengio
- 🌟 **Top Researchers**: Andrej Karpathy, Andrew Ng, Jeremy Howard
- 🏢 **Companies**: OpenAI, Anthropic, DeepMind, Hugging Face
- 📰 **Newsletters**: The Batch, Import AI, TLDR AI
- 📚 **Academic**: arXiv AI/ML, Distill.pub
- 🎬 **YouTube**: Two Minute Papers, Lex Fridman

Import with:
```bash
python3 rss-import.py data/ai-leaders.opml
```

## 🛠️ Development

### Running Tests

```bash
# Test discovery
python3 rss-discover.py https://example.com

# Test adding feed
python3 rss-add.py "https://news.ycombinator.com/rss" --category tech

# Generate report
python3 -c "
import feedparser
# See ai-rss-report.md for example
"
```

### Adding New RSSHub Routes

Edit `data/rsshub-routes.json`:
```json
{
  "category": "social",
  "routes": [
    {
      "name": "twitter-user",
      "path": "/twitter/user/:id",
      "example": "https://rsshub.app/twitter/user/karpathy",
      "description": "Twitter user timeline"
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- [RSSHub](https://github.com/DIYgod/RSSHub) - Open source RSS feed generator
- [feedparser](https://github.com/kurtmckee/feedparser) - RSS/Atom parser
- [Claude Code](https://github.com/anthropics/claude-code) - AI coding assistant

---

**Happy RSS Reading! 📖**

> "RSS is not dead, it's just sleeping." - Internet proverb
