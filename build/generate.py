#!/usr/bin/env python3
"""Generate every page of roofinspectiondenver.com.

Run from the repo root:  python3 build/generate.py

Content lives in build/*_data.py, image slots in build/site_images.py,
icons in build/icons/ (Lucide, ISC license). Output: index.html, service
pages, city pages, hub pages, thank-you/privacy/404 and sitemap.xml.
"""
import html
import json
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from services_data import SERVICES  # noqa: E402
from cities_data import CITIES  # noqa: E402
from home_data import HOME_FAQ  # noqa: E402
from site_images import IMAGES, CITY_HEROES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://roofinspectiondenver.com"
PHONE = "(303) 555-0142"
TEL = "+13035550142"
EMAIL = "info@roofinspectiondenver.com"
TODAY = date.today().isoformat()

SVC = {s["slug"]: s for s in SERVICES}
CITY_BY_NAME = {c["name"]: c for c in CITIES}
PAGE_CITIES = [c for c in CITIES if c["name"] != "Denver"]
esc = html.escape

SERVICE_ICONS = {
    "residential-roof-inspection": "house",
    "hail-damage-roof-inspection": "cloud-hail",
    "storm-damage-roof-inspection": "wind",
    "real-estate-roof-inspection": "key-round",
    "roof-certification": "file-badge",
    "insurance-claim-roof-inspection": "clipboard-list",
    "commercial-roof-inspection": "building-2",
    "drone-roof-inspection": "drone",
    "infrared-roof-inspection": "thermometer-sun",
    "annual-roof-maintenance-inspection": "calendar-check",
    "new-roof-warranty-inspection": "hammer",
    "attic-ventilation-inspection": "fan",
}
CORE_SERVICES = ["hail-damage-roof-inspection", "real-estate-roof-inspection", "residential-roof-inspection",
                 "insurance-claim-roof-inspection", "roof-certification", "commercial-roof-inspection"]


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def city_url(c):
    # The homepage targets "roof inspection Denver"; a separate Denver page would compete with it.
    return "/" if c["name"] == "Denver" else f"/{c['slug']}/"


# ---------------------------------------------------------------- primitives

_icon_cache = {}


def icon(name, cls="i"):
    if name not in _icon_cache:
        svg = open(os.path.join(os.path.dirname(__file__), "icons", name + ".svg")).read()
        svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
        svg = re.sub(r"\s+", " ", svg).replace("> <", "><")
        svg = re.sub(r'class="[^"]*"', "", svg).replace('width="24" height="24" ', "")
        _icon_cache[name] = svg
    return _icon_cache[name].replace("<svg ", f'<svg class="{cls}" aria-hidden="true" focusable="false" ', 1)


def stars():
    return '<span class="stars" aria-hidden="true">' + icon("star") * 5 + "</span>"


def img(key, sizes="(max-width: 1024px) 100vw, 50vw", eager=False, alt=None):
    a = IMAGES[key]["alt"] if alt is None else alt
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="/assets/img/{key}-1600.webp" '
            f'srcset="/assets/img/{key}-800.webp 800w, /assets/img/{key}-1600.webp 1600w" sizes="{sizes}" '
            f'width="1600" height="1067" alt="{esc(a)}" {load} decoding="async">')


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# ---------------------------------------------------------------- structured data

def business_node(full=False):
    node = {
        "@type": ["RoofingContractor", "LocalBusiness"],
        "@id": SITE + "/#business",
        "name": "Roof Inspection Denver",
        "url": SITE + "/",
        "telephone": "+1-303-555-0142",
        "email": EMAIL,
        "image": SITE + "/assets/og-image.png",
        "logo": SITE + "/assets/favicon.svg",
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "addressLocality": "Denver", "addressRegion": "CO", "addressCountry": "US"},
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": "370", "bestRating": "5"},
    }
    if full:
        node.update({
            "description": "Roof Inspection Denver provides residential and commercial roof inspections, hail and storm damage assessments, real estate roof inspections, roof certifications, and insurance claim documentation throughout the Denver metro area.",
            "geo": {"@type": "GeoCoordinates", "latitude": 39.7392, "longitude": -104.9903},
            "openingHoursSpecification": [
                {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "18:00"},
                {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "08:00", "closes": "14:00"},
            ],
            "areaServed": [{"@type": "City", "name": f"{c['name']}, CO"} for c in CITIES],
            "hasOfferCatalog": {
                "@type": "OfferCatalog", "name": "Roof Inspection Services",
                "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": f"{SITE}/{s['slug']}/"}} for s in SERVICES],
            },
        })
    return node


def breadcrumbs_ld(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + url} for i, (name, url) in enumerate(trail)]}


def faq_ld(faqs, url):
    return {"@type": "FAQPage", "@id": SITE + url + "#faq", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs]}


# ---------------------------------------------------------------- layout

def head(title, meta, url, graph, preload=None, robots="index, follow, max-image-preview:large"):
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False) if graph else ""
    pre = (f'  <link rel="preload" as="image" href="/assets/img/{preload}-1600.webp" '
           f'imagesrcset="/assets/img/{preload}-800.webp 800w, /assets/img/{preload}-1600.webp 1600w" imagesizes="100vw">\n') if preload else ""
    ld_block = f'  <script type="application/ld+json">\n{ld}\n  </script>\n' if ld else ""
    return f"""<!doctype html>
<html lang="en-US">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(meta)}">
  <link rel="canonical" href="{SITE}{url}">
  <meta name="robots" content="{robots}">
  <meta name="geo.region" content="US-CO">
  <meta name="geo.placename" content="Denver">
  <meta name="theme-color" content="#0c2340">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Roof Inspection Denver">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(meta)}">
  <meta property="og:url" content="{SITE}{url}">
  <meta property="og:image" content="{SITE}/assets/og-image.png">
  <meta property="og:locale" content="en_US">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="/assets/fonts/jakarta.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
{pre}  <link rel="stylesheet" href="/assets/styles.css">
  <script>document.documentElement.classList.add('js')</script>
{ld_block}</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
"""


