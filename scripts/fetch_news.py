#!/usr/bin/env python3
"""Fetch news from Google News RSS feeds and generate the dashboard HTML."""

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import escape

FEEDS = {
    "Top Headlines": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "Military & Defense": "https://news.google.com/rss/search?q=military+OR+defense+OR+army+OR+navy+OR+airforce+OR+pentagon&hl=en-US&gl=US&ceid=US:en",
    "Armed Conflicts": "https://news.google.com/rss/search?q=war+OR+troops+OR+armed+forces+OR+military+operations&hl=en-US&gl=US&ceid=US:en",
}

MAX_ITEMS_PER_FEED = 15


def fetch_feed(url):
    """Fetch and parse an RSS feed, returning a list of article dicts."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    articles = []
    for item in root.iter("item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        pub_date = item.findtext("pubDate", "")
        source = item.findtext("source", "")
        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "source": source,
            })
    return articles[:MAX_ITEMS_PER_FEED]


def build_html(feeds_data, updated_at):
    """Generate the dashboard HTML page."""
    sections = ""
    for feed_name, articles in feeds_data.items():
        rows = ""
        for i, a in enumerate(articles):
            source_badge = (
                f'<span class="source">{escape(a["source"])}</span>'
                if a["source"]
                else ""
            )
            rows += f"""
            <tr class="{'alt' if i % 2 else ''}">
                <td><a href="{escape(a['link'])}" target="_blank" rel="noopener">{escape(a['title'])}</a></td>
                <td>{source_badge}</td>
                <td class="date">{escape(a['pub_date'][:22] if a['pub_date'] else '')}</td>
            </tr>"""

        sections += f"""
        <section>
            <h2>{escape(feed_name)}</h2>
            <table>
                <thead>
                    <tr><th>Headline</th><th>Source</th><th>Published</th></tr>
                </thead>
                <tbody>{rows}
                </tbody>
            </table>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily News Dashboard</title>
    <style>
        :root {{
            --bg: #0f1117;
            --card: #1a1d27;
            --border: #2a2d3a;
            --text: #e1e4ed;
            --muted: #8b8fa3;
            --accent: #6c9cfc;
            --accent2: #f06868;
            --row-alt: #15171f;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        header {{
            background: linear-gradient(135deg, #1a1d27 0%, #252836 100%);
            border-bottom: 1px solid var(--border);
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
        }}
        header h1 span {{ color: var(--accent2); }}
        .updated {{
            color: var(--muted);
            font-size: 0.85rem;
        }}
        main {{ max-width: 1200px; margin: 2rem auto; padding: 0 1.5rem; }}
        section {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        h2 {{
            padding: 1rem 1.5rem;
            font-size: 1.1rem;
            border-bottom: 1px solid var(--border);
            color: var(--accent2);
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            text-align: left;
            padding: 0.6rem 1.5rem;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted);
            border-bottom: 1px solid var(--border);
        }}
        td {{
            padding: 0.7rem 1.5rem;
            font-size: 0.9rem;
            border-bottom: 1px solid var(--border);
        }}
        tr.alt {{ background: var(--row-alt); }}
        a {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .source {{
            background: #2a2d3a;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.78rem;
            color: var(--muted);
            white-space: nowrap;
        }}
        .date {{ white-space: nowrap; color: var(--muted); font-size: 0.82rem; }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--muted);
            font-size: 0.8rem;
        }}
        @media (max-width: 700px) {{
            th:nth-child(3), td:nth-child(3) {{ display: none; }}
            td, th {{ padding: 0.5rem 0.8rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Daily News <span>Dashboard</span></h1>
        <div class="updated">Last updated: {escape(updated_at)}</div>
    </header>
    <main>{sections}
    </main>
    <footer>
        Auto-updated daily at 7:00 AM UTC via GitHub Actions &middot; Powered by Google News RSS
    </footer>
</body>
</html>"""


def main():
    feeds_data = {}
    for name, url in FEEDS.items():
        try:
            feeds_data[name] = fetch_feed(url)
            print(f"Fetched {len(feeds_data[name])} articles for '{name}'")
        except Exception as e:
            print(f"Error fetching '{name}': {e}")
            feeds_data[name] = []

    updated_at = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = build_html(feeds_data, updated_at)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard generated at {updated_at}")


if __name__ == "__main__":
    main()
