#!/usr/bin/env python3
"""
NYT Mamdani Report Generator
Genererar en HTML-rapport från insamlad data.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / "data"
SNAPSHOTS_FILE = DATA_DIR / "snapshots.json"
REPORT_FILE = DATA_DIR / "report.html"


def load_snapshots() -> list:
    """Ladda snapshots från JSON-fil."""
    if SNAPSHOTS_FILE.exists():
        return json.loads(SNAPSHOTS_FILE.read_text(encoding="utf-8"))
    return []


def generate_report():
    """Generera HTML-rapport."""
    snapshots = load_snapshots()
    
    if not snapshots:
        print("Ingen data att rapportera.")
        return
    
    # Beräkna statistik
    total_checks = len(snapshots)
    checks_with_mentions = sum(1 for s in snapshots if s["mentions_count"] > 0)
    total_mentions = sum(s["mentions_count"] for s in snapshots)
    
    # Gruppera per dag
    by_date = defaultdict(list)
    for s in snapshots:
        date = s["timestamp"][:10]
        by_date[date].append(s)
    
    # Unika artiklar (baserat på URL)
    unique_articles = {}
    for s in snapshots:
        for m in s.get("mentions", []):
            if m.get("href") and m["href"] not in unique_articles:
                unique_articles[m["href"]] = {
                    "headline": m.get("headline") or m.get("text", "")[:100],
                    "first_seen": s["timestamp"],
                    "section": m.get("section", "unknown")
                }
    
    # Generera HTML
    html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYT Mamdani Tracker - Rapport</title>
    <style>
        :root {{
            --bg: #fafafa;
            --text: #1a1a1a;
            --muted: #666;
            --border: #e0e0e0;
            --accent: #1a73e8;
            --highlight: #fff3cd;
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--bg);
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--muted);
            margin-bottom: 2rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent);
        }}
        
        .stat-label {{
            font-size: 0.875rem;
            color: var(--muted);
        }}
        
        h2 {{
            font-size: 1.25rem;
            margin-top: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }}
        
        .article {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        
        .article-headline {{
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .article-headline a {{
            color: var(--text);
            text-decoration: none;
        }}
        
        .article-headline a:hover {{
            color: var(--accent);
        }}
        
        .article-meta {{
            font-size: 0.875rem;
            color: var(--muted);
        }}
        
        .day-section {{
            margin-bottom: 2rem;
        }}
        
        .day-header {{
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--muted);
        }}
        
        .snapshot {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .snapshot.has-mentions {{
            border-left: 4px solid var(--accent);
        }}
        
        .snapshot-time {{
            font-size: 0.875rem;
            color: var(--muted);
        }}
        
        .screenshot-link {{
            font-size: 0.875rem;
            margin-left: 1rem;
        }}
        
        .mention {{
            background: var(--highlight);
            padding: 0.5rem;
            border-radius: 4px;
            margin-top: 0.5rem;
            font-size: 0.875rem;
        }}
        
        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            font-size: 0.875rem;
            color: var(--muted);
        }}
    </style>
</head>
<body>
    <h1>NYT Mamdani Tracker</h1>
    <p class="subtitle">Övervakning av omnämnanden av Mamdani på nytimes.com</p>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{total_checks}</div>
            <div class="stat-label">Kontroller</div>
        </div>
        <div class="stat">
            <div class="stat-value">{checks_with_mentions}</div>
            <div class="stat-label">Med omnämnanden</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(unique_articles)}</div>
            <div class="stat-label">Unika artiklar</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(by_date)}</div>
            <div class="stat-label">Dagar</div>
        </div>
    </div>
    
    <h2>Unika artiklar</h2>
"""
    
    if unique_articles:
        for url, info in sorted(unique_articles.items(), key=lambda x: x[1]["first_seen"], reverse=True):
            html += f"""
    <div class="article">
        <div class="article-headline"><a href="{url}" target="_blank">{info['headline']}</a></div>
        <div class="article-meta">
            Först sedd: {info['first_seen'][:16].replace('T', ' ')} · 
            Sektion: {info['section']}
        </div>
    </div>
"""
    else:
        html += "<p>Inga artiklar hittade ännu.</p>"
    
    html += """
    <h2>Alla kontroller</h2>
"""
    
    # Visa per dag, senaste först
    for date in sorted(by_date.keys(), reverse=True):
        day_snapshots = by_date[date]
        day_mentions = sum(s["mentions_count"] for s in day_snapshots)
        
        html += f"""
    <div class="day-section">
        <div class="day-header">{date} ({len(day_snapshots)} kontroller, {day_mentions} omnämnanden)</div>
"""
        
        for s in sorted(day_snapshots, key=lambda x: x["timestamp"], reverse=True):
            time_str = s["timestamp"][11:16]
            has_mentions = s["mentions_count"] > 0
            css_class = "snapshot has-mentions" if has_mentions else "snapshot"
            
            screenshot_html = ""
            if s.get("screenshot"):
                screenshot_html = f'<a href="screenshots/{s["screenshot"]}" class="screenshot-link" target="_blank">📷 Screenshot</a>'
            
            html += f"""
        <div class="{css_class}">
            <span class="snapshot-time">{time_str} UTC</span>
            {screenshot_html}
            <strong> — {s['mentions_count']} omnämnanden</strong>
"""
            
            for m in s.get("mentions", []):
                headline = m.get("headline") or m.get("text", "")[:80]
                html += f"""
            <div class="mention">
                {headline}
                <br><small>Sektion: {m.get('section', 'unknown')}</small>
            </div>
"""
            
            html += """
        </div>
"""
        
        html += """
    </div>
"""
    
    html += f"""
    <footer>
        Rapport genererad: {datetime.now().strftime('%Y-%m-%d %H:%M')} · 
        Data: <a href="snapshots.json">snapshots.json</a>
    </footer>
</body>
</html>
"""
    
    REPORT_FILE.write_text(html, encoding="utf-8")
    print(f"Rapport genererad: {REPORT_FILE}")
    return REPORT_FILE


if __name__ == "__main__":
    generate_report()
