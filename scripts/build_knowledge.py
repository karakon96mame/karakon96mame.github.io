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
CATEGORY_ENDPOINT = os.environ.get("MICROCMS_CATEGORY_ENDPOINT", "categories").strip("/")
TAG_ENDPOINT = os.environ.get("MICROCMS_TAG_ENDPOINT", "tags").strip("/")


def fetch_all(endpoint: str = ENDPOINT) -> list[dict]:
    if not SERVICE or not API_KEY:
        raise SystemExit("MICROCMS_SERVICE_DOMAIN and MICROCMS_API_KEY are required")
    result: list[dict] = []
    offset = 0
    while True:
        query = urlencode({"limit": 100, "offset": offset, "orders": "-publishedAt"})
        url = f"https://{SERVICE}.microcms.io/api/v1/{endpoint}?{query}"
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


def item_categories(item: dict) -> list[dict]:
    value = item.get("categories") or []
    if isinstance(value, dict):
        value = [value]
    return [category for category in value if isinstance(category, dict) and category.get("id")]


def item_tags(item: dict) -> list[dict]:
    value = item.get("tags") or []
    if isinstance(value, dict):
        value = [value]
    return [tag for tag in value if isinstance(tag, dict) and tag.get("id")]


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
    :root{{--green:#28714f;--green-dark:#174b38;--pale:#e9f3ec;--ink:#24322d;--muted:#66736e;--paper:#fff;--soft:#f6f8f6;--line:#d9e3de}}
    [data-theme="dark"]{{--green:#8ec9a8;--green-dark:#d1eadb;--pale:#263b31;--ink:#edf4f0;--muted:#b8c8c0;--paper:#17231e;--soft:#101914;--line:#35483f}}
    *{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;color:var(--ink);background:var(--soft);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif;line-height:1.8}}
    a{{color:var(--green)}} .topic-header{{background:color-mix(in srgb,var(--paper) 96%,transparent);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10;box-shadow:0 3px 16px rgba(24,67,48,.08)}}
    .topic-header-inner{{max-width:1280px;margin:auto;padding:8px 18px 10px}}
    .topic-brand-row{{display:flex;align-items:center;gap:14px;min-width:0}}
    .topic-brand{{display:flex;align-items:center;gap:10px;color:var(--ink);font-weight:800;text-decoration:none;white-space:nowrap}}
    .topic-logo{{width:54px;height:54px;object-fit:contain}}
    .topic-brand-name{{font-size:1rem;line-height:1.3}} .topic-tagline{{color:var(--muted);font-size:.8rem;line-height:1.45}}
    .topic-theme{{margin-left:auto;border:1px solid var(--line);border-radius:999px;width:40px;height:40px;background:var(--paper);color:var(--ink);font-size:1rem;cursor:pointer}}
    .topic-nav-row{{display:flex;align-items:center;gap:8px;margin-top:7px}}
    .topic-nav{{display:flex;align-items:center;gap:3px;min-width:0;padding:4px;background:var(--pale);border-radius:12px}}
    .topic-nav a{{padding:7px 10px;border-radius:9px;color:var(--ink);font-size:.85rem;font-weight:750;text-decoration:none;white-space:nowrap}}
    .topic-nav a:hover,.topic-nav a[aria-current="page"]{{background:var(--green);color:#fff}}
    .topic-actions{{display:flex;gap:6px;margin-left:auto}} .topic-action{{display:flex;align-items:center;justify-content:center;min-height:35px;padding:6px 10px;border-radius:10px;color:#fff!important;font-size:.76rem;font-weight:800;line-height:1.25;text-align:center;text-decoration:none;box-shadow:0 3px 10px rgba(28,36,46,.16)}}
    .topic-action-book{{background:linear-gradient(135deg,#e85d2a,#c83e22)}} .topic-action-visit{{background:linear-gradient(135deg,#168b86,#0b6664)}}
    main{{max-width:960px;margin:38px auto;padding:0 20px}} .topic-card,.topic-article{{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:clamp(24px,4vw,46px);box-shadow:0 8px 28px rgba(22,75,55,.07)}}
    h1{{font-size:clamp(1.65rem,4vw,2.45rem);line-height:1.35;margin-top:0}} h2{{margin-top:2em;border-left:5px solid var(--green);padding-left:.7em}}
    img{{max-width:100%;height:auto;border-radius:12px}} .topic-list{{display:grid;gap:18px}} .topic-item{{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:24px;text-decoration:none;color:inherit;box-shadow:0 5px 18px rgba(22,75,55,.045);transition:.2s ease}}
    .topic-item:hover{{border-color:var(--green);transform:translateY(-2px)}} .topic-item h2{{margin:.3em 0;border:0;padding:0;font-size:1.25rem}}
    .topic-meta{{color:var(--muted);font-size:.92rem}} .topic-summary{{margin:.5em 0 0}} .topic-back{{display:inline-block;margin-bottom:18px}}
    .topic-categories{{display:flex;gap:8px;flex-wrap:wrap;margin:.65em 0}} .topic-category{{display:inline-block;border-radius:999px;padding:.25em .8em;background:#e5f0eb;color:var(--green);font-weight:700;font-size:.88rem;text-decoration:none}}
    .topic-tags{{display:flex;gap:7px;flex-wrap:wrap;margin:.55em 0}} .topic-tag{{display:inline-block;border-radius:6px;padding:.18em .55em;background:var(--soft);color:var(--muted);font-size:.82rem;text-decoration:none}} .topic-tag::before{{content:"#"}}
    .topic-filters{{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}} .topic-filter{{border:1px solid var(--green);border-radius:999px;padding:8px 14px;background:var(--paper);color:var(--green);font:inherit;font-weight:700;cursor:pointer}} .topic-filter[aria-pressed="true"]{{background:var(--green);color:#fff}}
    .topic-footer{{margin-top:56px;background:#173e33;color:#fff}} .topic-footer-inner{{max-width:1120px;margin:auto;padding:34px 20px;display:grid;grid-template-columns:1.2fr 1fr;gap:24px}} .topic-footer a{{color:#fff}} .topic-footer-title{{font-weight:800;font-size:1.05rem}} .topic-footer-links{{display:flex;gap:10px 18px;flex-wrap:wrap;align-content:start}} .topic-copyright{{grid-column:1/-1;border-top:1px solid #ffffff35;padding-top:14px;font-size:.78rem;color:#dce9e2}}
    @media(max-width:900px){{.topic-nav-row{{align-items:stretch;flex-direction:column}}.topic-nav{{overflow-x:auto}}.topic-actions{{width:100%;margin:0;display:grid;grid-template-columns:1fr 1fr}}}}
    @media(max-width:600px){{.topic-header-inner{{padding:7px 10px 9px}}.topic-logo{{width:64px;height:64px}}.topic-brand-row{{align-items:flex-start}}.topic-brand{{flex-direction:column;gap:1px}}.topic-brand-name{{font-size:.75rem}}.topic-tagline{{align-self:center;font-size:.72rem;padding-top:8px}}.topic-nav a{{font-size:.77rem;padding:7px 8px}}.topic-action{{font-size:.74rem}}main{{margin:24px auto;padding:0 14px}}.topic-footer-inner{{grid-template-columns:1fr}}.topic-copyright{{grid-column:auto}}}}
  </style>
</head>
<body>
<header class="topic-header"><div class="topic-header-inner">
  <div class="topic-brand-row">
    <a class="topic-brand" href="/"><img class="topic-logo" src="/images/logo/osumasi.png" alt="くろまめはりきゅう院ロゴ"><span class="topic-brand-name">くろまめ<br>はりきゅう院</span></a>
    <span class="topic-tagline">昔ながらの接骨院ぽい治療院から、<br>訪問マッサージもあります</span>
    <button class="topic-theme" type="button" id="topic-theme" aria-label="ダーク／ライトモード切替">◐</button>
  </div>
  <div class="topic-nav-row">
    <nav class="topic-nav" aria-label="サイトメニュー"><a href="/">台町店</a><a href="/visit.html">訪問マッサージ</a><a href="/acupuncture.html">はりきゅう</a><a href="/shop.html">健康グッズ</a><a href="/column.html" aria-current="page">健康コラム</a></nav>
    <div class="topic-actions" aria-label="予約・お問い合わせ"><a class="topic-action topic-action-book" href="https://script.google.com/macros/s/AKfycbzxj8ITX23qJl1l47Oz4WEmYuvHqCZ6e7rmhiN1S73aSaMsIkGbous3P3MDijdkSaQI/exec" target="_blank" rel="noopener noreferrer">📅 台町店予約</a><a class="topic-action topic-action-visit" href="/visit.html#apply">✉ 訪問マッサージお問い合わせ</a></div>
  </div>
</div></header>
<main>{body}</main>
<footer class="topic-footer"><div class="topic-footer-inner"><div><a class="topic-footer-title" href="/">くろまめ鍼灸マッサージ院</a><p>横浜市神奈川区台町の鍼灸・マッサージ院です。訪問マッサージにも対応しています。</p></div><nav class="topic-footer-links" aria-label="フッターメニュー"><a href="/">台町店</a><a href="/visit.html">訪問マッサージ</a><a href="/acupuncture.html">はりきゅう</a><a href="/shop.html">健康グッズ</a><a href="/column.html">健康コラム</a></nav><small class="topic-copyright">© くろまめ鍼灸マッサージ院</small></div></footer>
<script>(function(){{var html=document.documentElement;var theme=localStorage.getItem('km-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');html.setAttribute('data-theme',theme);document.getElementById('topic-theme').addEventListener('click',function(){{theme=html.getAttribute('data-theme')==='dark'?'light':'dark';html.setAttribute('data-theme',theme);localStorage.setItem('km-theme',theme);}});}})();</script>
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
    categories = item_categories(item)
    tags = item_tags(item)
    category_html = "".join(f'<a class="topic-category" href="/column/category/{text(category["id"])}.html">{text(category.get("name") or "カテゴリー")}</a>' for category in categories)
    categories_html = f'<p class="topic-categories">{category_html}</p>' if category_html else ""
    tag_html = "".join(f'<a class="topic-tag" href="/column/tag/{text(tag["id"])}.html">{text(tag.get("name") or "タグ")}</a>' for tag in tags)
    tags_html = f'<p class="topic-tags">{tag_html}</p>' if tag_html else ""
    image_html = f'<p><img src="{text(image.get("url"))}" alt="{text(title)}"></p>' if isinstance(image, dict) and image.get("url") else ""
    body = f'''<a class="topic-back" href="/column.html">← 健康コラム一覧へ</a>
<article class="topic-article">
  <h1>{text(title)}</h1>
  {categories_html}
  {tags_html}
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
    if categories:
        structured["articleSection"] = [str(category.get("name") or "") for category in categories]
    if tags:
        structured["keywords"] = [str(tag.get("name") or "") for tag in tags]
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
    categories = fetch_all(CATEGORY_ENDPOINT)
    tags = fetch_all(TAG_ENDPOINT)
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
        linked_categories = item_categories(item)
        category_ids = " ".join(str(category["id"]) for category in linked_categories)
        category_badges = "".join(f'<span class="topic-category">{text(category.get("name") or "カテゴリー")}</span>' for category in linked_categories)
        tag_badges = "".join(f'<span class="topic-tag">{text(tag.get("name") or "タグ")}</span>' for tag in item_tags(item))
        cards.append(f'<a class="topic-item" data-categories="{text(category_ids)}" href="/column/{text(filename)}"><span class="topic-meta">{text(iso_date(date))}</span><div class="topic-categories">{category_badges}</div><div class="topic-tags">{tag_badges}</div><h2>{text(title)}</h2><p class="topic-summary">{text(summary)}</p></a>')
        urls.append(f"{BASE_URL}column/{filename}")
    for old in article_dir.glob("*.html"):
        if old.name not in live_files:
            old.unlink()
    filters = '<button class="topic-filter" type="button" data-filter="all" aria-pressed="true">すべて</button>' + "".join(f'<button class="topic-filter" type="button" data-filter="{text(category["id"])}" aria-pressed="false">{text(category.get("name") or "カテゴリー")}</button>' for category in categories)
    filter_script = '''<script>document.querySelectorAll('.topic-filter').forEach(function(button){button.addEventListener('click',function(){var selected=button.dataset.filter;document.querySelectorAll('.topic-filter').forEach(function(item){item.setAttribute('aria-pressed',String(item===button));});document.querySelectorAll('.topic-item').forEach(function(card){var values=(card.dataset.categories||'').split(' ');card.hidden=selected!=='all'&&!values.includes(selected);});});});</script>'''
    listing = '<section class="topic-card"><h1>健康コラム</h1><p>鍼灸・マッサージや日々の健康に役立つ情報をお届けします。</p></section><div class="topic-filters" aria-label="カテゴリーで絞り込む">' + filters + '</div><div class="topic-list">' + ("".join(cards) if cards else "<p>記事を準備しています。</p>") + "</div>" + filter_script
    (OUT / "column.html").write_text(shell("健康コラム｜くろまめ鍼灸マッサージ院", "鍼灸・マッサージや日々の健康に役立つ情報を紹介します。", f"{BASE_URL}column.html", listing), encoding="utf-8")

    category_dir = article_dir / "category"
    category_dir.mkdir(exist_ok=True)
    live_category_files: set[str] = set()
    for category in categories:
        category_id = re.sub(r"[^a-zA-Z0-9_-]", "", str(category.get("id", "")))
        if not category_id:
            continue
        category_name = str(category.get("name") or "カテゴリー")
        category_cards = [card for card, item in zip(cards, items) if category_id in [str(c.get("id")) for c in item_categories(item)]]
        category_body = f'<a class="topic-back" href="/column.html">← 健康コラム一覧へ</a><section class="topic-card"><h1>{text(category_name)}の記事</h1></section><div class="topic-list" style="margin-top:20px">' + ("".join(category_cards) if category_cards else "<p>このカテゴリーの記事は準備中です。</p>") + "</div>"
        category_filename = f"{category_id}.html"
        live_category_files.add(category_filename)
        category_url = f"{BASE_URL}column/category/{category_filename}"
        (category_dir / category_filename).write_text(shell(f"{category_name}の記事｜健康コラム", f"{category_name}に関する健康コラムの記事一覧です。", category_url, category_body), encoding="utf-8")
        urls.append(category_url)
    for old in category_dir.glob("*.html"):
        if old.name not in live_category_files:
            old.unlink()

    tag_dir = article_dir / "tag"
    tag_dir.mkdir(exist_ok=True)
    live_tag_files: set[str] = set()
    for tag in tags:
        tag_id = re.sub(r"[^a-zA-Z0-9_-]", "", str(tag.get("id", "")))
        if not tag_id:
            continue
        tag_name = str(tag.get("name") or "タグ")
        tag_cards = [card for card, item in zip(cards, items) if tag_id in [str(t.get("id")) for t in item_tags(item)]]
        tag_body = f'<a class="topic-back" href="/column.html">← 健康コラム一覧へ</a><section class="topic-card"><h1>#{text(tag_name)} の記事</h1></section><div class="topic-list" style="margin-top:20px">' + ("".join(tag_cards) if tag_cards else "<p>このタグの記事は準備中です。</p>") + "</div>"
        tag_filename = f"{tag_id}.html"
        live_tag_files.add(tag_filename)
        tag_url = f"{BASE_URL}column/tag/{tag_filename}"
        (tag_dir / tag_filename).write_text(shell(f"{tag_name}の記事｜健康コラム", f"{tag_name}に関する健康コラムの記事一覧です。", tag_url, tag_body), encoding="utf-8")
        urls.append(tag_url)
    for old in tag_dir.glob("*.html"):
        if old.name not in live_tag_files:
            old.unlink()
    update_sitemap(urls)
    print(f"Built {len(items)} health column articles")


if __name__ == "__main__":
    main()
