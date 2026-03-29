"""HTML report generator - Premium Design v2."""

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
        lang_label = "语言" if is_zh else "Language"
        repos_label = "个仓库" if is_zh else "repos"
        generated = "生成于" if is_zh else "Generated at"

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark">
    <title>{html.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Geist:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>{css}</style>
</head>
<body>
    <div class="bg-pattern"></div>
    <div class="bg-glow"></div>
    <div class="container">
        <header class="header">
            <div class="header-content">
                <div class="badge-row">
                    <span class="badge">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                        </svg>
                        {"热门仓库" if is_zh else "Trending"}
                    </span>
                    <button class="lang-btn" onclick="toggleLang()">
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
                <div class="meta-row">
                    <span class="meta-chip">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2"/>
                            <line x1="16" y1="2" x2="16" y2="6"/>
                            <line x1="8" y1="2" x2="8" y2="6"/>
                            <line x1="3" y1="10" x2="21" y2="10"/>
                        </svg>
                        {datetime.now().strftime('%Y-%m-%d')}
                    </span>
                    <span class="meta-chip">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
                        </svg>
                        {len(items)} {repos_label}
                    </span>
                </div>
            </div>
        </header>
        <main class="cards">
            {cards_html}
        </main>
        <footer class="footer">
            <span>{generated} {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            <span class="divider">•</span>
            <span>RSS Manager</span>
        </footer>
    </div>
    <script>
    const translations = {{
        zh: {{
            badge: '热门仓库',
            title: '{html.escape(title)}',
            subtitle: '{html.escape(subtitle)}',
            repos: '{len(items)} 个仓库',
            generated: '生成于',
            lang: 'EN',
            today: '今日',
            week: '本周',
            month: '本月',
        }},
        en: {{
            badge: 'Trending',
            title: '{html.escape(title)}',
            subtitle: '{html.escape(subtitle)}',
            repos: '{len(items)} repos',
            generated: 'Generated at',
            lang: '中文',
            today: 'Today',
            week: 'Week',
            month: 'Month',
        }}
    }};

    function toggleLang() {{
        const html = document.documentElement;
        const current = html.lang;
        const next = current === 'zh' ? 'en' : 'zh';
        const t = translations[next];

        html.lang = next;
        document.querySelector('.badge').innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>` + t.badge;
        document.querySelector('.lang-btn').innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>` + t.lang;
        document.querySelector('.subtitle').textContent = t.subtitle;
        const chips = document.querySelectorAll('.meta-chip');
        chips[1].innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>` + t.repos;
        document.querySelector('.footer').innerHTML = `<span>${{t.generated}} ${{new Date().toLocaleString()}}</span><span class="divider">•</span><span>RSS Manager</span>`;
    }}
    </script>
</body>
</html>"""

    def _get_css(self) -> str:
        """Premium dark theme CSS."""
        return """
        :root {
            --bg: #030712;
            --bg-2: #0a0f1a;
            --surface: #111827;
            --surface-2: #1f2937;
            --border: #1f2937;
            --border-2: #374151;
            --text: #f9fafb;
            --text-2: #d1d5db;
            --text-3: #9ca3af;
            --accent: #3b82f6;
            --gold: #f59e0b;
            --silver: #9ca3af;
            --bronze: #ea580c;
            --green: #22c55e;
            --radius: 16px;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        html { color-scheme: dark; }

        body {
            font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        /* Background */
        .bg-pattern {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.015'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }

        .bg-glow {
            position: fixed;
            top: -200px;
            left: 50%;
            transform: translateX(-50%);
            width: 800px;
            height: 400px;
            background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.12) 0%, transparent 70%);
            z-index: 0;
            pointer-events: none;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 24px;
            position: relative;
            z-index: 1;
        }

        /* Header */
        .header {
            padding: 64px 0 48px;
            text-align: center;
        }

        .header-content {
            max-width: 560px;
            margin: 0 auto;
        }

        .badge-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 24px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 100px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-2);
        }

        .badge svg { color: var(--text); }

        .lang-btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: transparent;
            border: 1px solid var(--border-2);
            border-radius: 100px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-3);
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'Geist Mono', monospace;
        }

        .lang-btn:hover {
            border-color: var(--accent);
            color: var(--accent);
        }

        .title {
            font-size: clamp(1.75rem, 4vw, 2.5rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.1;
            margin-bottom: 12px;
            background: linear-gradient(180deg, #fff 0%, #d1d5db 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 1rem;
            color: var(--text-3);
            margin-bottom: 28px;
            font-weight: 400;
        }

        .meta-row {
            display: flex;
            justify-content: center;
            gap: 12px;
        }

        .meta-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 12px;
            color: var(--text-3);
        }

        /* Cards */
        .cards {
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding-bottom: 64px;
        }

        .card {
            background: var(--bg-2);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px 24px;
            display: grid;
            grid-template-columns: 48px 1fr auto;
            gap: 16px;
            align-items: center;
            transition: all 0.2s ease;
            position: relative;
        }

        .card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 12px;
            bottom: 12px;
            width: 3px;
            border-radius: 0 4px 4px 0;
            background: var(--border);
            transition: background 0.2s;
        }

        .card:hover {
            border-color: var(--border-2);
            background: var(--surface);
            transform: translateX(4px);
        }

        .card:hover::before {
            background: var(--accent);
        }

        .card.rank-1::before { background: var(--gold); }
        .card.rank-2::before { background: var(--silver); }
        .card.rank-3::before { background: var(--bronze); }

        /* Rank */
        .rank {
            font-family: 'Geist Mono', monospace;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-3);
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
        }

        .card.rank-1 .rank { color: var(--gold); background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.3); }
        .card.rank-2 .rank { color: var(--silver); background: rgba(156, 163, 175, 0.1); border-color: rgba(156, 163, 175, 0.3); }
        .card.rank-3 .rank { color: var(--bronze); background: rgba(234, 88, 12, 0.1); border-color: rgba(234, 88, 12, 0.3); }

        /* Info */
        .info {
            min-width: 0;
        }

        .repo-link {
            font-size: 15px;
            font-weight: 600;
            color: var(--text);
            text-decoration: none;
            display: block;
            margin-bottom: 4px;
            transition: color 0.15s;
        }

        .repo-link:hover { color: var(--accent); }

        .repo-link .owner { color: var(--text-2); font-weight: 500; }
        .repo-link .slash { color: var(--text-3); margin: 0 2px; }

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
            gap: 8px;
        }

        .stars {
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: 'Geist Mono', monospace;
            font-size: 14px;
            font-weight: 600;
            color: var(--gold);
        }

        .stars svg { width: 16px; height: 16px; }

        .growth {
            font-size: 11px;
            font-weight: 500;
            color: var(--green);
            background: rgba(34, 197, 94, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
        }

        .tags {
            display: flex;
            gap: 6px;
        }

        .tag {
            font-size: 11px;
            font-weight: 500;
            padding: 2px 8px;
            background: var(--surface-2);
            color: var(--text-3);
            border-radius: 4px;
        }

        /* Footer */
        .footer {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            padding: 32px;
            color: var(--text-3);
            font-size: 12px;
            border-top: 1px solid var(--border);
        }

        .divider { opacity: 0.5; }

        /* Responsive */
        @media (max-width: 720px) {
            .card {
                grid-template-columns: 40px 1fr;
                grid-template-rows: auto auto;
                gap: 12px;
            }

            .rank { width: 40px; height: 40px; font-size: 13px; }

            .stats {
                grid-column: 1 / -1;
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
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
            desc = html.escape(item.get('description', '') or ('No description' if lang == 'en' else '暂无描述'))
            stars = item.get('stars_formatted', str(item.get('stars', 'N/A')))
            growth = item.get('stars_growth', '')
            lang_name = html.escape(item.get('language', ''))
            lang_color = item.get('language_color', '#8b949e')
            topics = item.get('topics', [])[:2]

            growth_html = f'<span class="growth">+{growth}/day</span>' if growth else ''
            tags_html = ''.join([f'<span class="tag">{html.escape(t)}</span>' for t in topics])

            # Language indicator
            lang_html = f'<span class="lang-dot" style="background:{lang_color}"></span> {lang_name}' if lang_name else ''

            card = f"""
            <article class="card {rank_class}">
                <div class="rank">#{rank}</div>
                <div class="info">
                    <a href="{url}" target="_blank" class="repo-link">
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
                    <div class="tags">{tags_html}</div>
                </div>
            </article>"""
            cards.append(card)
        return '\n'.join(cards)

    def generate(self, items: List[Dict], theme: str = "default") -> str:
        """Generate RSS HTML report."""
        return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>RSS</title></head><body></body></html>"""

    def save(self, content: str, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)