def brand():
    return """<a class="brand" href="/" aria-label="Roof Inspection Denver home">
        <img src="/assets/favicon.svg" alt="" width="40" height="40">
        <span>Roof Inspection Denver<small>Denver Metro Roof Inspections</small></span>
      </a>"""


def header(home=False):
    pre = "" if home else "/"
    return f"""  <header class="site-header">
    <div class="container">
      {brand()}
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">{icon("menu")}</button>
      <nav class="nav" id="site-nav" aria-label="Main">
        <ul>
          <li><a href="/services/">Inspections</a></li>
          <li><a href="/hail-damage-roof-inspection/">Hail Damage</a></li>
          <li><a href="/real-estate-roof-inspection/">Real Estate</a></li>
          <li><a href="/service-areas/">Service Areas</a></li>
          <li><a href="{pre}#reviews">Reviews</a></li>
          <li><a href="{pre}#faq">FAQ</a></li>
          <li><a class="nav-phone" href="tel:{TEL}">{icon("phone")} {PHONE}</a></li>
          <li><a class="btn btn-primary" href="#book">Book Inspection</a></li>
        </ul>
      </nav>
    </div>
  </header>
"""


def footer():
    svc_links = "\n".join(f'            <li><a href="/{s}/">{esc(SVC[s]["name"])}</a></li>' for s in CORE_SERVICES)
    city_links = "\n".join(f'            <li><a href="{city_url(c)}">Roof Inspection {esc(c["name"])}</a></li>' for c in PAGE_CITIES[:6])
    return f"""
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          {brand()}
          <p>Professional, unbiased roof inspections for homeowners, buyers, sellers, agents and property managers across the greater Denver, Colorado metro area.</p>
          <p style="display:flex;align-items:center;gap:10px">{stars()} <span>4.9 from 370 Google reviews</span></p>
        </div>
        <div>
          <h2>Inspections</h2>
          <ul>
{svc_links}
            <li><a href="/services/">All inspection services →</a></li>
          </ul>
        </div>
        <div>
          <h2>Service Areas</h2>
          <ul>
{city_links}
            <li><a href="/service-areas/">All service areas →</a></li>
          </ul>
        </div>
        <div>
          <h2>Contact</h2>
          <address style="font-style:normal">
            <ul class="contact">
              <li>{icon("map-pin")} <span>Denver, CO — serving the entire metro</span></li>
              <li>{icon("phone")} <a href="tel:{TEL}">{PHONE}</a></li>
              <li>{icon("mail")} <a href="mailto:{EMAIL}">{EMAIL}</a></li>
              <li>{icon("clock")} <span>Mon–Fri 7am–6pm · Sat 8am–2pm</span></li>
            </ul>
          </address>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© <span id="year">2026</span> Roof Inspection Denver · roofinspectiondenver.com</span>
        <span><a href="/privacy.html">Privacy Policy</a> · <a href="/sitemap.xml">Sitemap</a></span>
      </div>
    </div>
  </footer>

  <a class="mobile-call" href="tel:{TEL}">{icon("phone")} Call for a Roof Inspection</a>

  <script>
    (function () {{
      var btn = document.querySelector('.nav-toggle'), nav = document.getElementById('site-nav');
      btn.addEventListener('click', function () {{
        var open = nav.classList.toggle('open');
        btn.setAttribute('aria-expanded', open);
      }});
      nav.addEventListener('click', function (e) {{
        if (e.target.closest('a')) {{ nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }}
      }});
      document.getElementById('year').textContent = new Date().getFullYear();
      var els = document.querySelectorAll('.reveal');
      if (!('IntersectionObserver' in window)) {{ els.forEach(function (el) {{ el.classList.add('in'); }}); return; }}
      var io = new IntersectionObserver(function (entries) {{
        entries.forEach(function (en) {{ if (en.isIntersecting) {{ en.target.classList.add('in'); io.unobserve(en.target); }} }});
      }}, {{ rootMargin: '0px 0px -8% 0px' }});
      els.forEach(function (el) {{ io.observe(el); }});
    }})();
  </script>
</body>
</html>
"""


def breadcrumb_nav(trail):
    parts = [f'<span aria-current="page">{esc(n)}</span>' if i == len(trail) - 1 else f'<a href="{u}">{esc(n)}</a>'
             for i, (n, u) in enumerate(trail)]
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + " &nbsp;/&nbsp; ".join(parts) + "</nav>"


FORM_OPTIONS = ["Hail or storm damage", "Buying / selling a home", "Roof certification", "Insurance claim documentation",
                "Leak or moisture concern", "General roof condition check", "Commercial / multi-family"]


def form_card(default_type=None, city=None):
    opts = "".join(f'<option{" selected" if o == default_type else ""}>{o}</option>' for o in FORM_OPTIONS)
    ph = f"e.g. {city}, CO" if city else "e.g. Lakewood, CO"
    return f"""
        <div class="quote-card" id="book">
          <h2>Book your roof inspection</h2>
          <p class="small">Reply within one business hour · Most inspections in 24–48 hours</p>
          <form name="inspection-request" method="POST" action="/thank-you.html" data-netlify="true" netlify-honeypot="company">
            <input type="hidden" name="form-name" value="inspection-request">
            <p class="hidden"><label>Leave blank <input name="company"></label></p>
            <div class="form-row">
              <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
              <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required></div>
            </div>
            <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
            <div class="field"><label for="f-address">Property address or city</label><input id="f-address" name="address" autocomplete="street-address" placeholder="{ph}" required></div>
            <div class="field"><label for="f-type">What do you need?</label><select id="f-type" name="inspection_type">{opts}</select></div>
            <button class="btn btn-primary" type="submit">Request My Inspection {icon("arrow-right")}</button>
          </form>
          <p class="assure">{icon("shield-check")} No obligation · No sales pressure</p>
        </div>"""


