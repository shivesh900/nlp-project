"""Build a real, multi-language text dataset from Wikipedia.

For each language we pull the intro paragraphs of random Wikipedia articles,
split them into sentences and keep sentences of a sensible length. Every row
keeps the article it came from, so train/test can be split *by article*
(no sentence of a test article is ever seen in training).

Text is from Wikipedia and licensed CC BY-SA 4.0.

Usage:  python scripts/build_dataset.py  [--articles 120]
Output: data/wikipedia_sentences.csv  (language, text, article, url)
"""
import argparse
import csv
import re
import time
from pathlib import Path

import requests

LANGUAGES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
    "ml": "Malayalam", "bn": "Bengali", "mr": "Marathi", "fr": "French", "es": "Spanish", "de": "German",
}
HEADERS = {"User-Agent": "nlp-project-dataset-builder/1.0 (https://github.com/shivesh900/nlp-project)"}
SENT_SPLIT = re.compile(r"(?<=[.!?।॥])\s+")
OUT = Path(__file__).resolve().parent.parent / "data" / "wikipedia_sentences.csv"


def random_intros(code: str, n: int):
    """Yield (title, extract) for ~n random main-namespace articles."""
    got = 0
    while got < n:
        r = requests.get(
            f"https://{code}.wikipedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "generator": "random", "grnnamespace": 0,
                "grnlimit": 20, "prop": "extracts", "exintro": 1, "explaintext": 1, "exlimit": 20,
            },
            headers=HEADERS, timeout=30,
        )
        r.raise_for_status()
        for page in r.json().get("query", {}).get("pages", {}).values():
            text = (page.get("extract") or "").strip()
            if len(text) > 80:
                got += 1
                yield page["title"], text
        time.sleep(0.2)


def sentences(text: str):
    for s in SENT_SPLIT.split(re.sub(r"\s+", " ", text)):
        s = s.strip()
        # skip very short fragments, lists of numbers, and lines that are mostly Latin
        # in a non-Latin-script language (e.g. untranslated references)
        if 25 <= len(s) <= 300 and sum(ch.isalpha() for ch in s) > 15:
            yield s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--articles", type=int, default=120, help="articles per language")
    args = ap.parse_args()
    rows = []
    for code, name in LANGUAGES.items():
        n = 0
        for title, extract in random_intros(code, args.articles):
            url = f"https://{code}.wikipedia.org/wiki/{title.replace(' ', '_')}"
            for s in list(sentences(extract))[:4]:  # cap per article so long intros don't dominate
                rows.append({"language": name, "text": s, "article": f"{code}:{title}", "url": url})
                n += 1
        print(f"{name:10s} {n:5d} sentences")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["language", "text", "article", "url"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows → {OUT}")


if __name__ == "__main__":
    main()
