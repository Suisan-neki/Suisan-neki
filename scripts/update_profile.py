"""Refresh public Qiita articles without requiring account credentials."""
import html
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


def render_articles(items):
    rows = []
    for item in items:
        if item.get("private"):
            continue
        url = item["url"]
        if not url.startswith("https://qiita.com/"):
            raise ValueError("Unexpected article URL")
        title = html.escape(" ".join(item["title"].split()))
        date = html.escape(item["created_at"][:10])
        rows.append(f'<li><a href="{html.escape(url, quote=True)}">{title}</a><br><sub>{date}</sub></li>')
    return "<ul>\n" + "\n".join(rows[:3]) + "\n</ul>" if rows else '[Qiitaの記事一覧](https://qiita.com/Suisan-neki)'


def main():
    request = Request(
        "https://qiita.com/api/v2/users/Suisan-neki/items?per_page=3",
        headers={"User-Agent": "Suisan-neki-profile", "Accept": "application/json"},
    )
    with urlopen(request, timeout=30) as response:
        items = json.load(response)
    if not isinstance(items, list):
        raise ValueError("Unexpected Qiita response")
    path = Path(__file__).resolve().parents[1] / "README.md"
    text = path.read_text(encoding="utf-8")
    block = "<!-- QIITA:START -->\n" + render_articles(items) + "\n<!-- QIITA:END -->"
    updated, count = re.subn(r"<!-- QIITA:START -->.*?<!-- QIITA:END -->", lambda _: block, text, flags=re.S)
    if count != 1:
        raise ValueError("Expected exactly one Qiita block")
    if updated != text:
        path.write_text(updated, encoding="utf-8")
    print(f"Qiita articles checked: {len(items)}")


if __name__ == "__main__":
    main()
