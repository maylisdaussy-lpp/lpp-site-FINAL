#!/usr/bin/env python3
"""Génère les articles HTML LPP à partir des sources markdown.

Usage : python3 build.py <template.html> <src_dir> <out_dir>
Produit <out_dir>/_a-publier/<slug>/index.html et <out_dir>/_a-publier/calendrier.json
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

import markdown

SITE = "https://lespetitspapierspeints.com"
AUTHOR = "Maylis Daussy"

PRO_LABELS = {
    "E": ("Une entreprise", "Décrire mon projet →"),
    "C": ("Un CSE", "Préparer mon événement CSE →"),
    "K": ("Une collectivité", "Demander un devis pour ma commune →"),
    "S": ("Une école ou une crèche", "Monter le projet de mon établissement →"),
    "H": ("Un établissement de santé ou un EHPAD", "Recevoir la fiche technique M1 →"),
    "A": ("Une agence événementielle", "Proposer un partenariat →"),
    "G": ("Une gare, un aéroport, un lieu d'accueil du public", "Étudier mon espace familles →"),
}

TAG_STYLES = {
    "CSE": "color:#c0254f;background:#fde8ef",
    "Particuliers": "color:#c0254f;background:#fde8ef",
}


def parse_source(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise ValueError(f"front matter manquant : {path}")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, m.group(2)


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:48].rstrip("-")


def short_label(s, n=38):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"^(L'idée|Le principe)\s*:\s*", "", s)
    s = s[:1].upper() + s[1:]
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:") + "…"


def split_faq(body):
    """Retire la section FAQ et la renvoie sous forme de liste (q, a)."""
    m = re.search(r"\n## Questions fréquentes\n(.*?)(?=\n## |\Z)", body, re.S)
    if not m:
        return body, []
    faq_md = m.group(1)
    items = re.findall(r"Q:\s*(.+?)\nA:\s*(.+?)(?=\n\s*\nQ:|\n*\Z)", faq_md.strip() + "\n", re.S)
    body = body[: m.start()] + body[m.end():]
    return body, [(q.strip(), a.strip()) for q, a in items]


def split_sources(body):
    m = re.search(r"\n## Sources\n(.*?)(?=\n## |\Z)", body, re.S)
    if not m:
        return body, ""
    return body[: m.start()] + body[m.end():], m.group(1).strip()


def md(s):
    return markdown.markdown(s, extensions=["tables"], output_format="html5")


def inline_md(s):
    out = md(s)
    return re.sub(r"^<p>(.*)</p>$", r"\1", out.strip(), flags=re.S)


def word_count(*parts):
    text = " ".join(re.sub(r"<[^>]+>", " ", p) for p in parts)
    return len(re.findall(r"\w+", text))


def build_article(meta, body, template, all_meta):
    body, faq = split_faq(body)
    body, sources_md = split_sources(body)

    content_html = md(body.strip())

    # Ancres sur les H2 + sommaire
    toc = []
    used = set()

    def h2_sub(m):
        inner = m.group(1)
        hid = slugify(re.sub(r"<[^>]+>", "", inner))
        base, i = hid, 2
        while hid in used:
            hid = f"{base}-{i}"
            i += 1
        used.add(hid)
        toc.append((hid, short_label(inner)))
        return f'<h2 id="{hid}">{inner}</h2>'

    content_html = re.sub(r"<h2>(.*?)</h2>", h2_sub, content_html)

    # Image secondaire après le N-ième H2
    if meta.get("img2"):
        n = int(meta.get("img2_after", "2"))
        parts = re.split(r"(?=<h2 id=)", content_html)
        if len(parts) > n:
            img = (f'<img src="{meta["img2"]}" alt="{html.escape(meta["img2_alt"], quote=True)}" '
                   f'class="article-img" loading="lazy">\n')
            # après le premier paragraphe de la section n
            sec = parts[n]
            sec = re.sub(r"(</p>)", r"\1\n" + img.replace("\\", "\\\\"), sec, count=1)
            parts[n] = sec
            content_html = "".join(parts)

    # Encart CTA après l'introduction (avant le premier H2)
    enc = meta["encart"].split("||")
    enc_text, enc_btn = enc[0], enc[1]
    enc_html = (f'<div class="cta-inline-article"><p>{html.escape(enc_text)}')
    if len(enc) >= 4:
        enc_html += (f' <a href="{enc[3]}" style="color:#fff;border-bottom:1px solid rgba(255,255,255,.6)">'
                     f'{html.escape(enc[2])}</a>')
    if meta["audience"] == "pro":
        enc_html += f'</p><a href="/contact/" class="btn-white-sm" style="color:#EB356F;border-bottom:0">{html.escape(enc_btn)}</a></div>'
    else:
        enc_html += f'</p><a href="/particuliers/" class="btn-white-sm" style="color:#EB356F;border-bottom:0">{html.escape(enc_btn)}</a></div>'
    content_html = content_html.replace('<h2 id=', enc_html + "\n<h2 id=", 1)

    # Bloc « Vous êtes… »
    if meta["audience"] == "pro":
        items = []
        for idx, code in enumerate(meta["order"].split(",")):
            who, label = PRO_LABELS[code.strip()]
            if idx == 0 and meta.get("first_label"):
                label = meta["first_label"]
            if idx == 0 and meta.get("first_who"):
                who = meta["first_who"]
            items.append(f'<li><strong>{html.escape(who)}</strong> : <a href="/contact/">{html.escape(label)}</a></li>')
        vous = ('<h2 id="vous-etes">Vous êtes…</h2>\n<ul>\n' + "\n".join(items) + "\n</ul>\n"
                '<p>Pas encore de projet précis ? <a href="/nos-supports/">Découvrez nos supports</a> '
                'ou <a href="/inspirez-vous/">inspirez-vous de nos réalisations</a>.</p>')
    else:
        vous = ('<h2 id="pour-aller-plus-loin">Pour la maison</h2>\n'
                '<p>Nos décorations à colorier existent aussi pour les chambres et les salons. '
                '<a href="/particuliers/">Découvrir nos modèles pour les particuliers</a>.</p>')

    faq_html = ""
    if faq:
        faq_html = ('<div class="faq-section"><h2 id="questions-frequentes">Questions fréquentes</h2>'
                    + "".join(f'<details class="faq-item"><summary class="faq-q">{html.escape(q)}</summary>'
                              f'<p class="faq-a">{inline_md(a)}</p></details>' for q, a in faq)
                    + "</div>")

    sources_html = ""
    if sources_md:
        src = md(sources_md).replace("<a href=", '<a target="_blank" rel="noopener" href=')
        sources_html = '<h2 id="sources">Sources</h2>\n' + src

    final_href = "/contact/" if meta["audience"] == "pro" else "/particuliers/"
    final_btn = "Discuter de mon projet" if meta["audience"] == "pro" else "Voir les modèles"
    final_cta = (f'<div class="cta-inline-article"><p>{html.escape(meta["final_cta"])}</p>'
                 f'<a href="{final_href}" class="btn-white-sm" style="color:#EB356F;border-bottom:0">{final_btn}</a></div>')

    article_html = "\n".join([content_html, vous, faq_html, final_cta, sources_html])

    words = word_count(meta["intro"], content_html, faq_html)
    minutes = max(4, round(words / 220))

    # Sidebar
    toc_html = "".join(f'<li><a href="#{a}">{html.escape(l)}</a></li>' for a, l in toc[:7])
    rel = meta["related"].split("|")
    rel_pairs = list(zip(rel[0::2], rel[1::2]))
    rel_html = "".join(f'<li><a href="/{s}/">{html.escape(l)}</a></li>' for s, l in rel_pairs)
    if meta["audience"] == "pro":
        side_cta = ('<div class="sidebar-cta"><p>Décorations murales géantes à colorier, personnalisées et fabriquées en France.</p>'
                    '<a href="/contact/" class="btn-pink">Demander un devis</a></div>')
    else:
        side_cta = ('<div class="sidebar-cta"><p>Des murs à colorier pour la chambre, fabriqués en France sur papier recyclé.</p>'
                    '<a href="/particuliers/" class="btn-pink">Voir les modèles</a></div>')
    sidebar = ('<aside class="article-sidebar">\n'
               f'      <div class="sidebar-card"><h3>Dans cet article</h3><ul class="toc-list">{toc_html}</ul></div>\n'
               f'      <div class="sidebar-card"><h3>Articles similaires</h3><ul class="related-articles">{rel_html}</ul></div>\n'
               f'      {side_cta}\n'
               '    </aside>')

    tag = meta["tag"]
    tag_style = TAG_STYLES.get(tag, "color:#1a7fa3;background:#e8f8fd")
    hero = f'''<div class="article-hero">
    <div class="article-hero-inner">
      <nav class="article-breadcrumb"><a href="/">Accueil</a><span>/</span><a href="/blog/">Blog</a><span>/</span><span>{html.escape(tag)}</span></nav>
      <span class="article-tag" style="{tag_style}">{html.escape(tag)}</span>
      <h1 class="article-title">{html.escape(meta["title"])}</h1>
      <p class="article-intro">{html.escape(meta["intro"])}</p>
      <div class="article-meta"><span>Par {AUTHOR}, Les Petits Papiers</span><span>·</span><span>Lecture {minutes} min</span></div>
    </div>
    <img src="{meta["hero"]}" alt="{html.escape(meta["hero_alt"], quote=True)}" class="article-hero-img">
  </div>
  <div class="article-layout">
    <article class="article-content">
{article_html}
    </article>
    {sidebar}
  </div>'''

    # Remplacement dans le gabarit
    out = template
    url = f"{SITE}/{meta['slug']}/"
    full_title = f'{meta["seo_title"]} - Les Petits Papiers'
    esc = lambda s: html.escape(s, quote=True)
    out = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(meta["meta"])}">', out, count=1)
    out = re.sub(r"<title>.*?</title>", f"<title>{esc(full_title)}</title>", out, count=1, flags=re.S)
    out = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', out, count=1)
    out = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(full_title)}">', out, count=1)
    out = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(meta["meta"])}">', out, count=1)
    out = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{SITE}{meta["hero"]}">', out, count=1)
    out = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', out, count=1)

    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
        "description": meta["meta"], "image": f"{SITE}{meta['hero']}",
        "datePublished": meta["date"], "dateModified": meta["date"],
        "mainEntityOfPage": url,
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Organization", "name": "Les Petits Papiers", "url": SITE},
    }]
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", inline_md(a))}}
            for q, a in faq]})
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    out = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: ld_html, out, count=1, flags=re.S)

    start = out.index('<div class="article-hero">')
    end = out.index("<footer>")
    out = out[:start] + hero + "\n\n  " + out[end:]
    return out, words


def card(meta, all_slugs=None):
    return {
        "slug": meta["slug"], "date": meta["date"], "title": meta["title"],
        "excerpt": meta["meta"], "tag": meta["tag"], "image": meta["hero"],
        "image_alt": meta["hero_alt"],
    }


def main():
    template = Path(sys.argv[1]).read_text(encoding="utf-8")
    src_dir, out_dir = Path(sys.argv[2]), Path(sys.argv[3])
    sources = sorted(src_dir.glob("*.md"))
    metas = [parse_source(p) for p in sources]
    all_meta = {m["slug"]: m for m, _ in metas}
    cal = []
    report = []
    for (meta, body), p in zip(metas, sources):
        page, words = build_article(meta, body, template, all_meta)
        dest = out_dir / "_a-publier" / meta["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        cal.append(card(meta))
        report.append((p.name, meta["slug"], meta["date"], words))
    cal.sort(key=lambda c: c["date"])
    (out_dir / "_a-publier" / "calendrier.json").write_text(
        json.dumps(cal, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in report:
        print(*r)


if __name__ == "__main__":
    main()
