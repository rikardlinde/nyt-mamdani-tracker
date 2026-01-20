#!/usr/bin/env python3
"""Exportera snapshots till CSV för kalkylbladsanalys."""

import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
SNAPSHOTS_FILE = DATA_DIR / "snapshots.json"
CSV_FILE = DATA_DIR / "mamdani_mentions.csv"


def export_csv():
    if not SNAPSHOTS_FILE.exists():
        print("Ingen data att exportera.")
        return

    snapshots = json.loads(SNAPSHOTS_FILE.read_text(encoding="utf-8"))

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Tidpunkt (UTC)",
            "Datum",
            "Tid",
            "Antal omnämnanden",
            "Rubrik",
            "Sektion",
            "Länk",
            "Screenshot"
        ])

        for snap in snapshots:
            timestamp = snap["timestamp"]
            date = timestamp[:10]
            time = timestamp[11:16]
            count = snap["mentions_count"]
            screenshot = snap.get("screenshot", "")

            if snap["mentions"]:
                for m in snap["mentions"]:
                    writer.writerow([
                        timestamp,
                        date,
                        time,
                        count,
                        m.get("headline") or m.get("text", "")[:100],
                        m.get("section", ""),
                        m.get("href", ""),
                        screenshot
                    ])
            else:
                writer.writerow([
                    timestamp,
                    date,
                    time,
                    0,
                    "",
                    "",
                    "",
                    screenshot
                ])

    print(f"Exporterat till {CSV_FILE}")


if __name__ == "__main__":
    export_csv()