def hero(h1_html, lead, img_key, eyebrow=None, trail=None, ticks=None, default_type=None, city=None):
    ticks = ticks or ["Photo-documented report", "Hail & storm experts", "Every Denver metro city"]
    tick_html = "".join(f"<li>{icon('circle-check')} {esc(t)}</li>" for t in ticks)
    crumbs = breadcrumb_nav(trail) if trail else ""
    eb = f'<span class="eyebrow" style="color:#ffb37f">{esc(eyebrow)}</span>' if eyebrow else ""
    return f"""
  <main id="main">
    <section class="hero{' hero-sub' if trail else ''}" aria-labelledby="hero-title">
      <div class="hero-bg">{img(img_key, sizes="100vw", eager=True)}</div>
      <div class="container">
        {crumbs}
        <div class="hero-grid">
          <div>
            {eb}
            <h1 id="hero-title">{h1_html}</h1>
            <p class="lead">{esc(lead)}</p>
            <div class="hero-cta">
              <a class="btn btn-primary" href="#book">Schedule an Inspection {icon("arrow-right")}</a>
              <a class="btn btn-light" href="tel:{TEL}">{icon("phone")} {PHONE}</a>
            </div>
            <div class="hero-proof">
              <div class="g-rating"><b>4.9</b><div>{stars()}<span class="txt">370 Google reviews</span></div></div>
              <ul class="hero-ticks">{tick_html}</ul>
            </div>
          </div>
{form_card(default_type, city)}
        </div>
      </div>
    </section>
"""


def stats_band():
    items = [("star", "4.9 / 5", "Average rating on Google"), ("users", "370+", "Verified Google reviews"),
             ("map-pin", "30+", "Denver metro cities served"), ("clock", "24–48 hr", "Typical inspection turnaround")]
    cells = "".join(f'<div><span class="ic">{icon(i)}</span><p style="margin:0"><strong>{v}</strong><span>{t}</span></p></div>' for i, v, t in items)
    return f"""
    <div class="stats-wrap"><div class="container"><div class="stats">{cells}</div></div></div>
"""


def photo_card(slug, text=None, heading="h3"):
    s = SVC[slug]
    return f"""
          <a class="card card-link photo-card reveal" href="/{slug}/">
            <div class="thumb">{img(slug, sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 400px")}<span class="chip-ic">{icon(SERVICE_ICONS[slug])}</span></div>
            <div class="body">
              <{heading}>{esc(s['name'])}</{heading}>
              <p>{esc(text or s['short'])}</p>
              <span class="link-arrow">Learn more {icon("arrow-right")}</span>
            </div>
          </a>"""


def icon_card(slug):
    s = SVC[slug]
    return f"""
          <a class="card card-link icon-card reveal" href="/{slug}/">
            <span class="ic">{icon(SERVICE_ICONS[slug])}</span>
            <h3>{esc(s['name'])}</h3>
            <p>{esc(s['short'])}</p>
          </a>"""


def process_section(place="the Denver metro"):
    steps = [("calendar-days", "Schedule", f"Book online or by phone. Most inspections in {esc(place)} happen within 24–48 hours."),
             ("scan-search", "Inspect", "We examine every slope on foot and by drone where needed, plus gutters, flashing and the attic."),
             ("file-text", "Report", "You get a photo-documented report with every finding labeled and rated by urgency."),
             ("thumbs-up", "Decide", "We explain your options in plain English. No pressure and no upselling.")]
    lis = "".join(f'<li class="reveal"><span class="ic">{icon(i)}</span><span class="num">Step {n + 1}</span><h3>{t}</h3><p>{d}</p></li>'
                  for n, (i, t, d) in enumerate(steps))
    return f"""
    <section class="section soft" aria-labelledby="process-title">
      <div class="container">
        <div class="section-head center">
          <span class="eyebrow">How it works</span>
          <h2 id="process-title">A Simple, Four-Step Roof Inspection</h2>
          <p>No jargon, no pressure. Just clear answers about your roof.</p>
        </div>
        <ol class="steps">{lis}</ol>
      </div>
    </section>
"""


def faq_section(groups, title, intro="Straight answers to the questions Denver homeowners ask us most."):
    """groups: list of (group_title_html or None, [(q, a_html), ...])."""
    titled = any(t for t, _ in groups)
    qh = "h4" if titled else "h3"
    body = ""
    for gt, faqs in groups:
        items = "".join(f"""
            <details>
              <summary><{qh}>{esc(strip_tags(q))}</{qh}><span class="tog">{icon("chevron-down")}</span></summary>
              <div class="answer"><p>{a}</p></div>
            </details>""" for q, a in faqs)
        body += f'\n          <div class="faq-group">{f"<h3>{gt}</h3>" if gt else ""}{items}\n          </div>'
    return f"""
    <section class="section faq" id="faq" aria-labelledby="faq-title">
      <div class="container faq-layout">
        <div class="faq-aside">
          <span class="eyebrow">FAQ</span>
          <h2 id="faq-title">{esc(title)}</h2>
          <p>{intro}</p>
          <div class="card">
            <h3>Still have questions?</h3>
            <p>Talk to a Denver roof inspection specialist. We're happy to help, even if you're not ready to book.</p>
            <a class="btn btn-primary" href="tel:{TEL}">{icon("phone")} {PHONE}</a>
          </div>
        </div>
        <div>{body}
        </div>
      </div>
    </section>
"""


