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
    :root,[data-theme="light"]{{--green:#016b5f;--ink:#28251d;--muted:#5a5750;--paper:#f9f8f5;--soft:#f7f6f2;--line:#d4d1ca;--pale:#cee0d8;--text-xs:clamp(.75rem,.7rem + .25vw,.875rem);--text-sm:clamp(.875rem,.8rem + .35vw,1rem);--text-lg:clamp(1.125rem,1rem + .75vw,1.5rem);--font-display:"Noto Serif JP",Georgia,serif;--font-body:"Noto Sans JP","Helvetica Neue",sans-serif;--header-h:64px}}
    [data-theme="dark"]{{--green:#3fa890;--ink:#cdccca;--muted:#8f8e8c;--paper:#1c1b19;--soft:#171614;--line:#393836;--pale:#1e3530}}
    [data-vision]{{--soft:#fffde7;--paper:#fffff0;--ink:#1a1000;--muted:#3a2e00;--line:#8b7000;--green:#5c3d00;font-size:120%!important}} [data-vision] *{{letter-spacing:.03em}} [data-vision] a{{text-decoration:underline}}
    [data-fontsize="large"]{{font-size:115%}} [data-fontsize="xlarge"]{{font-size:130%}}
    *{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;color:var(--ink);background:var(--soft);font-family:var(--font-body);line-height:1.8}} button{{font:inherit;color:inherit;cursor:pointer}} a{{color:var(--green);text-decoration:none}}
    .site-header{{position:fixed;top:3px;left:0;right:0;padding:12px 0;background:var(--paper);border-bottom:1px solid var(--line);z-index:1000}}
    .header-inner{{display:flex;align-items:center;justify-content:flex-start;gap:1rem;width:100%;padding-inline:1rem}} .header-left{{flex-shrink:0}} .logo{{display:flex;align-items:center}} .logo-img{{display:block;width:128px;height:128px;object-fit:contain}} .mobile-logo-name{{display:none}}
    .header-right{{display:flex;flex:1;min-width:0;flex-direction:column}} .logo-text-wrap{{display:flex;align-items:baseline;gap:8px}} .logo-text{{font-family:var(--font-display);font-size:var(--text-sm);font-weight:700}} .logo-sub{{margin-left:8px;color:var(--muted);font-size:var(--text-xs)}}
    .main-nav{{display:flex;flex-direction:column;align-items:flex-start;gap:4px;width:100%}} .nav-row{{display:flex;align-items:center;flex-wrap:wrap;gap:6px;width:100%}} .primary-nav-links{{display:flex;align-items:center;gap:6px;padding:7px 9px;background:var(--pale);border:1px solid var(--line);border-radius:12px}} .main-nav a{{padding:.5rem .7rem;border-radius:6px;color:var(--ink);font-size:.9rem;font-weight:700;white-space:nowrap}} .main-nav a:hover,.main-nav a.active{{background:var(--green);color:#fff}}
    .header-quick-actions{{display:flex;gap:6px}} .header-quick-actions-desktop{{margin-left:auto;padding-right:53px}} .header-quick-actions-mobile{{display:none}} .header-action{{display:flex;align-items:center;justify-content:center;gap:.42rem;min-height:34px;padding:.42rem .58rem;border-radius:10px;color:#fff!important;font-size:.76rem;font-weight:800;line-height:1.15;text-align:center;box-shadow:0 3px 10px rgba(28,36,46,.16)}} .header-action-book{{width:164px;background:linear-gradient(135deg,#e85d2a,#c83e22)}} .header-action-visit{{width:210px;background:linear-gradient(135deg,#168b86,#0b6664)}}
    .header-controls{{position:fixed;right:10px;top:13%;transform:translateY(-50%);display:flex;flex-direction:column;gap:10px;z-index:1001;padding:8px;border-radius:999px;background:var(--green);box-shadow:0 6px 16px rgba(0,0,0,.12)}} .ctrl-btn,.hamburger{{display:flex;align-items:center;justify-content:center;width:36px;height:36px;padding:0;border:0;border-radius:50%;background:transparent;color:#fff}} .ctrl-btn.active{{background:rgba(255,255,255,.22)}} .hamburger{{display:none;flex-direction:column;gap:5px}} .hamburger span{{display:block;width:20px;height:2px;background:currentColor;transition:.18s}} .hamburger.open span:nth-child(1){{transform:translateY(7px) rotate(45deg)}} .hamburger.open span:nth-child(2){{opacity:0}} .hamburger.open span:nth-child(3){{transform:translateY(-7px) rotate(-45deg)}}
    .mobile-nav{{position:fixed;inset:0;background:var(--paper);z-index:999;display:flex;flex-direction:column;padding:calc(var(--header-h) + 1.5rem) 1.5rem;gap:.5rem;overflow-y:auto;transform:translateX(100%);transition:transform .3s}} .mobile-nav.open{{transform:translateX(0)}} .mobile-nav-heading{{color:var(--green);font-weight:700}} .mobile-nav a{{display:block;padding:.75rem 1rem;border-radius:8px;color:var(--ink);font-size:var(--text-lg)}}
    main{{max-width:960px;margin:0 auto;padding:calc(var(--header-h) + 125px) 20px 0}} .topic-card,.topic-article{{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:clamp(24px,4vw,46px);box-shadow:0 8px 28px rgba(22,75,55,.07)}}
    h1{{font-size:clamp(1.65rem,4vw,2.45rem);line-height:1.35;margin-top:0}} h2{{margin-top:2em;border-left:5px solid var(--green);padding-left:.7em}}
    img{{max-width:100%;height:auto;border-radius:12px}} .topic-list{{display:grid;gap:18px}} .topic-item{{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:24px;text-decoration:none;color:inherit;box-shadow:0 5px 18px rgba(22,75,55,.045);transition:.2s ease}}
    .topic-item:hover{{border-color:var(--green);transform:translateY(-2px)}} .topic-item h2{{margin:.3em 0;border:0;padding:0;font-size:1.25rem}}
    .topic-meta{{color:var(--muted);font-size:.92rem}} .topic-summary{{margin:.5em 0 0}} .topic-back{{display:inline-block;margin-bottom:18px}}
    .topic-categories{{display:flex;gap:8px;flex-wrap:wrap;margin:.65em 0}} .topic-category{{display:inline-block;border-radius:999px;padding:.25em .8em;background:#e5f0eb;color:var(--green);font-weight:700;font-size:.88rem;text-decoration:none}}
    .topic-tags{{display:flex;gap:7px;flex-wrap:wrap;margin:.55em 0}} .topic-tag{{display:inline-block;border-radius:6px;padding:.18em .55em;background:var(--soft);color:var(--muted);font-size:.82rem;text-decoration:none}} .topic-tag::before{{content:"#"}}
    .topic-filters{{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}} .topic-filter{{border:1px solid var(--green);border-radius:999px;padding:8px 14px;background:var(--paper);color:var(--green);font:inherit;font-weight:700;cursor:pointer}} .topic-filter[aria-pressed="true"]{{background:var(--green);color:#fff}}
    .topic-footer{{margin-top:56px;background:#173e33;color:#fff}} .topic-footer-inner{{max-width:1120px;margin:auto;padding:34px 20px;display:grid;grid-template-columns:1.2fr 1fr;gap:24px}} .topic-footer a{{color:#fff}} .topic-footer-title{{font-weight:800;font-size:1.05rem}} .topic-footer-links{{display:flex;gap:10px 18px;flex-wrap:wrap;align-content:start}} .topic-copyright{{grid-column:1/-1;border-top:1px solid #ffffff35;padding-top:14px;font-size:.78rem;color:#dce9e2}}
    @media(max-width:1099px) and (min-width:768px){{.header-quick-actions-desktop .header-action{{width:auto;font-size:.68rem}}.header-quick-actions-desktop{{padding-right:45px}}}}
    @media(max-width:767px){{:root{{--header-h:96px}}.site-header .header-inner{{display:grid;grid-template-columns:82px minmax(0,1fr);grid-template-areas:'logo intro' 'actions actions';align-items:start;gap:5px 10px;padding:7px 10px 0}}.header-left{{grid-area:logo;display:flex;flex-direction:column;align-items:center}}.logo-img{{width:72px;height:72px}}.mobile-logo-name{{display:block;margin-top:1px;font-family:var(--font-display);font-size:.66rem;font-weight:700;line-height:1.25;text-align:center}}.header-right{{grid-area:intro;align-self:center;padding-right:48px}}.logo-text{{display:none}}.logo-text-wrap{{display:block}}.logo-sub{{display:block;margin:0;font-size:.76rem;line-height:1.55}}.main-nav{{display:none}}.header-quick-actions-desktop{{display:none}}.header-quick-actions-mobile{{grid-area:actions;display:grid;grid-template-columns:1fr 1fr;width:100%;padding:4px 48px 8px 0}}.header-quick-actions-mobile .header-action{{width:auto;font-size:.78rem}}.header-controls{{right:8px;top:10%;gap:6px;padding:4px}}.header-controls .ctrl-btn,.hamburger{{width:32px;height:32px}}.hamburger{{display:flex}}main{{padding:calc(var(--header-h) + 80px) 14px 0}}.topic-footer-inner{{grid-template-columns:1fr}}.topic-copyright{{grid-column:auto}}}}
  </style>
</head>
<body>
<header class="site-header" role="banner"><div class="header-inner"><div class="header-left"><a href="/" class="logo" aria-label="くろまめはりきゅう院 トップページ"><img src="/images/logo/osumasi.png" alt="くろまめはりきゅう院ロゴ" class="logo-img" width="128" height="128"></a><span class="mobile-logo-name">くろまめはりきゅう院</span></div><div class="header-right"><div class="logo-text-wrap"><span class="logo-text">くろまめはりきゅう院</span><span class="logo-sub">昔ながらの接骨院ぽい治療院から、訪問マッサージもあります</span></div><nav class="main-nav"><div class="nav-row"><div class="primary-nav-links"><a href="/">台町店</a><a href="/visit.html">訪問マッサージ</a><a href="/acupuncture.html">はりきゅう</a><a href="/shop.html">健康グッズ</a><a href="/column.html" class="active" aria-current="page">健康コラム</a></div><div class="header-quick-actions header-quick-actions-desktop" aria-label="予約・お問い合わせ"><a class="header-action header-action-book" href="https://script.google.com/macros/s/AKfycbzxj8ITX23qJl1l47Oz4WEmYuvHqCZ6e7rmhiN1S73aSaMsIkGbous3P3MDijdkSaQI/exec" target="_blank" rel="noopener noreferrer">📅 台町店予約</a><a class="header-action header-action-visit" href="/visit.html#apply">✉ 訪問マッサージお問い合わせ</a></div></div></nav></div><div class="header-quick-actions header-quick-actions-mobile" aria-label="予約・お問い合わせ"><a class="header-action header-action-book" href="https://script.google.com/macros/s/AKfycbzxj8ITX23qJl1l47Oz4WEmYuvHqCZ6e7rmhiN1S73aSaMsIkGbous3P3MDijdkSaQI/exec" target="_blank" rel="noopener noreferrer">📅 台町店予約</a><a class="header-action header-action-visit" href="/visit.html#apply">✉ 訪問マッサージお問い合わせ</a></div><div class="header-controls"><button class="hamburger" id="hamburger-btn" aria-label="メニューを開く" aria-expanded="false" aria-controls="mobile-nav"><span></span><span></span><span></span></button><button class="ctrl-btn" id="theme-toggle" aria-label="ダークモードに切り替え" title="ダーク／ライトモード切替">◐</button><button class="ctrl-btn" id="vision-toggle" aria-label="弱視者用ハイコントラストモード切替" title="弱視対応モード">◉</button><button class="ctrl-btn" id="font-toggle" aria-label="文字サイズ切替" title="文字サイズ切替"><span class="ctrl-btn-label">Aa</span></button></div></div></header>
<nav class="mobile-nav" id="mobile-nav" aria-label="モバイルナビゲーション" aria-hidden="true"><p class="mobile-nav-heading">サイトメニュー</p><a href="/">› 台町店</a><a href="/visit.html">› 訪問マッサージ</a><a href="/acupuncture.html">› はりきゅう</a><a href="/shop.html">› 健康グッズ</a><a href="/column.html" class="active" aria-current="page">› 健康コラム</a></nav>
<main id="main-content">{body}</main>
<footer class="topic-footer"><div class="topic-footer-inner"><div><a class="topic-footer-title" href="/">くろまめ鍼灸マッサージ院</a><p>埼玉県本庄市台町の鍼灸・マッサージ院です。訪問マッサージにも対応しています。</p></div><nav class="topic-footer-links" aria-label="フッターメニュー"><a href="/">台町店</a><a href="/visit.html">訪問マッサージ</a><a href="/acupuncture.html">はりきゅう</a><a href="/shop.html">健康グッズ</a><a href="/column.html">健康コラム</a></nav><small class="topic-copyright">© くろまめ鍼灸マッサージ院</small></div></footer>
<script>(function(){{var html=document.documentElement;var theme=localStorage.getItem('km-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');var visionOn=localStorage.getItem('km-vision')==='1';var fontStep=Number(localStorage.getItem('km-fontstep')||0);var fontSizes=[null,'large','xlarge'];html.setAttribute('data-theme',theme);if(visionOn)html.setAttribute('data-vision','');if(fontSizes[fontStep])html.setAttribute('data-fontsize',fontSizes[fontStep]);document.getElementById('theme-toggle').addEventListener('click',function(){{theme=theme==='dark'?'light':'dark';html.setAttribute('data-theme',theme);localStorage.setItem('km-theme',theme);this.classList.toggle('active',theme==='dark');}});document.getElementById('vision-toggle').addEventListener('click',function(){{visionOn=!visionOn;if(visionOn)html.setAttribute('data-vision','');else html.removeAttribute('data-vision');this.classList.toggle('active',visionOn);localStorage.setItem('km-vision',visionOn?'1':'0');}});document.getElementById('font-toggle').addEventListener('click',function(){{fontStep=(fontStep+1)%fontSizes.length;html.removeAttribute('data-fontsize');if(fontSizes[fontStep])html.setAttribute('data-fontsize',fontSizes[fontStep]);localStorage.setItem('km-fontstep',String(fontStep));}});var hamburger=document.getElementById('hamburger-btn'),mobileNav=document.getElementById('mobile-nav'),isOpen=false;hamburger.addEventListener('click',function(){{isOpen=!isOpen;hamburger.classList.toggle('open',isOpen);mobileNav.classList.toggle('open',isOpen);mobileNav.setAttribute('aria-hidden',String(!isOpen));hamburger.setAttribute('aria-expanded',String(isOpen));}});document.querySelectorAll('.mobile-nav a').forEach(function(a){{a.addEventListener('click',function(){{isOpen=false;hamburger.classList.remove('open');mobileNav.classList.remove('open');mobileNav.setAttribute('aria-hidden','true');hamburger.setAttribute('aria-expanded','false');}});}});}})();</script>
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
