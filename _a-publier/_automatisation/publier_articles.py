#!/usr/bin/env python3
"""Publie les articles programmés de _a-publier/ dont la date est arrivée.

Pour chaque article du calendrier dont la date est passée (heure de Paris) :
  - copie _a-publier/<slug>/index.html vers <slug>/index.html ;
  - ajoute l'URL au sitemap.xml ;
  - ajoute une carte en tête de blog/index.html.
Ensuite, dans tous les articles programmés déjà en ligne :
  - les liens vers un article pas encore publié deviennent du texte simple ;
  - ce texte redevient un lien dès que l'article cible est publié.

Variable d'environnement facultative : LPP_DATE=AAAA-MM-JJ pour simuler une date.
"""
import datetime
import html
import json
import os
import re
import shutil
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "_a-publier"
SITE = "https://lespetitspapierspeints.com"


def today():
    forced = os.environ.get("LPP_DATE")
    if forced:
        return datetime.date.fromisoformat(forced)
    return datetime.datetime.now(ZoneInfo("Europe/Paris")).date()


def is_live(slug):
    return (ROOT / slug / "index.html").exists()


def add_to_sitemap(item):
    path = ROOT / "sitemap.xml"
    s = path.read_text(encoding="utf-8")
    loc = f"{SITE}/{item['slug']}/"
    if f"<loc>{loc}</loc>" in s:
        return
    line = (f"  <url><loc>{loc}</loc><lastmod>{item['date']}</lastmod>"
            f"<priority>0.7</priority><changefreq>monthly</changefreq></url>\n")
    s = s.replace("</urlset>", line + "</urlset>", 1)
    path.write_text(s, encoding="utf-8")


def add_blog_card(item):
    path = ROOT / "blog" / "index.html"
    s = path.read_text(encoding="utf-8")
    if f'href="/{item["slug"]}/"' in s:
        return
    e = lambda t: html.escape(t, quote=True)
    year = item["date"][:4]
    card = f'''
    <div class="post-card">
      <a href="/{item['slug']}/">
        <img src="{item['image']}" alt="{e(item['image_alt'])}" class="post-img" loading="lazy">
        <div class="post-body">
          <div class="post-meta">
            <span class="post-tag">{e(item['tag'])}</span>
            <span class="post-date">{year}</span>
          </div>
          <h2>{e(item['title'])}</h2>
          <p>{e(item['excerpt'])}</p>
          <span class="post-read">Lire l'article →</span>
        </div>
      </a>
    </div>
'''
    marker = '<div class="blog-grid">'
    if marker not in s:
        raise SystemExit("Grille du blog introuvable dans blog/index.html")
    s = s.replace(marker, marker + "\n" + card, 1)
    path.write_text(s, encoding="utf-8")


def refresh_links(calendar):
    """Active ou désactive les liens entre articles programmés selon leur état."""
    live = {c["slug"] for c in calendar if is_live(c["slug"])}
    pending = {c["slug"] for c in calendar} - live
    for slug in live:
        page = ROOT / slug / "index.html"
        s = page.read_text(encoding="utf-8")
        before = s
        for target in pending:
            s = re.sub(rf'<a href="/{re.escape(target)}/">(.*?)</a>',
                       rf'<span data-lpp-attente="{target}">\1</span>', s, flags=re.S)
        for target in live:
            s = re.sub(rf'<span data-lpp-attente="{re.escape(target)}">(.*?)</span>',
                       rf'<a href="/{target}/">\1</a>', s, flags=re.S)
        if s != before:
            page.write_text(s, encoding="utf-8")


def main():
    calendar = json.loads((DRAFTS / "calendrier.json").read_text(encoding="utf-8"))
    day = today()
    published = []
    for item in sorted(calendar, key=lambda c: c["date"]):
        if datetime.date.fromisoformat(item["date"]) > day or is_live(item["slug"]):
            continue
        src = DRAFTS / item["slug"] / "index.html"
        dest = ROOT / item["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        add_to_sitemap(item)
        add_blog_card(item)
        published.append(item["slug"])
    refresh_links(calendar)
    print(f"Date : {day.isoformat()}")
    print("Publiés aujourd'hui : " + (", ".join(published) if published else "aucun"))
    remaining = [c for c in calendar if not is_live(c["slug"])]
    if remaining:
        nxt = min(remaining, key=lambda c: c["date"])
        print(f"Prochain : {nxt['slug']} le {nxt['date']}")


if __name__ == "__main__":
    main()