SAMPLE_REVIEWS = [  # SAMPLE TEXT: replace with verbatim excerpts from real Google reviews before launch
    ("After the hailstorm we had no idea if the roof was damaged. The inspector walked every slope, sent a report full of photos that afternoon, and the adjuster approved our claim without a fight.", "Homeowner", "Aurora, CO"),
    ("Honest is the word. They told us our roof was in good shape and didn't need anything. No upsell, no pressure. That's exactly why we'll call them again.", "Homeowner", "Lakewood, CO"),
    ("We were under contract on a house in Highlands Ranch. Their roof inspection found issues the home inspector missed, and we negotiated a credit that more than paid for it.", "Home buyer", "Highlands Ranch, CO"),
]


def reviews_section():
    cards = "".join(f"""
          <figure class="review reveal">
            <div class="top">{stars()}<span style="font-size:.8rem;color:var(--muted);font-weight:600">Google review</span></div>
            <blockquote>“{esc(q)}”</blockquote>
            <figcaption><span class="avatar" aria-hidden="true">{who[0]}</span><cite>{esc(who)}<span>{esc(where)}</span></cite></figcaption>
          </figure>""" for q, who, where in SAMPLE_REVIEWS)
    return f"""
    <section class="section soft" id="reviews" aria-labelledby="reviews-title">
      <div class="container">
        <div class="review-head">
          <div class="section-head">
            <span class="eyebrow">Customer reviews</span>
            <h2 id="reviews-title">370 Google Reviews. 4.9 Stars. Hundreds of Happy Denver Homeowners.</h2>
          </div>
          <div class="review-score"><b>4.9</b><div>{stars()}<span class="txt">Based on 370 Google reviews</span></div></div>
        </div>
        <!-- SAMPLE REVIEWS: replace with verbatim excerpts from real Google reviews (with permission) before launch. -->
        <div class="grid-3">{cards}
        </div>
        <p style="text-align:center;margin:40px 0 0"><a class="btn btn-outline" href="https://www.google.com/search?q=Roof+Inspection+Denver+reviews" rel="noopener" target="_blank">Read all reviews on Google {icon("arrow-right")}</a></p>
      </div>
    </section>
"""


def cta(where="the Denver metro", img_key="house-dusk"):
    return f"""
    <section class="cta" aria-labelledby="cta-title">
      <div class="container">
        <div class="cta-box">
          <div class="band-bg">{img(img_key, sizes="(max-width: 1240px) 100vw, 1240px")}</div>
          <div>
            <h2 id="cta-title">Get an Honest Answer About Your Roof</h2>
            <p>Book a roof inspection in {esc(where)}. Most appointments within 24–48 hours, with a photo report the same day.</p>
          </div>
          <div class="cta-actions">
            <a class="btn btn-primary" href="#book">Schedule Inspection {icon("arrow-right")}</a>
            <a class="btn btn-light" href="tel:{TEL}">{icon("phone")} {PHONE}</a>
          </div>
        </div>
      </div>
    </section>
  </main>
"""


def city_chips(cities, prefix=""):
    return "".join(f'<li><a href="{city_url(c)}">{icon("map-pin")}{esc(prefix + c["name"])}</a></li>' for c in cities)


def checks(items, cls=""):
    return f'<ul class="checks {cls}">' + "".join(f"<li>{icon('circle-check')}<span>{esc(i)}</span></li>" for i in items) + "</ul>"


# ---------------------------------------------------------------- homepage

