"""HTML report generator - Premium Knowledge Card Design."""

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
        """Generate premium dark theme HTML report for GitHub trending."""
        css = self._get_css()
        cards_html = self._generate_cards(items)

        # i18n
        is_zh = lang == "zh"
        lang_label = "语言" if is_zh else "Language"
        stars_label = "星" if is_zh else "stars"
        per_day = "/天" if is_zh else "/day"
        generated = "生成于" if is_zh else "Generated at"
        repos_label = "个仓库" if is_zh else "repos"

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark">
    <title>{html.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>{css}</style>
</head>
<body>
    <div class="bg">
        <div class="bg-grid"></div>
    </div>
    <div class="container">
        <header class="header">
            <div class="badge">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                </svg>
                {"热门仓库" if is_zh else "Trending"}
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
                    {len(items)} {repos_label}
                </span>
                <button class="lang-toggle" onclick="toggleLang()">{("EN" if is_zh else "中文")}</button>
            </div>
        </header>
        <main class="cards-grid">
            {cards_html}
        </main>
        <footer class="footer">
            <p>{generated} {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </footer>
    </div>
    <script>
    function toggleLang() {{
        const html = document.documentElement;
        const current = html.lang;
        const isZh = current === 'zh';
        html.lang = isZh ? 'en' : 'zh';
        document.querySelector('.lang-toggle').textContent = isZh ? '中文' : 'EN';

        // Update static text
        const badge = document.querySelector('.badge');
        badge.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>` + (isZh ? 'Trending' : '热门仓库');

        document.querySelector('.lang-toggle').textContent = isZh ? '中文' : 'EN';

        // Update footer
        document.querySelector('.footer p').textContent = (isZh ? 'Generated at' : '生成于') + ' ' + new Date().toLocaleString();
    }}
    </script>
</body>
</html>"""

    def _get_css(self) -> str:
        """Premium dark theme CSS."""
        return """
        :root {
            --bg: #09090b;
            --bg-alt: #18181b;
            --surface: #27272a;
            --border: #3f3f46;
            --text: #fafafa;
            --text-2: #a1a1aa;
            --text-3: #71717a;
            --accent: #3b82f6;
            --gold: #fbbf24;
            --silver: #d4d4d8;
            --bronze: #f97316;
            --green: #22c55e;
            --radius: 12px;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        html { color-scheme: dark; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        /* Background */
        .bg {
            position: fixed;
            inset: 0;
            z-index: 0;
            overflow: hidden;
        }

        .bg-grid {
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
            background-size: 60px 60px;
            mask-image: radial-gradient(ellipse 80% 80% at 50% 0%, black 40%, transparent 100%);
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 24px;
            position: relative;
            z-index: 1;
        }

        /* Header */
        .header {
            padding: 72px 0 48px;
            text-align: center;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--bg-alt);
            border: 1px solid var(--border);
            border-radius: 100px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-2);
            margin-bottom: 20px;
            letter-spacing: 0.02em;
        }

        .badge svg { color: var(--text); }

        .title {
            font-size: clamp(2rem, 5vw, 2.75rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.1;
            margin-bottom: 12px;
            background: linear-gradient(180deg, #fff 0%, #a1a1aa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 1.125rem;
            color: var(--text-2);
            margin-bottom: 24px;
            font-weight: 400;
        }

        .meta {
            display: flex;
            justify-content: center;
            gap: 16px;
            flex-wrap: wrap;
        }

        .meta-item {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--text-3);
        }

        /* Cards Grid */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            padding-bottom: 80px;
        }

        @media (max-width: 720px) {
            .cards-grid { grid-template-columns: 1fr; }
        }

        /* Card */
        .card {
            background: var(--bg-alt);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px;
            position: relative;
            overflow: hidden;
            transition: all 0.2s ease;
        }

        .card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: var(--border);
            transition: background 0.2s ease;
        }

        .card:hover {
            border-color: var(--text-3);
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.5);
        }

        .card:hover::before {
            background: var(--accent);
        }

        /* Rank colors */
        .card.rank-1::before { background: var(--gold); }
        .card.rank-2::before { background: var(--silver); }
        .card.rank-3::before { background: var(--bronze); }

        .card.rank-1:hover::before { background: var(--gold); }
        .card.rank-2:hover::before { background: var(--silver); }
        .card.rank-3:hover::before { background: var(--bronze); }

        /* Card Header */
        .card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
        }

        .rank {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-3);
            padding: 4px 8px;
            background: var(--surface);
            border-radius: 4px;
        }

        .card.rank-1 .rank { color: var(--gold); }
        .card.rank-2 .rank { color: var(--silver); }
        .card.rank-3 .rank { color: var(--bronze); }

        .stars {
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 13px;
            font-weight: 600;
            color: var(--gold);
        }

        .stars svg {
            width: 14px;
            height: 14px;
        }

        .growth {
            font-size: 11px;
            font-weight: 600;
            color: var(--green);
            font-family: 'IBM Plex Mono', monospace;
        }

        /* Repo Name */
        .repo-name {
            font-size: 1.0625rem;
            font-weight: 600;
            margin-bottom: 8px;
            line-height: 1.3;
        }

        .repo-name a {
            color: var(--text);
            text-decoration: none;
            transition: color 0.15s;
        }

        .repo-name a:hover { color: var(--accent); }

        .repo-name .owner { color: var(--text-2); font-weight: 500; }
        .repo-name .slash { color: var(--text-3); margin: 0 1px; }

        /* Description */
        .desc {
            font-size: 13px;
            color: var(--text-2);
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 16px;
            min-height: 42px;
        }

        /* Card Footer */
        .card-foot {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding-top: 14px;
            border-top: 1px solid var(--border);
        }

        .lang {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: var(--text-2);
        }

        .lang-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        .tags {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .tag {
            font-size: 11px;
            font-weight: 500;
            padding: 3px 8px;
            background: var(--surface);
            color: var(--text-2);
            border-radius: 4px;
            border: 1px solid var(--border);
            transition: all 0.15s;
        }

        .tag:hover {
            border-color: var(--accent);
            color: var(--accent);
        }

        .lang-toggle {
            background: var(--bg-alt);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-2);
            font-size: 12px;
            font-weight: 600;
            padding: 6px 12px;
            cursor: pointer;
            transition: all 0.15s;
            font-family: 'IBM Plex Mono', monospace;
        }

        .lang-toggle:hover {
            border-color: var(--accent);
            color: var(--accent);
        }

        .footer {
            text-align: center;
            padding: 32px;
            color: var(--text-3);
            font-size: 13px;
            border-top: 1px solid var(--border);
            margin-top: 48px;
        }
        """

    def _generate_cards(self, items: List[Dict]) -> str:
        """Generate HTML cards."""
        cards = []
        for i, item in enumerate(items, 1):
            rank_class = f"rank-{i}" if i <= 3 else ""
            owner = html.escape(item.get('owner', ''))
            repo = html.escape(item.get('repo', ''))
            url = html.escape(item.get('url', '#'))
            desc = html.escape(item.get('description', 'No description'))
            stars = item.get('stars_formatted', str(item.get('stars', 'N/A')))
            growth = item.get('stars_growth', '')
            lang = html.escape(item.get('language', ''))
            lang_color = item.get('language_color', '#8b949e')
            topics = item.get('topics', [])[:3]

            growth_html = f'<span class="growth">+{growth}/day</span>' if growth else ''
            tags_html = ''.join([f'<span class="tag">{html.escape(t)}</span>' for t in topics])

            card = f"""
            <article class="card {rank_class}">
                <div class="card-top">
                    <span class="rank">#{i}</span>
                    <div class="stars">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                        </svg>
                        {stars}
                        {growth_html}
                    </div>
                </div>
                <h3 class="repo-name">
                    <a href="{url}" target="_blank" rel="noopener">
                        <span class="owner">{owner}</span><span class="slash">/</span>{repo}
                    </a>
                </h3>
                <p class="desc">{desc}</p>
                <div class="card-foot">
                    <div class="lang">
                        <span class="lang-dot" style="background:{lang_color}"></span>
                        {lang}
                    </div>
                    <div class="tags">{tags_html}</div>
                </div>
            </article>"""
            cards.append(card)
        return '\n'.join(cards)

    def generate(self, items: List[Dict], theme: str = "default") -> str:
        """Generate RSS HTML report."""
        css = self._get_rss_css()
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(self.title)}</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{html.escape(self.title)}</h1>
            <p class="date">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </header>
        <main>{self._generate_items_html(items)}</main>
    </div>
</body>
</html>"""

    def _get_rss_css(self) -> str:
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #09090b; color: #fafafa; padding: 40px 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 40px; }
        h1 { font-size: 2rem; margin-bottom: 8px; }
        .date { color: #71717a; font-size: 14px; }
        .item { background: #18181b; border: 1px solid #3f3f46; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
        .item h2 { font-size: 1rem; margin-bottom: 8px; }
        .item h2 a { color: #3b82f6; text-decoration: none; }
        .item h2 a:hover { text-decoration: underline; }
        .item p { color: #a1a1aa; font-size: 14px; line-height: 1.5; }
        .meta { font-size: 12px; color: #71717a; margin-top: 8px; }
        """

    def _generate_items_html(self, items: List[Dict]) -> str:
        return ''.join([
            f'<div class="item"><h2><a href="{html.escape(i.get("url",""))}">{html.escape(i.get("title",""))}</a></h2><p>{html.escape(i.get("summary",""))}</p><div class="meta">{html.escape(i.get("source",""))}</div></div>'
            for i in items
        ])

    def save(self, content: str, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)