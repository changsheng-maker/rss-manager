"""HTML report generator - Premium Dashboard Design."""

from datetime import datetime
from typing import List, Dict
import html


class HTMLReportGenerator:
    """Generate HTML reports from RSS feeds."""

    def __init__(self, title: str = "RSS Report"):
        self.title = title

    def generate_github_trending_html(
        self,
        title: str,
        subtitle: str,
        items: List[Dict],
        lang: str = "zh"
    ) -> str:
        """Generate premium HTML report."""
        css = self._get_css()
        cards_html = self._generate_cards(items, lang)
        is_zh = lang == "zh"

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark">
    <title>{html.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
    <style>{css}</style>
</head>
<body>
    <div class="page">
        <header class="header">
            <div class="header-top">
                <div class="brand">
                    <svg class="brand-icon" width="24" height="24" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                    </svg>
                    <span class="brand-text">{"热门仓库" if is_zh else "Trending"}</span>
                </div>
                <button class="lang-toggle" onclick="toggleLang()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="2" y1="12" x2="22" y2="12"/>
                        <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
                    </svg>
                    {"EN" if is_zh else "中文"}
                </button>
            </div>
            <h1 class="title">{html.escape(title)}</h1>
            <p class="subtitle">{html.escape(subtitle)}</p>
            <div class="meta">
                <span class="meta-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2"/>
                        <line x1="16" y1="2" x2="16" y2="6"/>
                        <line x1="8" y1="2" x2="8" y2="6"/>
                        <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    {datetime.now().strftime('%Y-%m-%d')}
                </span>
                <span class="meta-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
                    </svg>
                    {len(items)} {"个项目" if is_zh else "repos"}
                </span>
            </div>
        </header>
        <main class="list">
            {cards_html}
        </main>
        <footer class="footer">
            <span>{"生成于" if is_zh else "Generated at"} {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            <span class="dot">•</span>
            <span>RSS Manager</span>
        </footer>
    </div>
    <script>
    const translations = {{
        zh: {{
            badge: '热门仓库',
            repos: '{len(items)} 个项目',
            generated: '生成于',
            lang: 'EN',
            noDesc: '暂无描述',
        }},
        en: {{
            badge: 'Trending',
            repos: '{len(items)} repos',
            generated: 'Generated at',
            lang: '中文',
            noDesc: 'No description',
        }}
    }};

    function toggleLang() {{
        const html = document.documentElement;
        const next = html.lang === 'zh' ? 'en' : 'zh';
        const t = translations[next];
        html.lang = next;

        document.querySelector('.brand-text').textContent = t.badge;
        document.querySelector('.lang-toggle').innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>` + t.lang;
        document.querySelector('.footer').innerHTML = `<span>${{t.generated}} ${{new Date().toLocaleString()}}</span><span class="dot">•</span><span>RSS Manager</span>`;
    }}
    </script>
</body>
</html>"""

    def _get_css(self) -> str:
        """Premium light theme CSS."""
        return """
        :root {
            --bg: #ffffff;
            --surface: #fafafa;
            --surface-hover: #f4f4f5;
            --border: #e4e4e7;
            --border-hover: #d4d4d8;
            --text: #18181b;
            --text-2: #52525b;
            --text-3: #a1a1aa;
            --accent: #0ea5e9;
            --accent-dim: rgba(14, 165, 233, 0.1);
            --gold: #d97706;
            --gold-dim: rgba(217, 119, 6, 0.1);
            --silver: #737373;
            --silver-dim: rgba(115, 115, 115, 0.1);
            --bronze: #ea580c;
            --bronze-dim: rgba(234, 88, 12, 0.1);
            --green: #16a34a;
            --radius: 10px;
        }

        *, *::before, *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            color-scheme: light;
            font-size: 16px;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .page {
            max-width: 900px;
            margin: 0 auto;
            padding: 0 24px;
        }

        /* Header */
        .header {
            padding: 48px 0 40px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 24px;
        }

        .header-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-icon {
            color: var(--text);
        }

        .brand-text {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-2);
            letter-spacing: 0.02em;
        }

        .lang-toggle {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-2);
            font-size: 12px;
            font-weight: 500;
            font-family: 'JetBrains Mono', monospace;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .lang-toggle:hover {
            border-color: var(--accent);
            color: var(--accent);
        }

        .title {
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text);
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 15px;
            color: var(--text-3);
            margin-bottom: 20px;
        }

        .meta {
            display: flex;
            gap: 20px;
        }

        .meta-item {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--text-3);
        }

        /* List */
        .list {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        /* Card */
        .card {
            display: grid;
            grid-template-columns: 56px 1fr auto;
            gap: 16px;
            align-items: center;
            padding: 16px 20px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            transition: all 0.15s ease;
            cursor: pointer;
        }

        .card:hover {
            border-color: var(--border-hover);
            background: var(--surface-hover);
        }

        .card:hover .card-link {
            color: var(--accent);
        }

        /* Rank */
        .rank {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-3);
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
        }

        .card.rank-1 .rank {
            color: var(--gold);
            background: var(--gold-dim);
            border-color: rgba(217, 119, 6, 0.2);
        }

        .card.rank-2 .rank {
            color: var(--silver);
            background: var(--silver-dim);
            border-color: rgba(115, 115, 115, 0.2);
        }

        .card.rank-3 .rank {
            color: var(--bronze);
            background: var(--bronze-dim);
            border-color: rgba(234, 88, 12, 0.2);
        }

        /* Info */
        .info {
            min-width: 0;
        }

        .card-link {
            font-size: 15px;
            font-weight: 600;
            color: var(--text);
            text-decoration: none;
            display: block;
            margin-bottom: 4px;
            transition: color 0.15s;
        }

        .card-link .owner {
            color: var(--text-2);
            font-weight: 500;
        }

        .card-link .slash {
            color: var(--text-3);
            margin: 0 1px;
        }

        .desc {
            font-size: 13px;
            color: var(--text-3);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Stats */
        .stats {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
        }

        .stars {
            display: flex;
            align-items: center;
            gap: 5px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
        }

        .stars svg {
            width: 16px;
            height: 16px;
            color: var(--gold);
            fill: currentColor;
        }

        .growth {
            font-size: 12px;
            font-weight: 500;
            color: var(--green);
            font-family: 'JetBrains Mono', monospace;
        }

        /* Footer */
        .footer {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            padding: 40px 0;
            font-size: 12px;
            color: var(--text-3);
        }

        .dot {
            opacity: 0.5;
        }

        /* Responsive */
        @media (max-width: 640px) {
            .card {
                grid-template-columns: 44px 1fr;
                grid-template-rows: auto auto;
                gap: 12px;
            }

            .rank {
                width: 36px;
                height: 36px;
                font-size: 12px;
            }

            .stats {
                grid-column: 1 / -1;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            }
        }
        """

    def _generate_cards(self, items: List[Dict], lang: str) -> str:
        """Generate HTML cards."""
        cards = []
        for item in items:
            rank = item.get('rank', 0)
            rank_class = f"rank-{rank}" if rank <= 3 else ""
            owner = html.escape(item.get('owner', ''))
            repo = html.escape(item.get('repo', ''))
            url = html.escape(item.get('url', '#'))
            desc = html.escape(item.get('description', '') or ('暂无描述' if lang == 'zh' else 'No description'))
            stars = item.get('stars_formatted', str(item.get('stars', 'N/A')))
            growth = item.get('stars_growth', '')

            growth_html = f'<span class="growth">+{growth}/day</span>' if growth else ''

            card = f"""
            <article class="card {rank_class}">
                <div class="rank">{rank}</div>
                <div class="info">
                    <a href="{url}" target="_blank" class="card-link">
                        <span class="owner">{owner}</span><span class="slash">/</span>{repo}
                    </a>
                    <p class="desc">{desc}</p>
                </div>
                <div class="stats">
                    <span class="stars">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                        </svg>
                        {stars}
                    </span>
                    {growth_html}
                </div>
            </article>"""
            cards.append(card)
        return '\n'.join(cards)

    def generate(self, items: List[Dict], theme: str = "default") -> str:
        return """<!DOCTYPE html><html><head></head><body></body></html>"""

    def save(self, content: str, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)