#!/usr/bin/env python3
"""
NYT Mamdani Monitor
Övervakar nytimes.com för omnämnanden av "Mamdani" och sparar data + screenshots.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


DATA_DIR = Path(__file__).parent / "data"
SNAPSHOTS_FILE = DATA_DIR / "snapshots.json"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
NYT_URL = "https://www.nytimes.com/"
SEARCH_TERM = "mamdani"


def load_snapshots() -> list:
    """Ladda befintliga snapshots från JSON-fil."""
    if SNAPSHOTS_FILE.exists():
        return json.loads(SNAPSHOTS_FILE.read_text(encoding="utf-8"))
    return []


def save_snapshots(snapshots: list) -> None:
    """Spara snapshots till JSON-fil."""
    SNAPSHOTS_FILE.write_text(
        json.dumps(snapshots, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def find_mamdani_mentions(html: str, base_url: str) -> list:
    """
    Hitta alla omnämnanden av Mamdani på sidan.
    Returnerar lista med dict: {text, href, section, context}
    """
    soup = BeautifulSoup(html, "html.parser")
    mentions = []
    
    # Hitta alla länkar och element som innehåller "Mamdani"
    for element in soup.find_all(string=re.compile(SEARCH_TERM, re.IGNORECASE)):
        # Hitta närmaste länk-förälder
        link = element.find_parent("a")
        href = None
        if link and link.get("href"):
            href = urljoin(base_url, link["href"])
        
        # Hitta section/område på sidan
        section = find_section(element)
        
        # Hämta kontext (omgivande text)
        context = get_context(element)
        
        # Hämta rubriktext om det är en rubrik
        headline = find_headline(element)
        
        mentions.append({
            "text": element.strip(),
            "headline": headline,
            "href": href,
            "section": section,
            "context": context[:500] if context else None  # Begränsa längd
        })
    
    # Deduplicera baserat på href eller text
    seen = set()
    unique_mentions = []
    for m in mentions:
        key = m["href"] or m["text"]
        if key not in seen:
            seen.add(key)
            unique_mentions.append(m)
    
    return unique_mentions


def find_section(element) -> str:
    """Försök identifiera vilken sektion på sidan elementet finns i."""
    # Leta efter section, nav, eller element med data-testid
    for parent in element.parents:
        if parent.name == "section":
            # Kolla efter aria-label eller data-block-tracking-id
            label = parent.get("aria-label") or parent.get("data-block-tracking-id")
            if label:
                return label
        
        # NYT använder ofta data-testid
        testid = parent.get("data-testid")
        if testid:
            return testid
    
    return "unknown"


def get_context(element) -> str:
    """Hämta omgivande text för kontext."""
    # Gå upp till närmaste container
    for parent in element.parents:
        if parent.name in ["article", "div", "section", "li"]:
            text = parent.get_text(separator=" ", strip=True)
            if len(text) > 50:  # Tillräckligt med kontext
                return text
    return element.strip()


def find_headline(element) -> str | None:
    """Hitta rubrik om elementet är del av en artikel-länk."""
    for parent in element.parents:
        if parent.name == "a":
            # Kolla om det finns en h2/h3 i länken
            headline = parent.find(["h1", "h2", "h3", "h4"])
            if headline:
                return headline.get_text(strip=True)
            # Annars returnera hela länktexten om den är rimlig
            text = parent.get_text(strip=True)
            if len(text) < 200:
                return text
    return None


def take_screenshot(page, timestamp: str) -> str:
    """Ta screenshot efter att ha scrollat igenom sidan för att ladda allt."""
    filename = f"nyt_{timestamp}.png"
    filepath = SCREENSHOTS_DIR / filename
    
    # Scrolla genom hela sidan för att trigga lazy loading
    page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 800;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 200);
            });
        }
    """)
    
    # Vänta på att bilder laddas
    page.wait_for_timeout(3000)
    
    # Scrolla tillbaka till toppen
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)
    
    # Ta full-page screenshot
    page.screenshot(path=str(filepath), full_page=True)
    
    return filename


def run_monitor():
    """Kör övervakningen."""
    print(f"Startar NYT Mamdani Monitor - {datetime.now(timezone.utc).isoformat()}")
    
    # Säkerställ att mappar finns
    DATA_DIR.mkdir(exist_ok=True)
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        # Starta browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        # Hämta NYT
        print(f"Hämtar {NYT_URL}...")
        page.goto(NYT_URL, wait_until="domcontentloaded", timeout=90000)
        
        # Vänta lite extra för dynamiskt innehåll
        page.wait_for_timeout(5000)
        
        # Hämta HTML
        html = page.content()
        
        # Sök efter Mamdani
        mentions = find_mamdani_mentions(html, NYT_URL)
        
        # Skapa timestamp
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Ta screenshot om det finns omnämnanden (eller alltid för debugging)
        screenshot_file = None
        if mentions:
            screenshot_file = take_screenshot(page, timestamp)
            print(f"Screenshot sparat: {screenshot_file}")
        
        browser.close()
    
    # Skapa snapshot-post
    snapshot = {
        "timestamp": now.isoformat(),
        "url": NYT_URL,
        "mentions_count": len(mentions),
        "mentions": mentions,
        "screenshot": screenshot_file
    }
    
    # Ladda och uppdatera snapshots
    snapshots = load_snapshots()
    snapshots.append(snapshot)
    save_snapshots(snapshots)
    
    # Rapport
    print(f"\nResultat:")
    print(f"  Tidpunkt: {now.isoformat()}")
    print(f"  Omnämnanden: {len(mentions)}")
    
    if mentions:
        print(f"\n  Hittade:")
        for m in mentions:
            print(f"    - {m['headline'] or m['text'][:60]}")
            if m["href"]:
                print(f"      Länk: {m['href']}")
            print(f"      Sektion: {m['section']}")
    else:
        print("  Inga omnämnanden av Mamdani på förstasidan just nu.")
    
    return snapshot


if __name__ == "__main__":
    run_monitor()
