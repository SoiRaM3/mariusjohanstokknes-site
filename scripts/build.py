#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from html import escape
import json
import datetime

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config/site.json").read_text(encoding="utf-8"))
BOOKS = json.loads((ROOT / "content/books.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
FRAGMENTS = json.loads((ROOT / "content/fragments.json").read_text(encoding="utf-8"))

GENERATED_PAGES = [
    "index.html", "books.html", "fiction.html", "fragments.html", "framework.html",
    "notes.html", "about.html", "contact.html", "start-here.html", "privacy.html", "404.html"
]

def e(value: object) -> str:
    return escape(str(value or ""), quote=True)

def search_data() -> list[dict]:
    data = []
    for title, url, text in [
        ("Home", "index.html", CONFIG["description"]),
        ("Books", "books.html", "Complete catalogue and current releases."),
        ("Fiction", "fiction.html", "Dystopian, psychological and bureaucratic fiction."),
        ("Fragments", "fragments.html", "Selected lines and source-attributed fragments."),
        ("Framework", "framework.html", "The Stokknes Chaos Framework."),
        ("Notes", "notes.html", "Irregular publishing updates."),
        ("About Stokknes", "about.html", "Short author biography."),
        ("Contact", "contact.html", "Public channels, press and review copies."),
        ("Start Here", "start-here.html", "Reader paths through the books."),
    ]:
        data.append({"title": title, "url": url, "text": text, "type": "Page"})
    for book in BOOKS:
        data.append({
            "title": book["title"],
            "url": f'books.html#{book["slug"]}',
            "text": book["short"],
            "type": book["type"],
        })
    return data

def header(current: str) -> str:
    nav = "\n".join(
        f'<a class="{"active" if current == href else ""}" href="{e(href)}">{e(label)}</a>'
        for label, href in CONFIG["navigation"]
    )
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="index.html">M. J. STOKKNES<span class="brand-dot">.</span></a>
    <nav class="primary-nav" data-primary-nav aria-label="Primary navigation">{nav}</nav>
    <div class="header-actions">
      <button class="icon-btn" type="button" aria-label="Search" aria-expanded="false" data-search-button>⌕</button>
      <a class="icon-btn" href="books.html" aria-label="Books">◫</a>
      <button class="icon-btn menu-btn" type="button" aria-label="Menu" aria-expanded="false" data-menu-button>☰</button>
    </div>
  </div>
</header>
<div class="search-panel" data-search-panel>
  <div class="search-inner">
    <input type="search" placeholder="Search books, fiction, fragments…" aria-label="Search site" data-search-input>
    <div class="search-results" data-search-results></div>
  </div>
</div>
"""

def footer() -> str:
    links = [
        ("Review copies", "contact.html"),
        ("Press", "contact.html"),
        ("Amazon author page", CONFIG["amazon"]),
        ("Goodreads", CONFIG["goodreads"]),
        ("GitHub", CONFIG["github_repo"]),
    ]
    link_html = "".join(
        f'<a href="{e(url)}"{" target=\"_blank\" rel=\"noreferrer\"" if url.startswith("http") else ""}>{e(label)}</a>'
        for label, url in links if url
    )
    return f"""
<footer class="site-footer">
  <div class="footer-inner">
    <span>© {e(CONFIG["copyright_year"])} M. J. STOKKNES. ALL RIGHTS RESERVED.</span>
    <div class="footer-links">{link_html}<a href="#top" aria-label="Back to top">↑</a></div>
  </div>
</footer>
<script>window.STOKKNES_SEARCH={json.dumps(search_data(), ensure_ascii=False)};</script>
<script src="assets/js/site.js"></script>
"""

def document(title: str, current: str, body: str, description: str = "") -> str:
    full_title = f"{title} | {CONFIG['site_name']}" if title != CONFIG["site_name"] else title
    desc = description or CONFIG["description"]
    canonical = CONFIG["domain"].rstrip("/") + "/" + ("" if current == "index.html" else current)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#070806">
  <title>{e(full_title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{e(canonical)}">
  <meta property="og:title" content="{e(full_title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{e(canonical)}">
  <meta property="og:image" content="{e(CONFIG['domain'].rstrip('/') + '/assets/images/editorial/hero.jpg')}">
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">
  <link rel="stylesheet" href="assets/css/site.css">
</head>
<body id="top">
{header(current)}
<main id="main">{body}</main>
{footer()}
</body>
</html>
"""

def book_cover(book: dict) -> str:
    return f'<div class="book-cover"><img src="{e(book["image"])}" alt="Cover of {e(book["title"])}" loading="lazy"></div>'

def homepage() -> str:
    upcoming = [b for b in BOOKS if b.get("featured") == "upcoming"]
    latest = [b for b in BOOKS if b.get("featured") == "latest"]
    upcoming_html = "".join(f"""
      <article class="feature-book">
        {book_cover(book)}
        <div>
          <h3>{e(book["title"])}</h3>
          <div class="type">{e(book["type"])}</div>
          <p>{e(book["short"])}</p>
          <div class="meta-line">{e(book["status"])} · {e(book["release"])}</div>
          <a class="small-button" href="fiction.html">View page</a>
        </div>
      </article>""" for book in upcoming)
    latest_html = "".join(f"""
      <article class="latest-card">
        {book_cover(book)}
        <h3>{e(book["title"])}</h3>
        <div class="type">{e(book["subtitle"] or book["type"])}</div>
        <p>{e(book["price"])}</p>
        <a class="small-button" href="{e(book["buy"] or "books.html")}"{" target=\"_blank\" rel=\"noreferrer\"" if book["buy"] else ""}>View</a>
      </article>""" for book in latest)
    cats = [
        ("Chaos & You<br>Series", "books.html", "category-chaos.jpg"),
        ("Standalone<br>Nonfiction", "books.html", "category-nonfiction.jpg"),
        ("Fiction", "fiction.html", "category-fiction.jpg"),
        ("Fragments<br>& Notes", "fragments.html", "category-fragments.jpg"),
        ("Framework<br>& Compendium", "framework.html", "category-framework.jpg"),
        ("Archive<br>Earlier Work", "books.html", "category-archive.jpg"),
    ]
    cats_html = "".join(f"""
      <a class="category-card" href="{href}">
        <img src="assets/images/categories/{img}" alt="" loading="lazy">
        <span>{label}</span>
      </a>""" for label, href, img in cats)
    return f"""
<section class="hero">
  <div class="hero-inner">
    <div class="hero-copy">
      <h1>M. J. STOKKNES</h1>
      <div class="rule"></div>
      <p class="hero-lede">{e(CONFIG["tagline"])}</p>
      <div class="button-row">
        <a class="button primary" href="start-here.html">Start here</a>
        <a class="button" href="books.html">Browse books</a>
      </div>
      <blockquote class="hero-quote">We do not live in a world of lies.<br>We live in a world of agreements<br>no one has read.<cite>— M. J. Stokknes</cite></blockquote>
    </div>
  </div>
</section>

<section class="section">
  <div class="release-grid">
    <div class="release-block">
      <h2 class="section-title">Upcoming releases</h2>
      <div class="upcoming-grid">{upcoming_html}</div>
    </div>
    <div class="release-block">
      <h2 class="section-title">Latest releases</h2>
      <div class="latest-grid">{latest_html}</div>
    </div>
  </div>
  <div class="view-all-wrap"><a class="button" href="books.html">View all books →</a></div>
</section>

<section class="section">
  <h2 class="section-title">Browse by category</h2>
  <div class="category-grid">{cats_html}</div>
</section>

<section class="start-strip">
  <div class="start-inner">
    <h2 class="section-title">Start here</h2>
    <div class="path-grid">
      <article class="path"><h3>New here?</h3><p>Begin with accessible reads that introduce the ideas and the voice.</p><a href="start-here.html">Recommended start →</a></article>
      <article class="path"><h3>Deeper dive?</h3><p>Explore the Chaos & You series and the philosophy.</p><a href="books.html">Explore series →</a></article>
      <article class="path"><h3>Fiction reader?</h3><p>Dark, psychological, dystopian stories set in real places.</p><a href="fiction.html">Browse fiction →</a></article>
    </div>
  </div>
</section>

<section class="lower-band">
  <div class="lower-grid">
    <div class="lower-cell">
      <h3>Notes from the road</h3>
      <p>Thoughts, updates, new books.<br>Sent irregularly. No spam.</p>
      <form class="newsletter" data-newsletter-form>
        <input type="email" placeholder="Your email" aria-label="Email address" required>
        <button type="submit">Subscribe</button>
      </form>
      <p data-form-note style="margin-top:8px"></p>
    </div>
    <div class="lower-cell quote-cell">Nothing is more dangerous<br>than a man who has read<br>nothing and believes everything.<br>— M. J. Stokknes</div>
    <div class="lower-cell">
      <h3>Connect</h3>
      <div class="social-links">
        <a href="{e(CONFIG['goodreads'])}" target="_blank" rel="noreferrer" aria-label="Goodreads">g</a>
        <a href="{e(CONFIG['github_profile'])}" target="_blank" rel="noreferrer" aria-label="GitHub">⌘</a>
        <a href="{e(CONFIG['amazon'])}" target="_blank" rel="noreferrer" aria-label="Amazon">a</a>
        <a href="contact.html" aria-label="Contact">✉</a>
      </div>
    </div>
  </div>
</section>
"""

def page_hero(page: dict) -> str:
    return f"""
<section class="page-hero">
  <div class="page-hero-inner">
    <span class="kicker">{e(page['kicker'])}</span>
    <h1>{e(page['title'])}</h1>
    <p>{e(page['intro'])}</p>
  </div>
</section>"""

def standard_page(key: str, current: str) -> str:
    page = PAGES[key]
    sections = "".join(f"""
      <section class="prose-section">
        <h2>{e(title)}</h2>
        <p>{e(text)}</p>
      </section>""" for title, text in page["sections"])
    body = page_hero(page) + f'<div class="page-content"><div class="prose-sections">{sections}</div></div>'
    return document(page["title"], current, body, page["intro"])

def books_page() -> str:
    cards = []
    for book in BOOKS:
        group = "fiction" if "novella" in book["type"].lower() or "noir" in book["type"].lower() else "chaos"
        actions = f'<a class="small-button" href="#{e(book["slug"])}">Details</a>'
        if book["buy"]:
            actions += f'<a class="small-button" href="{e(book["buy"])}" target="_blank" rel="noreferrer">Buy</a>'
        cards.append(f"""
        <article class="book-card" id="{e(book['slug'])}" data-book-card data-group="{group}">
          {book_cover(book)}
          <div class="book-type">{e(book['type'])} · {e(book['status'])}</div>
          <h3>{e(book['title'])}</h3>
          <p>{e(book['long'])}</p>
          <div class="card-actions">{actions}</div>
        </article>""")
    body = """
<section class="page-hero"><div class="page-hero-inner">
  <span class="kicker">CATALOGUE</span><h1>Books</h1>
  <p>Philosophy, independent nonfiction, and fiction. The books are the clearest introduction.</p>
</div></section>
<div class="page-content">
  <div class="catalogue-head">
    <h2>Current catalogue</h2>
    <div class="filters">
      <button class="filter-btn active" data-filter="all">All</button>
      <button class="filter-btn" data-filter="chaos">Chaos & You</button>
      <button class="filter-btn" data-filter="fiction">Fiction</button>
    </div>
  </div>
  <div class="book-grid">""" + "".join(cards) + "</div></div>"
    return document("Books", "books.html", body, "Books by M. J. Stokknes.")

def fiction_page() -> str:
    page = PAGES["fiction"]
    cards = "".join(f"""
      <article class="fiction-card"><span class="kicker">IN DEVELOPMENT</span><h2>{e(title)}</h2><p>{e(text)}</p></article>
    """ for title, text in page["sections"])
    body = page_hero(page) + f'<div class="page-content"><div class="fiction-grid">{cards}</div></div>'
    return document(page["title"], "fiction.html", body, page["intro"])

def fragments_page() -> str:
    cards = "".join(f"""
      <article class="fragment-card"><blockquote>“{e(item['text'])}”</blockquote><cite>{e(item['source'])}</cite></article>
    """ for item in FRAGMENTS)
    body = """
<section class="page-hero"><div class="page-hero-inner">
  <span class="kicker">SELECTED LINES</span><h1>Fragments</h1>
  <p>Condensed pieces from the books, notes, and the framework. A sentence is not a system, but it can still leave damage.</p>
</div></section>
<div class="page-content"><div class="fragment-grid">""" + cards + "</div></div>"
    return document("Fragments", "fragments.html", body, "Selected fragments from M. J. Stokknes.")

def start_here_page() -> str:
    paths = [
        ("Information and overload", "Information → Reality → Time", "Begin where the signal has already exceeded the nervous system."),
        ("Identity and intimacy", "Identity → Love → Reality", "Begin with the version of yourself assembled under pressure."),
        ("Power and civilization", "Power → Civilization → Information", "Begin with the cage that does not look like one."),
        ("Entropy", "Entropy → Civilization → Reality", "Begin with maintenance, exhaustion, and what cannot remain stable."),
        ("Philosophy", "Philosophy → Reality → Identity", "Begin with the answer that consumed its own question."),
        ("Fiction", "Terms and Conditions → The Violence Was Random → Synapse", "Begin with a story. The machinery will introduce itself."),
    ]
    cards = "".join(
        f'<article class="fiction-card"><span class="kicker">{e(seq)}</span><h2>{e(title)}</h2><p>{e(text)}</p></article>'
        for title, seq, text in paths
    )
    body = """
<section class="page-hero"><div class="page-hero-inner">
  <span class="kicker">READER PATHS</span><h1>Start Here</h1>
  <p>There are several ways into the work. None require reading everything in order.</p>
</div></section>
<div class="page-content"><div class="fiction-grid">""" + cards + "</div></div>"
    return document("Start Here", "start-here.html", body, "Where to begin with the books of M. J. Stokknes.")

def privacy_page() -> str:
    body = """
<section class="page-hero"><div class="page-hero-inner">
  <span class="kicker">LEGAL</span><h1>Privacy</h1>
  <p>A small static website with no advertising network, no account system, and no reason to collect more than necessary.</p>
</div></section>
<div class="page-content"><div class="prose-sections">
  <section class="prose-section"><h2>Current site</h2><p>This website is delivered as static files. It does not operate user accounts or a private database.</p></section>
  <section class="prose-section"><h2>Newsletter</h2><p>The visible newsletter form is not connected to a provider yet and does not submit addresses.</p></section>
  <section class="prose-section"><h2>External links</h2><p>Amazon, Goodreads, GitHub, and other external services apply their own privacy policies when opened.</p></section>
</div></div>"""
    return document("Privacy", "privacy.html", body, "Privacy information for mariusjohanstokknes.com.")

def not_found_page() -> str:
    body = """
<section class="page-hero"><div class="page-hero-inner">
  <span class="kicker">404</span><h1>The page is missing.</h1>
  <p>Either the link is old, the file moved, or the archive has started editing itself.</p>
  <div class="button-row" style="margin-top:24px"><a class="button primary" href="index.html">Return home</a><a class="button" href="books.html">Browse books</a></div>
</div></section>"""
    return document("Page not found", "404.html", body)

def write(name: str, text: str) -> None:
    (ROOT / name).write_text(text, encoding="utf-8", newline="\n")

write("index.html", document(CONFIG["site_name"], "index.html", homepage(), CONFIG["description"]))
write("books.html", books_page())
write("fiction.html", fiction_page())
write("fragments.html", fragments_page())
write("framework.html", standard_page("framework", "framework.html"))
write("notes.html", standard_page("notes", "notes.html"))
write("about.html", standard_page("about", "about.html"))
write("contact.html", standard_page("contact", "contact.html"))
write("start-here.html", start_here_page())
write("privacy.html", privacy_page())
write("404.html", not_found_page())

urls = [""] + [p for p in GENERATED_PAGES if p not in {"index.html", "404.html"}]
today = datetime.date.today().isoformat()
sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for page in urls:
    loc = CONFIG["domain"].rstrip("/") + "/" + page
    sitemap.append(f"<url><loc>{escape(loc)}</loc><lastmod>{today}</lastmod></url>")
sitemap.append("</urlset>")
write("sitemap.xml", "\n".join(sitemap))
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {CONFIG['domain'].rstrip('/')}/sitemap.xml\n")
print(f"Generated {len(GENERATED_PAGES)} pages.")
