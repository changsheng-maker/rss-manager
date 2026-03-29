# RSS Manager - RSS 订阅管理器

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/anthropics/claude-code)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | **中文**

> 为 Claude Code 打造的 RSS 订阅管理技能。自动发现 RSS 源、RSSHub 集成、OPML 导入导出，以及 AI 驱动的内容报告。

## ✨ 功能特性

- 🔍 **自动发现** - 自动识别任何网站的 RSS/Atom/JSON 订阅源
- 📚 **RSSHub 集成** - 通过 RSSHub 路由访问 800+ 平台
- 📥📤 **OPML 支持** - 与 Feedly、Inoreader 等工具互导订阅
- 🤖 **AI 报告** - 生成 AI 驱动的阅读摘要和趋势分析
- 📁 **分类管理** - 用标签和分类整理订阅源
- 🔗 **原生 RSS** - 直接支持 GitHub、YouTube、Reddit、Medium 等平台

## 🚀 快速开始

### 安装

```bash
# 克隆到 Claude Code 技能目录
cd ~/.claude/skills
git clone https://github.com/changsheng-maker/rss-manager.git

# 安装依赖
pip install -r rss-manager/requirements.txt
```

### 基础用法

```bash
# 1. 发现网站的 RSS 源
python3 rss-discover.py https://karpathy.ai

# 2. 添加到订阅库
python3 rss-add.py "https://karpathy.bearblog.dev/feed/" --category blogs

# 3. 查看所有订阅
python3 rss-list.py

# 4. 浏览 RSSHub 路由
python3 rss-rsshub.py --platform social

# 5. 从 OPML 导入
python3 rss-import.py ~/Downloads/feedly.opml

# 6. 导出为 OPML
python3 rss-export.py ~/Desktop/my-feeds.opml
```

## 📖 可用命令

| 命令 | 描述 | 示例 |
|---------|-------------|---------|
| `rss-discover` | 从 URL 发现 RSS 源 | `python3 rss-discover.py github.blog` |
| `rss-add` | 添加订阅到库 | `python3 rss-add.py URL --category tech` |
| `rss-list` | 列出所有订阅 | `python3 rss-list.py` |
| `rss-remove` | 删除订阅 | `python3 rss-remove.py FEED_ID` |
| `rss-import` | 导入 OPML 文件 | `python3 rss-import.py file.opml` |
| `rss-export` | 导出为 OPML | `python3 rss-export.py file.opml` |
| `rss-rsshub` | 浏览 RSSHub 路由 | `python3 rss-rsshub.py --platform blogs` |

## 📂 包含数据

- **50+ AI 大佬 RSS 源** - Andrej Karpathy、OpenAI、DeepMind 等
- **RSSHub 路由数据库** - 800+ 平台示例
- **常见订阅模式** - WordPress、Ghost、Medium 等

## 🏗️ 项目结构

```
rss-manager/
├── cli.py                 # 主 CLI 调度器
├── rss-discover.py        # 订阅源发现
├── rss-add.py            # 添加订阅
├── rss-list.py           # 列出订阅
├── rss-remove.py         # 删除订阅
├── rss-import.py         # OPML 导入
├── rss-export.py         # OPML 导出
├── rss-rsshub.py         # RSSHub 浏览器
├── lib/
│   ├── feed_discovery.py # 自动发现引擎
│   ├── feed_parser.py    # RSS/Atom/JSON 解析器
│   ├── storage.py        # 订阅存储
│   ├── opml.py          # OPML 处理
│   └── rsshub_client.py  # RSSHub 集成
├── data/
│   ├── ai-leaders.opml   # 50+ AI RSS 源
│   ├── rsshub-routes.json # RSSHub 路由
│   ├── common-feeds.json  # 订阅模式
│   └── categories.json    # 默认分类
└── SKILL.md              # 完整文档
```

## 🔗 支持的 RSS 源

### 原生 RSS（最稳定）
- **博客**: WordPress、Ghost、Medium、Bear Blog、Substack
- **代码**: GitHub releases/commits、GitLab
- **视频**: YouTube 频道、Bilibili
- **社交**: Reddit、Hacker News、Mastodon
- **新闻**: arXiv、Distill.pub、Papers with Code

### 通过 RSSHub
- Twitter/X、Instagram、TikTok、Telegram
- 微博、知乎、小红书、公众号
- LinkedIn、Facebook（有限）

## 📊 AI 大佬合集

预配置的 OPML，包含 50+ 顶级 AI 源：

- 🏆 **AI 教父**: Yann LeCun、Geoffrey Hinton、Yoshua Bengio
- 🌟 **顶级研究者**: Andrej Karpathy、Andrew Ng、Jeremy Howard
- 🏢 **公司**: OpenAI、Anthropic、DeepMind、Hugging Face
- 📰 **Newsletter**: The Batch、Import AI、TLDR AI
- 📚 **学术**: arXiv AI/ML、Distill.pub
- 🎬 **YouTube**: Two Minute Papers、Lex Fridman

导入方式：
```bash
python3 rss-import.py data/ai-leaders.opml
```

## 🛠️ 开发

### 运行测试

```bash
# 测试发现功能
python3 rss-discover.py https://example.com

# 测试添加订阅
python3 rss-add.py "https://news.ycombinator.com/rss" --category tech

# 生成报告
python3 -c "
import feedparser
# 见 ai-rss-report.md 示例
"
```

### 添加新的 RSSHub 路由

编辑 `data/rsshub-routes.json`：
```json
{
  "category": "social",
  "routes": [
    {
      "name": "twitter-user",
      "path": "/twitter/user/:id",
      "example": "https://rsshub.app/twitter/user/karpathy",
      "description": "Twitter 用户时间线"
    }
  ]
}
```

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/ amazing-feature`
3. 提交更改：`git commit -m '添加 amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

## 📄 许可证

MIT 许可证 - 见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [RSSHub](https://github.com/DIYgod/RSSHub) - 开源 RSS 生成器
- [feedparser](https://github.com/kurtmckee/feedparser) - RSS/Atom 解析器
- [Claude Code](https://github.com/anthropics/claude-code) - AI 编程助手

---

**阅读愉快！📖**

> "RSS 没有死，它只是睡着了。" - 互联网谚语
