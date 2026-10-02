"""Build static health-column pages from microCMS.

Required environment variables:
  MICROCMS_SERVICE_DOMAIN  e.g. example (not example.microcms.io)
  MICROCMS_API_KEY         read-only API key

Optional:
  MICROCMS_ENDPOINT        default: column
  SITE_OUTPUT_DIR          directory containing the published HTML files
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://karakon96mame.github.io/"
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("SITE_OUTPUT_DIR", ROOT / "outputs" / "karakon96mame.github.io"))
SERVICE = os.environ.get("MICROCMS_SERVICE_DOMAIN", "").strip()
API_KEY = os.environ.get("MICROCMS_API_KEY", "").strip()
ENDPOINT = os.environ.get("MICROCMS_ENDPOINT", "column").strip("/")


def fetch_all() -> list[dict]:
    if not SERVICE or not API_KEY:
        raise SystemExit("MICROCMS_SERVICE_DOMAIN and MICROCMS_API_KEY are required")
    result: list[dict] = []
    offset = 0
    while True:
        query = urlencode({"limit": 100, "offset": offset, "orders": "-publishedAt"})
        url = f"https://{SERVICE}.microcms.io/api/v1/{ENDPOINT}?{query}"
        request = Request(url, headers={"X-MICROCMS-API-KEY": API_KEY, "User-Agent": "kuromame-static-builder"})
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        contents = payload.get("contents", [])
        result.extend(contents)
        offset += len(contents)
        if not contents or offset >= int(payload.get("totalCount", len(result))):
            return result


def text(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def plain(value: object) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(value or ""))).strip()


def iso_date(value: object) -> str:
    raw = str(value or "")[:10]
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%Y年%-m月%-d日")
    except (ValueError, OSError):
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d")
            return f"{dt.year}年{dt.month}月{dt.day}日"
        except ValueError:
            return raw


def shell(title: str, description: str, canonical: str, body: str, structured: dict | None = None) -> str:
    json_ld = ""
    if structured:
        json_ld = '<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False) + "</script>"
    return f'''<!doctype html>
<html lang="ja" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{text(title)}</title>
  <meta name="description" content="{text(description)}">
  <link rel="canonical" href="{text(canonical)}">
  {json_ld}
  <style>
    :root{{--green:#1d6b55;--pale:#cee0d8;--ink:#24322d;--paper:#fff;--soft:#f5f8f6}}
    *{{box-sizing:border-box}} body{{margin:0;color:var(--ink);background:var(--soft);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif;line-height:1.8}}
    a{{color:var(--green)}} .topic-header{{background:var(--paper);border-bottom:1px solid #d9e3de;position:sticky;top:0;z-index:10}}
    .topic-nav{{max-width:1120px;margin:auto;padding:12px 20px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}}
    .topic-brand{{font-weight:800;text-decoration:none;margin-right:auto}} .topic-nav a:not(.topic-brand){{font-weight:650;text-decoration:none}}
    main{{max-width:920px;margin:32px auto;padding:0 20px}} .topic-card,.topic-article{{background:var(--paper);border:1px solid #d9e3de;border-radius:18px;padding:clamp(22px,4vw,44px);box-shadow:0 8px 28px #164b3710}}
    h1{{font-size:clamp(1.65rem,4vw,2.45rem);line-height:1.35;margin-top:0}} h2{{margin-top:2em;border-left:5px solid var(--green);padding-left:.7em}}
    img{{max-width:100%;height:auto;border-radius:12px}} .topic-list{{display:grid;gap:18px}} .topic-item{{background:var(--paper);border:1px solid #d9e3de;border-radius:14px;padding:22px;text-decoration:none;color:inherit}}
    .topic-item:hover{{border-color:var(--green);transform:translateY(-2px)}} .topic-item h2{{margin:.3em 0;border:0;padding:0;font-size:1.25rem}}
    .topic-meta{{color:#607069;font-size:.92rem}} .topic-summary{{margin:.5em 0 0}} .topic-back{{display:inline-block;margin-bottom:18px}}
    footer{{margin-top:48px;padding:30px 20px;text-align:center;background:#173e33;color:#fff}} footer a{{color:#fff}}
  </style>
</head>
<body>
<header class="topic-header"><nav class="topic-nav" aria-label="サイトメニュー">
  <a class="topic-brand" href="/">くろまめ鍼灸マッサージ院</a>
  <a href="/">台町店</a><a href="/visit.html">訪問マッサージ</a><a href="/acupuncture.html">はりきゅう</a><a href="/shop.html">健康グッズ</a><a href="/column.html">健康コラム</a>
</nav></header>
<main>{body}</main>
<footer><a href="/">くろまめ鍼灸マッサージ院</a><br><small>© くろまめ鍼灸マッサージ院</small></footer>
</body></html>'''


def build_article(item: dict) -> tuple[str, str]:
    content_id = re.sub(r"[^a-zA-Z0-9_-]", "", str(item.get("id", "")))
    if not content_id:
        raise ValueError("microCMS content without a valid id")
    title = str(item.get("title") or "健康コラム")
    content = str(item.get("content") or "")
    description = str(item.get("description") or plain(content)[:120])
    author = str(item.get("author") or "くろまめ鍼灸マッサージ院")
    published = item.get("publishedAt") or item.get("createdAt") or ""
    updated = item.get("updatedAt") or published
    canonical = f"{BASE_URL}column/{content_id}.html"
    image = item.get("eyecatch") or {}
    image_html = f'<p><img src="{text(image.get("url"))}" alt="{text(title)}"></p>' if isinstance(image, dict) and image.get("url") else ""
    body = f'''<a class="topic-back" href="/column.html">← 健康コラム一覧へ</a>
<article class="topic-article">
  <h1>{text(title)}</h1>
  <p class="topic-meta">公開日：{text(iso_date(published))}　更新日：{text(iso_date(updated))}　執筆：{text(author)}</p>
  {image_html}<div class="topic-body">{content}</div>
</article>'''
    structured = {
        "@context": "https://schema.org", "@type": "Article", "headline": title,
        "datePublished": published, "dateModified": updated,
        "author": {"@type": "Organization", "name": author},
        "publisher": {"@type": "Organization", "name": "くろまめ鍼灸マッサージ院"},
        "mainEntityOfPage": canonical,
    }
    if isinstance(image, dict) and image.get("url"):
        structured["image"] = [image["url"]]
    return content_id, shell(f"{title}｜くろまめ鍼灸マッサージ院", description, canonical, body, structured)


def update_sitemap(urls: list[str]) -> None:
    path = OUT / "sitemap.xml"
    existing = path.read_text(encoding="utf-8") if path.exists() else '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>\n'
    existing = re.sub(r"\s*<url><loc>https://karakon96mame\.github\.io/column(?:\.html|/[^<]+)</loc></url>", "", existing)
    nodes = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in urls)
    existing = existing.replace("</urlset>", nodes + "\n</urlset>")
    path.write_text(existing, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    article_dir = OUT / "column"
    article_dir.mkdir(exist_ok=True)
    items = fetch_all()
    live_files: set[str] = set()
    cards: list[str] = []
    urls = [f"{BASE_URL}column.html"]
    for item in items:
        content_id, page = build_article(item)
        filename = f"{content_id}.html"
        live_files.add(filename)
        (article_dir / filename).write_text(page, encoding="utf-8")
        title = str(item.get("title") or "健康コラム")
        summary = str(item.get("description") or plain(item.get("content"))[:100])
        date = item.get("publishedAt") or item.get("createdAt") or ""
        cards.append(f'<a class="topic-item" href="/column/{text(filename)}"><span class="topic-meta">{text(iso_date(date))}</span><h2>{text(title)}</h2><p class="topic-summary">{text(summary)}</p></a>')
        urls.append(f"{BASE_URL}column/{filename}")
    for old in article_dir.glob("*.html"):
        if old.name not in live_files:
            old.unlink()
    listing = '<section class="topic-card"><h1>健康コラム</h1><p>鍼灸・マッサージや日々の健康に役立つ情報をお届けします。</p></section><div class="topic-list" style="margin-top:20px">' + ("".join(cards) if cards else "<p>記事を準備しています。</p>") + "</div>"
    (OUT / "column.html").write_text(shell("健康コラム｜くろまめ鍼灸マッサージ院", "鍼灸・マッサージや日々の健康に役立つ情報を紹介します。", f"{BASE_URL}column.html", listing), encoding="utf-8")
    update_sitemap(urls)
    print(f"Built {len(items)} health column articles")


if __name__ == "__main__":
    main()