def home_page():
    url = "/"
    all_faqs = [qa for _, qs in HOME_FAQ for qa in qs]
    graph = [business_node(full=True),
             {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Roof Inspection Denver",
              "publisher": {"@id": SITE + "/#business"}, "inLanguage": "en-US"},
             faq_ld(all_faqs, url), breadcrumbs_ld([("Home", "/")])]
    core = "".join(photo_card(s) for s in CORE_SERVICES)
    more = "".join(icon_card(s) for s in SVC if s not in CORE_SERVICES)
    feats = [("shield-check", "Inspection-first, not sales-first", "We report what's on your roof honestly, including when nothing needs to be done."),
             ("scan-search", "We actually walk the roof", "Every slope, up close, where it's safe, plus drone imaging for steep or fragile roofs."),
             ("camera", "Detailed photo reports", "Dozens of labeled photos, findings and clear recommendations, usually the same day."),
             ("badge-check", "Built for insurance & real estate", "Documentation organized the way adjusters, agents and lenders need it.")]
    feat_html = "".join(f'<li><span class="ic">{icon(i)}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for i, t, d in feats)
    signs = ["Hail about quarter-size or larger in your area", "Dents in gutters, downspouts, vents or car hoods",
             "Shingle granules collecting at downspouts", "Neighbors getting adjuster visits or new roofs",
             "New water stains on ceilings or in the attic", "Shingles or flashing on the ground after high winds"]
    checklist = ["Shingle, tile, metal or membrane condition", "Hail impacts, granule loss & bruising", "Wind creasing, lifted or missing tabs",
                 "Ridge caps, hips and valleys", "Step, counter & chimney flashing", "Pipe boots and roof penetrations",
                 "Skylights and curb seals", "Vents, turbines and exhaust caps", "Gutters, downspouts & drip edge",
                 "Fascia, soffit and decking", "Attic ventilation & insulation", "Leaks, staining or mold",
                 "Ice dam and snow-load indicators", "Previous repairs & workmanship", "Estimated remaining roof life"]
    groups = [(t, qs) for t, qs in HOME_FAQ]
    body = hero('Roof Inspection Denver <span class="hl">Homeowners Trust</span>',
                "Thorough, unbiased roof inspections for homes and businesses across the Denver metro. Whether it's fresh hail damage, a home purchase, or an aging roof, we climb it, photograph it, and tell you exactly what we find.",
                "hero", eyebrow="Denver's roof inspection specialists") + stats_band() + f"""
    <section class="section" id="services" aria-labelledby="services-title">
      <div class="container">
        <div class="section-head center">
          <span class="eyebrow">Our inspections</span>
          <h2 id="services-title">Every Type of Roof Inspection in the Denver Metro</h2>
          <p>From a bungalow in Wash Park to a commercial flat roof in Aurora, we inspect every roof type and every scenario.</p>
        </div>
        <div class="grid-3">{core}
        </div>
        <div class="grid-3" style="margin-top:28px">{more}
        </div>
      </div>
    </section>

    <section class="section soft" aria-labelledby="why-title">
      <div class="container split">
        <div class="media tall reveal">
          {img("inspector")}
          <div class="media-badge"><span class="ic">{icon("star")}</span><div><b>4.9 ★ on Google</b><span>370 reviews from Denver-area homeowners</span></div></div>
        </div>
        <div>
          <span class="eyebrow">Why a Denver roof inspection matters</span>
          <h2 id="why-title">Colorado Weather Is Hard on Roofs. We Show You Exactly Where.</h2>
          <p>Denver sits in the heart of Colorado's "Hail Alley," one of the most hail-prone regions in North America. Add intense UV at 5,280 feet, freeze-thaw swings, Chinook winds off the Front Range and heavy spring snow, and roofs here wear out faster than in most of the country.</p>
          <p>Most of that damage isn't visible from the driveway. A professional roof inspection gives you a documented picture of your roof so you can file a claim, negotiate a home purchase, plan a replacement, or simply rest easy.</p>
          <ul class="features">{feat_html}</ul>
        </div>
      </div>
    </section>
{process_section()}
    <section class="section band" id="hail" aria-labelledby="hail-title">
      <div class="band-bg">{img("hail-damage-roof-inspection", sizes="100vw")}</div>
      <div class="container split">
        <div>
          <span class="eyebrow">Hail damage roof inspection Denver</span>
          <h2 id="hail-title">Hit by Hail? Get Your Roof Inspected Before You File a Claim.</h2>
          <p>The Denver metro sees severe hail most often between April and September. Even one-inch hail can fracture shingles and knock away protective granules, often without any sign from the ground.</p>
          <p>Our hail inspections use test squares, impact mapping and date-stamped photos to give you an honest answer to the question every homeowner asks after a storm: <em>do I actually have damage worth claiming?</em></p>
          <a class="btn btn-primary" href="/hail-damage-roof-inspection/">Hail Damage Inspections {icon("arrow-right")}</a>
        </div>
        <div class="glass reveal">
          <h3>Signs you need an inspection after a storm</h3>
          {checks(signs, "one")}
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="checklist-title">
      <div class="container split reverse">
        <div class="media-stack reveal">
          {img("shingles", sizes="(max-width: 1024px) 60vw, 30vw")}
          {img("attic-ventilation-inspection", sizes="(max-width: 1024px) 40vw, 20vw")}
          {img("drone-roof-inspection", sizes="(max-width: 1024px) 40vw, 20vw")}
        </div>
        <div>
          <span class="eyebrow">What we inspect</span>
          <h2 id="checklist-title">Our 40+ Point Roof Inspection Checklist</h2>
          <p>Every inspection follows the same documented checklist, so nothing is missed. We inspect asphalt, Class 4 impact-resistant shingles, concrete and clay tile, metal, cedar shake, slate and flat roofs.</p>
          {checks(checklist)}
        </div>
      </div>
    </section>

    <section class="section soft" aria-labelledby="re-title">
      <div class="container split">
        <div class="media reveal">
          {img("real-estate-roof-inspection")}
          <div class="media-badge right"><span class="ic">{icon("clock")}</span><div><b>24–48 hour scheduling</b><span>Built around inspection deadlines</span></div></div>
        </div>
        <div>
          <span class="eyebrow">Real estate roof inspections</span>
          <h2 id="re-title">Buying or Selling in Denver? Know the Roof Before You Close.</h2>
          <p>Home inspectors are generalists and often recommend "further evaluation by a qualified roofer." We provide that specialist-level detail, fast.</p>
          <ul class="features">
            <li><span class="ic">{icon("key-round")}</span><div><h3>Home buyers</h3><p>Learn the roof's true age and remaining life before your objection deadline, and negotiate with documentation.</p></div></li>
            <li><span class="ic">{icon("house")}</span><div><h3>Home sellers</h3><p>A pre-listing inspection lets you fix issues on your terms and list with confidence.</p></div></li>
            <li><span class="ic">{icon("file-badge")}</span><div><h3>Agents &amp; lenders</h3><p>Clear reports and roof certification letters when the roof qualifies.</p></div></li>
          </ul>
        </div>
      </div>
    </section>
{reviews_section()}
    <section class="section" id="areas" aria-labelledby="areas-title">
      <div class="container split">
        <div>
          <span class="eyebrow">Service areas</span>
          <h2 id="areas-title">Roof Inspections Across the Greater Denver Metro</h2>
          <p>Based in Denver, we inspect roofs in every city across Denver, Adams, Arapahoe, Jefferson, Douglas, Broomfield and Boulder counties, including Capitol Hill, Washington Park, the Highlands, Park Hill, Cherry Creek, Central Park and Green Valley Ranch.</p>
          <ul class="chips">{city_chips(PAGE_CITIES)}</ul>
          <p style="margin-top:24px"><a class="link-arrow" href="/service-areas/">View all service areas {icon("arrow-right")}</a></p>
        </div>
        <div class="media tall reveal">{img("skyline")}</div>
      </div>
    </section>
{faq_section(groups, "Roof Inspection Denver FAQ")}{cta()}"""
    return (head("Roof Inspection Denver | Hail, Storm & Real Estate Roof Inspections",
                 "Roof Inspection Denver provides thorough, unbiased roof inspections for homes and businesses across the Denver metro: hail damage, real estate, insurance and certification inspections. Rated 4.9★ from 370 Google reviews.",
                 url, graph, preload="hero") + header(home=True) + body + footer())


# ---------------------------------------------------------------- service page

def service_page(s):
    url = f"/{s['slug']}/"
    trail = [("Home", "/"), ("Inspections", "/services/"), (s["name"], url)]
    graph = [business_node(), {
        "@type": "Service", "@id": SITE + url + "#service", "name": s["name"], "serviceType": s["name"],
        "description": s["short"], "provider": {"@id": SITE + "/#business"}, "url": SITE + url,
        "image": f"{SITE}/assets/img/{s['slug']}-1600.webp",
        "areaServed": [{"@type": "City", "name": f"{c['name']}, CO"} for c in CITIES]},
        faq_ld(s["faqs"], url), breadcrumbs_ld(trail)]
    intro = "".join(f"<p>{p}</p>" for p in s["intro"])
    rows = "".join(f"""
        <article class="ed-row reveal">
          <h2>{esc(h2)}</h2>
          <div class="prose">{body_html}</div>
        </article>""" for h2, body_html in s["sections"])
    extra = f"""
    <section class="section" aria-label="{esc(s['name'])} details">
      <div class="container editorial">{rows}
      </div>
    </section>
"""
    related = "".join(photo_card(r) for r in s["related"])
    lower = s["name"].lower()
    second = "inspector" if s["slug"] != "residential-roof-inspection" else "shingles"
    body = hero(esc(s["h1"]), s["lead"], s["slug"], trail=trail) + stats_band() + f"""
    <section class="section" aria-labelledby="intro-title">
      <div class="container split">
        <div class="prose">
          <span class="eyebrow">{esc(s['name'])}</span>
          <h2 id="intro-title">Why Denver Property Owners Choose Our {esc(s['name'])}</h2>
          {intro}
          <a class="btn btn-dark" href="#book">Book Your Inspection {icon("arrow-right")}</a>
        </div>
        <div class="media tall reveal">
          {img(second)}
          <div class="media-badge"><span class="ic">{icon("camera")}</span><div><b>Same-day photo report</b><span>Every finding labeled and explained</span></div></div>
        </div>
      </div>
    </section>

    <section class="section soft" aria-labelledby="included-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">What's included</span>
          <h2 id="included-title">What Our {esc(s['name'])} Covers</h2>
        </div>
        <div class="checks-card reveal">{checks(s['included'], 'three')}</div>
      </div>
    </section>

    <section class="section band" aria-labelledby="when-title">
      <div class="band-bg">{img("house-dusk", sizes="100vw")}</div>
      <div class="container split">
        <div>
          <span class="eyebrow">When to book</span>
          <h2 id="when-title">When to Schedule a {esc(s['name'])}</h2>
          <p>If any of these sound familiar, an inspection will give you clear, documented answers and peace of mind.</p>
          <a class="btn btn-primary" href="#book">Schedule Now {icon("arrow-right")}</a>
        </div>
        <div class="glass reveal">{checks(s['when'], 'one')}</div>
      </div>
    </section>
{extra}{process_section()}
    <section class="section" aria-labelledby="areas-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Service areas</span>
          <h2 id="areas-title">{esc(s['name'])} Across the Denver Metro</h2>
          <p>We provide {esc(lower)}s in every city in the greater Denver area, plus Denver itself. Choose your city for local details.</p>
        </div>
        <ul class="chips">{city_chips(PAGE_CITIES)}</ul>
      </div>
    </section>
{faq_section([(None, s['faqs'])], s['name'] + ' FAQ', 'Common questions about our ' + esc(lower) + 's in Denver.')}
    <section class="section soft" aria-labelledby="related-title">
      <div class="container">
        <div class="section-head"><span class="eyebrow">Related</span><h2 id="related-title">Related Roof Inspection Services</h2></div>
        <div class="grid-3">{related}
        </div>
      </div>
    </section>
{cta()}"""
    return head(s["title"], s["meta"], url, graph, preload=s["slug"]) + header() + body + footer()


# ---------------------------------------------------------------- city page

CITY_SERVICE_BLURBS = {
    "residential-roof-inspection": "Complete condition report and remaining-life estimate for your {city} home.",
    "hail-damage-roof-inspection": "Test squares, impact mapping and photos after a {city} hailstorm.",
    "real-estate-roof-inspection": "Fast inspections for {city} buyers, sellers and agents on a deadline.",
    "roof-certification": "Written certification letters for qualifying {city} roofs.",
    "insurance-claim-roof-inspection": "Organized storm documentation to support your {city} claim.",
    "commercial-roof-inspection": "Flat, low-slope and HOA roof inspections for {city} properties.",
}


def city_faqs(c):
    n = c["name"]
    return [
        (f"How much does a roof inspection cost in {n}?",
         f"Pricing depends on the size, pitch and material of your roof and the type of inspection you need. Call or request an inspection online and we'll give you a clear, upfront price for your {n} property before we schedule. There are no hidden fees."),
        (f"How quickly can you inspect my roof in {n}?",
         f"We typically schedule roof inspections in {n} within 24–48 hours, with priority scheduling for real estate deadlines and after major hailstorms. Your photo report usually arrives the same day or next business day."),
        *c["faqs"],
        (f"What should I do after a hailstorm in {n}?",
         f"Note the date of the storm, look for dents on gutters, vents and vehicles, and schedule a <a href=\"/hail-damage-roof-inspection/\">hail damage roof inspection</a> while the evidence is fresh. If damage is confirmed, our report helps you file a well-documented insurance claim."),
    ]


def city_page(c, idx):
    n = c["name"]
    url = city_url(c)
    trail = [("Home", "/"), ("Service Areas", "/service-areas/"), (f"{n}, CO", url)]
    faqs = city_faqs(c)
    graph = [business_node(), {
        "@type": "Service", "@id": SITE + url + "#service", "name": f"Roof Inspection in {n}, CO", "serviceType": "Roof Inspection",
        "provider": {"@id": SITE + "/#business"}, "url": SITE + url,
        "areaServed": {"@type": "City", "name": f"{n}, CO", "containedInPlace": {"@type": "AdministrativeArea", "name": c["county"] + ", Colorado"}}},
        faq_ld(faqs, url), breadcrumbs_ld(trail)]
    title = f"Roof Inspection {n}, CO | Hail & Real Estate Roof Inspections"
    if len(title) > 65:
        title = f"Roof Inspection {n}, CO | Roof Inspection Denver"
    meta = (f"Roof inspections in {n}, CO: hail damage, storm, real estate, insurance and roof certification "
            f"inspections with photo reports. Serving {c['county']}. 4.9★ from 370 Google reviews.")
    hero_key = CITY_HEROES[idx % len(CITY_HEROES)]
    local_key = CITY_HEROES[(idx + 2) % len(CITY_HEROES)]
    intro = "".join(f"<p>{p}</p>" for p in c["intro"])
    hoods = "".join(f"<li><span>{icon('map-pin')}{esc(h)}</span></li>" for h in c["hoods"])
    services = "".join(photo_card(s, CITY_SERVICE_BLURBS[s].format(city=n)) for s in CORE_SERVICES)
    nearby = [CITY_BY_NAME[x] for x in c["nearby"] if x in CITY_BY_NAME]
    lead = (f"Thorough, unbiased roof inspections for homes and businesses in {n}. Hail damage, storm damage, "
            f"real estate and insurance inspections with a detailed photo report, usually within 24–48 hours.")
    why = [("shield-check", "Inspection-first", "Honest reports, never a sales pitch."),
           ("clock", f"Fast in {n}", "Most inspections within 24–48 hours."),
           ("camera", "Photo-documented", "Insurance- and real-estate-ready reports.")]
    why_html = "".join(f'<li><span class="ic">{icon(i)}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>' for i, t, d in why)
    body = hero(f"Roof Inspection in {esc(n)}, CO", lead, hero_key, eyebrow=f"Serving {c['county']}", trail=trail, city=n) + stats_band() + f"""
    <section class="section" aria-labelledby="intro-title">
      <div class="container split">
        <div class="prose">
          <span class="eyebrow">Local roof inspections</span>
          <h2 id="intro-title">Trusted Roof Inspections for {esc(n)} Homeowners</h2>
          {intro}
          <ul class="features">{why_html}</ul>
        </div>
        <div class="media tall reveal">
          {img("inspector")}
          <div class="media-badge"><span class="ic">{icon("star")}</span><div><b>4.9 ★ on Google</b><span>370 reviews across the Denver metro</span></div></div>
        </div>
      </div>
    </section>

    <section class="section soft" aria-labelledby="local-title">
      <div class="container split reverse">
        <div class="media reveal">{img(local_key)}</div>
        <div class="prose">
          <span class="eyebrow">Local roofing conditions</span>
          <h2 id="local-title">What {esc(n)} Roofs Are Up Against</h2>
          <p>{c['local']}</p>
          <h3>Common roof concerns we see in {esc(n)}</h3>
          {checks(c['notes'], 'one')}
        </div>
      </div>
      <div class="container" style="margin-top:64px">
        <div class="checks-card">
          <h3>{esc(n)} neighborhoods we serve</h3>
          <ul class="chips">{hoods}</ul>
          <p style="margin:18px 0 0">Don't see your neighborhood? We inspect roofs everywhere in {esc(n)} and throughout {esc(c['county'])}.</p>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="services-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Inspection services</span>
          <h2 id="services-title">Roof Inspection Services in {esc(n)}</h2>
          <p>Our most-requested inspections in {esc(n)}, plus drone, leak detection, attic and new-roof inspections. <a href="/services/">See all inspection services</a>.</p>
        </div>
        <div class="grid-3">{services}
        </div>
      </div>
    </section>
{process_section(n)}{faq_section([(None, faqs)], f'Roof Inspection {n} FAQ', f'Answers for {esc(n)} homeowners, buyers and property managers.')}
    <section class="section soft" aria-labelledby="nearby-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Nearby</span>
          <h2 id="nearby-title">Roof Inspections Near {esc(n)}</h2>
          <p>We also serve nearby communities across the Denver metro. <a href="/service-areas/">See all service areas</a>.</p>
        </div>
        <ul class="chips">{city_chips(nearby, "Roof Inspection ")}</ul>
      </div>
    </section>
{cta(n)}"""
    return head(title, meta, url, graph, preload=hero_key) + header() + body + footer()


# ---------------------------------------------------------------- hubs & misc

def services_hub():
    url = "/services/"
    trail = [("Home", "/"), ("Inspections", url)]
    graph = [business_node(), breadcrumbs_ld(trail), {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{s['slug']}/", "name": s["name"]} for i, s in enumerate(SERVICES)]}]
    cards = "".join(photo_card(s["slug"]) for s in SERVICES)
    body = hero("Roof Inspection Services in Denver",
                "From hail damage and real estate inspections to roof certifications, drone imaging and leak detection: every type of roof inspection for homes and businesses across the Denver metro.",
                "hero", trail=trail) + stats_band() + f"""
    <section class="section" aria-labelledby="all-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">All services</span>
          <h2 id="all-title">Choose Your Roof Inspection</h2>
          <p>Not sure which inspection you need? Call <a href="tel:{TEL}">{PHONE}</a> and we'll point you in the right direction.</p>
        </div>
        <div class="grid-3">{cards}
        </div>
      </div>
    </section>
{process_section()}{cta()}"""
    return head("Roof Inspection Services Denver | Hail, Real Estate & More",
                "Every type of roof inspection in the Denver metro: residential, hail damage, storm, real estate, roof certification, insurance, commercial, drone and leak detection. 4.9★ from 370 reviews.",
                url, graph, preload="hero") + header() + body + footer()


def areas_hub():
    url = "/service-areas/"
    trail = [("Home", "/"), ("Service Areas", url)]
    graph = [business_node(), breadcrumbs_ld(trail), {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": SITE + city_url(c), "name": f"Roof Inspection {c['name']}, CO"} for i, c in enumerate(CITIES)]}]
    cards = "".join(f"""
          <a class="card card-link area-card" href="{city_url(c)}">
            <div><h3>Roof Inspection {esc(c['name'])}</h3><span>{esc(c['county'])}</span></div>{icon("arrow-right")}
          </a>""" for c in sorted(CITIES, key=lambda c: c["name"]))
    body = hero("Roof Inspections Across the Greater Denver Metro",
                "Based in Denver, we inspect roofs in every city and community across Denver, Adams, Arapahoe, Jefferson, Douglas, Broomfield and Boulder counties.",
                "skyline", trail=trail) + stats_band() + f"""
    <section class="section" aria-labelledby="cities-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Cities we serve</span>
          <h2 id="cities-title">Find Roof Inspections in Your City</h2>
          <p>Select your city for local roofing conditions, neighborhoods and FAQs. If you're anywhere in the Denver metro and don't see your community, <a href="#book">just ask</a>. We serve it.</p>
        </div>
        <div class="grid-4">{cards}
        </div>
      </div>
    </section>
{cta()}"""
    return head("Roof Inspection Service Areas | Denver Metro Cities We Serve",
                "Roof Inspection Denver serves 30+ cities across the Denver metro, including Aurora, Lakewood, Arvada, Westminster, Centennial, Highlands Ranch, Boulder and more. 4.9★ from 370 reviews.",
                url, graph, preload="skyline") + header() + body + footer()


def simple_page(path, title, h1, content_html, robots="noindex, follow"):
    body = f"""
  <main id="main">
    <section class="hero hero-sub" aria-labelledby="hero-title">
      <div class="hero-bg">{img("house-dusk", sizes="100vw", eager=True)}</div>
      <div class="container" style="padding-bottom:96px">
        <h1 id="hero-title">{esc(h1)}</h1>
      </div>
    </section>
    <section class="section">
      <div class="container narrow prose">
{content_html}
      </div>
    </section>
  </main>
"""
    return head(f"{title} | Roof Inspection Denver", title, path, None, robots=robots) + header() + body + footer()


MISC = {
    "thank-you.html": ("Thank You", "Thanks! Your Inspection Request Is In", f"""        <p class="lead">A member of our team will reach out shortly (usually within one business hour) to confirm your inspection time.</p>
        <p>Need us sooner? Call <a href="tel:{TEL}">{PHONE}</a>.</p>
        <p><a class="btn btn-primary" href="/">Back to Home</a></p>"""),
    "404.html": ("Page Not Found", "Page Not Found", """        <p class="lead">We couldn't find that page, but we can still find hail damage on your roof.</p>
        <p><a class="btn btn-primary" href="/">Go to the Home Page</a> &nbsp; <a class="btn btn-outline" href="/services/">Browse Inspections</a></p>"""),
    "privacy.html": ("Privacy Policy", "Privacy Policy", f"""        <p>Roof Inspection Denver (roofinspectiondenver.com) respects your privacy. When you request an inspection, we collect the information you provide, such as your name, phone number, email address and property address, and use it only to schedule and perform your roof inspection and to communicate with you about it.</p>
        <h2>Information Sharing</h2>
        <p>We do not sell your personal information. We share it only with service providers who help us operate our business (for example, form handling or scheduling tools), or when required by law.</p>
        <h2>Contact</h2>
        <p>Questions about this policy? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>"""),
}


def sitemap(urls):
    body = "\n".join(f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n  </url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')


def main():
    missing = [k for k in IMAGES if not os.path.exists(os.path.join(ROOT, "assets", "img", f"{k}-1600.webp"))]
    if missing:
        sys.exit(f"Missing images {missing}. Run: python3 build/images.py placeholders")
    urls = ["/", "/services/", "/service-areas/"]
    write("index.html", home_page())
    write("services/index.html", services_hub())
    write("service-areas/index.html", areas_hub())
    for s in SERVICES:
        write(f"{s['slug']}/index.html", service_page(s))
        urls.append(f"/{s['slug']}/")
    for i, c in enumerate(PAGE_CITIES):
        write(f"{c['slug']}/index.html", city_page(c, i))
        urls.append(city_url(c))
    for path, (title, h1, content) in MISC.items():
        write(path, simple_page("/" + path, title, h1, content))
    sitemap(urls)
    print(f"Generated home, {len(SERVICES)} service pages, {len(PAGE_CITIES)} city pages, 2 hubs, {len(MISC)} misc; sitemap has {len(urls)} URLs.")


if __name__ == "__main__":
    main()
