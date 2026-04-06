# Daily News Dashboard

A self-updating news dashboard that aggregates headlines from Google News, focused on:

- **Top Headlines** — Major world news
- **Military & Defense** — Pentagon, armed forces, defense policy
- **Armed Conflicts** — Wars, troop deployments, military operations

## How it works

1. A GitHub Actions workflow runs **daily at 7:00 AM UTC**
2. `scripts/fetch_news.py` pulls articles from Google News RSS feeds
3. The script generates a static `index.html` dashboard
4. The workflow commits and pushes the updated page

## Manual update

Trigger the workflow manually from **Actions > Update Daily News Dashboard > Run workflow**.

## Local preview

```bash
python scripts/fetch_news.py
open index.html
```
