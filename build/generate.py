#!/usr/bin/env python3
"""Generate service pages, city pages, hub pages and sitemap.

Run from the repo root:  python3 build/generate.py
Edit content in build/services_data.py and build/cities_data.py, then re-run.
Also rewrites the shared header/footer in index.html between the
<!-- HEADER:START/END --> and <!-- FOOTER:START/END --> markers.
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://roofinspectiondenver.com"
PHONE = "(303) 555-0142"
TEL = "+13035550142"
TODAY = date.today().isoformat()

SVC = {s["slug"]: s for s in SERVICES}
CITY_BY_NAME = {c["name"]: c for c in CITIES}
esc = html.escape


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


# ---------------------------------------------------------------- shared parts

def business_node():
    return {
        "@type": ["RoofingContractor", "LocalBusiness"],
        "@id": SITE + "/#business",
        "name": "Roof Inspection Denver",
        "url": SITE + "/",
        "telephone": "+1-303-555-0142",
        "image": SITE + "/assets/og-image.png",
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "addressLocality": "Denver", "addressRegion": "CO", "addressCountry": "US"},
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": "370", "bestRating": "5"},
    }


def breadcrumbs_ld(trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + url}
            for i, (name, url) in enumerate(trail)
        ],
    }


def faq_ld(faqs, url):
    return {
        "@type": "FAQPage",
        "@id": SITE + url + "#faq",
        "mainEntity": [
            {"@type": "Question", "name": strip_tags(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in faqs
        ],
    }


def head(title, meta, url, graph):
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en-US">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(meta)}">
  <link rel="canonical" href="{SITE}{url}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="geo.region" content="US-CO">
  <meta name="theme-color" content="#0f2a3f">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Roof Inspection Denver">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(meta)}">
  <meta property="og:url" content="{SITE}{url}">
  <meta property="og:image" content="{SITE}/assets/og-image.png">
  <meta property="og:locale" content="en_US">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/styles.css">
  <script type="application/ld+json">
{ld}
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
"""


def header():
    return f"""<!-- HEADER:START -->
  <div class="topbar">
    <div class="container">
      <span><span class="stars" aria-hidden="true">★★★★★</span> 4.9 rating from 370 Google reviews</span>
      <span class="hide-sm">Serving Denver &amp; the entire Front Range metro · <a href="tel:{TEL}">{PHONE}</a></span>
    </div>
  </div>

  <header class="site-header">
    <div class="container">
      <a class="brand" href="/" aria-label="Roof Inspection Denver home">
        <img src="/assets/favicon.svg" alt="" width="36" height="36">
        Roof Inspection Denver
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
        <span></span><span></span><span></span>
      </button>
      <nav class="nav" id="site-nav" aria-label="Main">
        <ul>
          <li><a href="/services/">Inspections</a></li>
          <li><a href="/hail-damage-roof-inspection/">Hail Damage</a></li>
          <li><a href="/real-estate-roof-inspection/">Real Estate</a></li>
          <li><a href="/service-areas/">Service Areas</a></li>
          <li><a href="/#reviews">Reviews</a></li>
          <li><a href="/#faq">FAQ</a></li>
          <li><a class="btn btn-primary" href="#book">Book an Inspection</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <!-- HEADER:END -->"""


def footer():
    svc_links = "\n".join(f'            <li><a href="/{s["slug"]}/">{esc(s["name"])}</a></li>' for s in SERVICES[:6])
    city_links = "\n".join(f'            <li><a href="/{c["slug"]}/">{esc(c["name"])}</a></li>' for c in PAGE_CITIES[:6])
    return f"""<!-- FOOTER:START -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <h2>Roof Inspection Denver</h2>
          <p>Professional, unbiased roof inspections for homeowners, buyers, sellers, agents and property managers across the greater Denver, Colorado metro area.</p>
          <p><span class="stars" aria-hidden="true">★★★★★</span> 4.9 from 370 Google reviews</p>
        </div>
        <div>
          <h3>Inspections</h3>
          <ul>
{svc_links}
            <li><a href="/services/">All inspection services →</a></li>
          </ul>
        </div>
        <div>
          <h3>Service Areas</h3>
          <ul>
{city_links}
            <li><a href="/service-areas/">All service areas →</a></li>
          </ul>
        </div>
        <div>
          <h3>Contact</h3>
          <address style="font-style:normal">
            <ul>
              <li>Denver, CO</li>
              <li><a href="tel:{TEL}">{PHONE}</a></li>
              <li><a href="mailto:info@roofinspectiondenver.com">info@roofinspectiondenver.com</a></li>
              <li>Mon–Fri 7am–6pm · Sat 8am–2pm</li>
            </ul>
          </address>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© <span id="year">2026</span> Roof Inspection Denver · roofinspectiondenver.com</span>
        <span><a href="/privacy.html">Privacy Policy</a></span>
      </div>
    </div>
  </footer>

  <a class="mobile-call" href="tel:{TEL}">📞 Call for a Roof Inspection</a>

  <script>
    (function () {{
      var btn = document.querySelector('.nav-toggle');
      var nav = document.getElementById('site-nav');
      btn.addEventListener('click', function () {{
        var open = nav.classList.toggle('open');
        btn.setAttribute('aria-expanded', open);
      }});
      nav.addEventListener('click', function (e) {{
        if (e.target.tagName === 'A') {{ nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }}
      }});
      document.getElementById('year').textContent = new Date().getFullYear();
    }})();
  </script>
  <!-- FOOTER:END -->"""


def page_end():
    return "\n" + footer() + "\n</body>\n</html>\n"


def breadcrumb_nav(trail):
    parts = []
    for i, (name, url) in enumerate(trail):
        if i == len(trail) - 1:
            parts.append(f'<span aria-current="page">{esc(name)}</span>')
        else:
            parts.append(f'<a href="{url}">{esc(name)}</a>')
    sep = ' <span aria-hidden="true">›</span> '
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb">{sep.join(parts)}</nav>'


def form_card(default_type=None, city=None):
    options = ["Hail or storm damage", "Buying / selling a home", "Roof certification",
               "Insurance claim documentation", "Leak or moisture concern",
               "General roof condition check", "Commercial / multi-family"]
    opts = "".join(
        f'<option{" selected" if o == default_type else ""}>{o}</option>' for o in options)
    placeholder = f"e.g. {city}, CO" if city else "e.g. Lakewood, CO"
    return f"""
        <div class="quote-card" id="book">
          <h2>Request a Roof Inspection</h2>
          <p class="small">We typically respond within one business hour and can often inspect within 24–48 hours.</p>
          <form name="inspection-request" method="POST" action="/thank-you.html" data-netlify="true" netlify-honeypot="company">
            <input type="hidden" name="form-name" value="inspection-request">
            <p class="hidden"><label>Leave blank <input name="company"></label></p>
            <div class="form-row">
              <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
              <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required></div>
            </div>
            <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
            <div class="field"><label for="f-address">Property address or city</label><input id="f-address" name="address" autocomplete="street-address" placeholder="{placeholder}" required></div>
            <div class="field"><label for="f-type">Inspection type</label><select id="f-type" name="inspection_type">{opts}</select></div>
            <button class="btn btn-primary" type="submit">Get My Inspection Scheduled</button>
          </form>
        </div>"""


def hero(trail, eyebrow, h1, lead, default_type=None, city=None):
    return f"""
  <main id="main">
    <section class="hero hero-sub" aria-labelledby="hero-title">
      <div class="container">
        {breadcrumb_nav(trail)}
      </div>
      <div class="container hero-grid">
        <div>
          <span class="eyebrow" style="color:#f7b48a">{esc(eyebrow)}</span>
          <h1 id="hero-title">{esc(h1)}</h1>
          <p class="lead">{esc(lead)}</p>
          <div class="hero-cta">
            <a class="btn btn-primary" href="#book">Schedule an Inspection</a>
            <a class="btn btn-ghost" href="tel:{TEL}">Call {PHONE}</a>
          </div>
          <div class="rating-badge">
            <span class="stars" aria-hidden="true">★★★★★</span>
            <span><strong>4.9 / 5</strong> from <strong>370</strong> Google reviews</span>
          </div>
        </div>
{form_card(default_type, city)}
      </div>
    </section>
"""


def process_section(place="the Denver metro"):
    return f"""
    <section class="section alt" aria-labelledby="process-title">
      <div class="container">
        <div class="section-head center">
          <span class="eyebrow">How It Works</span>
          <h2 id="process-title">Our 4-Step Roof Inspection Process</h2>
        </div>
        <ol class="steps">
          <li><h3>Schedule</h3><p>Book online or by phone. Most inspections in {esc(place)} happen within 24–48 hours.</p></li>
          <li><h3>Inspect</h3><p>We examine the roof on foot and by drone where needed, plus gutters, flashing and the attic.</p></li>
          <li><h3>Report</h3><p>You get a photo-documented report with every finding labeled and rated by urgency.</p></li>
          <li><h3>Next Steps</h3><p>We explain your options in plain English — no pressure and no upselling.</p></li>
        </ol>
      </div>
    </section>
"""


def faq_section(faqs, title):
    items = "\n".join(f"""          <details>
            <summary><h3>{esc(q)}</h3></summary>
            <div class="answer"><p>{a}</p></div>
          </details>""" for q, a in faqs)
    return f"""
    <section class="section faq" id="faq" aria-labelledby="faq-title">
      <div class="container" style="max-width:900px">
        <div class="section-head center">
          <span class="eyebrow">FAQ</span>
          <h2 id="faq-title">{esc(title)}</h2>
        </div>
        <div class="faq-group">
{items}
        </div>
      </div>
    </section>
"""


def cta_band(where="the Denver metro"):
    return f"""
    <section class="cta-band" aria-labelledby="cta-title">
      <div class="container">
        <div>
          <h2 id="cta-title">Ready for an Honest Answer About Your Roof?</h2>
          <p style="margin:0">Book a roof inspection in {esc(where)} — most appointments within 24–48 hours.</p>
        </div>
        <div style="display:flex; gap:12px; flex-wrap:wrap">
          <a class="btn btn-primary" href="#book">Schedule an Inspection</a>
          <a class="btn btn-ghost" href="tel:{TEL}">{PHONE}</a>
        </div>
      </div>
    </section>
  </main>
"""


def city_url(c):
    # The homepage targets "roof inspection Denver"; a separate Denver page would compete with it.
    return "/" if c["name"] == "Denver" else f"/{c['slug']}/"


PAGE_CITIES = [c for c in CITIES if c["name"] != "Denver"]


def city_link_list(cities, prefix=""):
    return "\n".join(f'          <li><a href="{city_url(c)}">{esc(prefix + c["name"])}</a></li>' for c in cities)


def write(rel_dir, content):
    d = os.path.join(ROOT, rel_dir)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w") as f:
        f.write(content)


# ---------------------------------------------------------------- service page

def service_page(s):
    url = f"/{s['slug']}/"
    trail = [("Home", "/"), ("Inspections", "/services/"), (s["name"], url)]
    graph = [
        business_node(),
        {
            "@type": "Service",
            "@id": SITE + url + "#service",
            "name": s["name"],
            "serviceType": s["name"],
            "description": s["short"],
            "provider": {"@id": SITE + "/#business"},
            "areaServed": [{"@type": "City", "name": f"{c['name']}, CO"} for c in CITIES],
            "url": SITE + url,
        },
        faq_ld(s["faqs"], url),
        breadcrumbs_ld(trail),
    ]
    intro = "".join(f"<p>{p}</p>" for p in s["intro"])
    included = "".join(f"<li>{esc(i)}</li>" for i in s["included"])
    when = "".join(f"<li>{esc(w)}</li>" for w in s["when"])
    extra = ""
    for i, (h2, body) in enumerate(s["sections"]):
        cls = "section alt" if i % 2 else "section"
        extra += f"""
    <section class="{cls}">
      <div class="container prose">
        <h2>{esc(h2)}</h2>
        {body}
      </div>
    </section>
"""
    related = "".join(f"""
          <a class="card card-link" href="/{r}/">
            <div class="icon" aria-hidden="true">{SVC[r]['icon']}</div>
            <h3>{esc(SVC[r]['name'])}</h3>
            <p>{esc(SVC[r]['short'])}</p>
          </a>""" for r in s["related"])
    lower = s["name"].lower()
    body = hero(trail, "Roof Inspection Denver", s["h1"], s["lead"],
                default_type=None) + f"""
    <section class="section" aria-labelledby="intro-title">
      <div class="container grid-2">
        <div class="prose">
          <h2 id="intro-title">Why Denver Property Owners Choose Our {esc(s['name'])}</h2>
          {intro}
        </div>
        <div class="callout">
          <h3>When to schedule a {esc(lower)}</h3>
          <ul>{when}</ul>
          <a class="btn btn-primary" href="#book">Book Your Inspection</a>
        </div>
      </div>
    </section>

    <section class="section alt" aria-labelledby="included-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">What's Included</span>
          <h2 id="included-title">What Our {esc(s['name'])} Covers</h2>
        </div>
        <ul class="checklist checklist-3">{included}</ul>
      </div>
    </section>
{extra}{process_section()}
    <section class="section" aria-labelledby="areas-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Service Areas</span>
          <h2 id="areas-title">{esc(s['name'])} Across the Denver Metro</h2>
          <p>We provide {esc(lower)}s in every city in the greater Denver area. Choose your city for local details:</p>
        </div>
        <ul class="areas areas-links">
{city_link_list(PAGE_CITIES)}
        </ul>
      </div>
    </section>
{faq_section(s['faqs'], s['name'] + ' FAQ')}
    <section class="section alt" aria-labelledby="related-title">
      <div class="container">
        <div class="section-head"><h2 id="related-title">Related Roof Inspection Services</h2></div>
        <div class="grid-3">{related}
        </div>
      </div>
    </section>
{cta_band()}"""
    return head(s["title"], s["meta"], url, graph) + header() + body + page_end()


# ---------------------------------------------------------------- city page

CITY_SERVICE_BLURBS = {
    "residential-roof-inspection": "Complete condition report and remaining-life estimate for your {city} home.",
    "hail-damage-roof-inspection": "Test squares, impact mapping and photos after a {city} hailstorm.",
    "storm-damage-roof-inspection": "Find lifted, creased and missing shingles after high winds in {city}.",
    "real-estate-roof-inspection": "Fast inspections for {city} buyers, sellers and agents on a deadline.",
    "roof-certification": "Written certification letters for qualifying {city} roofs.",
    "insurance-claim-roof-inspection": "Organized storm documentation to support your {city} claim.",
    "commercial-roof-inspection": "Flat, low-slope and HOA roof inspections for {city} properties.",
    "drone-roof-inspection": "Aerial imaging for steep, tall, tile and slate roofs in {city}.",
    "infrared-roof-inspection": "Trace leaks to their true source with thermal imaging.",
    "annual-roof-maintenance-inspection": "A yearly check-up that keeps {city} roofs ahead of Colorado weather.",
    "new-roof-warranty-inspection": "Independent verification of a newly installed roof.",
    "attic-ventilation-inspection": "Stop ice dams and condensation at the source.",
}


CITY_CARD_SERVICES = {
    "residential-roof-inspection", "hail-damage-roof-inspection", "real-estate-roof-inspection",
    "insurance-claim-roof-inspection", "roof-certification", "commercial-roof-inspection",
}


def city_faqs(c):
    n = c["name"]
    return [
        (f"How much does a roof inspection cost in {n}?",
         f"Pricing depends on the size, pitch and material of your roof and the type of inspection you need. Call or request an inspection online and we'll give you a clear, upfront price for your {n} property before we schedule — no hidden fees."),
        (f"How quickly can you inspect my roof in {n}?",
         f"We typically schedule roof inspections in {n} within 24–48 hours, with priority scheduling for real estate deadlines and after major hailstorms. Your photo report usually arrives the same day or next business day."),
        *c["faqs"],
        (f"What should I do after a hailstorm in {n}?",
         f"Note the date of the storm, look for dents on gutters, vents and vehicles, and schedule a <a href=\"/hail-damage-roof-inspection/\">hail damage roof inspection</a> while the evidence is fresh. If damage is confirmed, our report helps you file a well-documented insurance claim."),
    ]


def city_page(c):
    n = c["name"]
    url = f"/{c['slug']}/"
    trail = [("Home", "/"), ("Service Areas", "/service-areas/"), (f"{n}, CO", url)]
    faqs = city_faqs(c)
    graph = [
        business_node(),
        {
            "@type": "Service",
            "@id": SITE + url + "#service",
            "name": f"Roof Inspection in {n}, CO",
            "serviceType": "Roof Inspection",
            "provider": {"@id": SITE + "/#business"},
            "areaServed": {"@type": "City", "name": f"{n}, CO",
                           "containedInPlace": {"@type": "AdministrativeArea", "name": c["county"] + ", Colorado"}},
            "url": SITE + url,
        },
        faq_ld(faqs, url),
        breadcrumbs_ld(trail),
    ]
    title = f"Roof Inspection {n}, CO | Hail & Real Estate Roof Inspections"
    if len(title) > 65:
        title = f"Roof Inspection {n}, CO | Roof Inspection Denver"
    meta = (f"Roof inspections in {n}, CO: hail damage, storm, real estate, insurance and roof certification "
            f"inspections with photo reports. Serving {c['county']}. 4.9★ from 370 Google reviews.")
    intro = "".join(f"<p>{p}</p>" for p in c["intro"])
    notes = "".join(f"<li>{esc(x)}</li>" for x in c["notes"])
    hoods = "".join(f"<li>{esc(h)}</li>" for h in c["hoods"])
    services = "".join(f"""
          <a class="card card-link" href="/{s['slug']}/">
            <div class="icon" aria-hidden="true">{s['icon']}</div>
            <h3>{esc(s['name'])}</h3>
            <p>{esc(CITY_SERVICE_BLURBS[s['slug']].format(city=n))}</p>
          </a>""" for s in SERVICES if s["slug"] in CITY_CARD_SERVICES)
    nearby = [CITY_BY_NAME[x] for x in c["nearby"] if x in CITY_BY_NAME]
    lead = (f"Thorough, unbiased roof inspections for homes and businesses in {n}. Hail damage, storm damage, "
            f"real estate and insurance inspections with a detailed photo report — usually within 24–48 hours.")
    body = hero(trail, f"Serving {c['county']}", f"Roof Inspection in {n}, CO", lead, city=n) + f"""
    <section class="section" aria-labelledby="intro-title">
      <div class="container grid-2">
        <div class="prose">
          <h2 id="intro-title">Trusted Roof Inspections for {esc(n)} Homeowners</h2>
          {intro}
          <p>Every inspection includes a written, photo-documented report, an estimate of your roof's remaining life, and plain-English recommendations. If your roof is in good shape, we'll tell you so.</p>
        </div>
        <div class="callout">
          <h3>Why {esc(n)} chooses Roof Inspection Denver</h3>
          <ul class="checklist" style="columns:1">
            <li><strong>4.9★ from 370 Google reviews</strong> across the Denver metro</li>
            <li><strong>Inspection-first:</strong> honest reports, never a sales pitch</li>
            <li><strong>Fast scheduling</strong> in {esc(n)}, often within 24–48 hours</li>
            <li><strong>Insurance- and real-estate-ready</strong> photo documentation</li>
            <li><strong>Every roof type:</strong> shingle, tile, metal, slate, cedar and flat</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="section alt" aria-labelledby="local-title">
      <div class="container grid-2">
        <div class="prose">
          <span class="eyebrow">Local Roofing Conditions</span>
          <h2 id="local-title">What {esc(n)} Roofs Are Up Against</h2>
          <p>{c['local']}</p>
          <h3>Common roof concerns we see in {esc(n)}</h3>
          <ul>{notes}</ul>
        </div>
        <div class="card">
          <h3>{esc(n)} Neighborhoods We Serve</h3>
          <ul class="hoods">{hoods}</ul>
          <p style="margin-top:14px">Don't see your neighborhood? We inspect roofs everywhere in {esc(n)} and throughout {esc(c['county'])}.</p>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="services-title">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Inspection Services</span>
          <h2 id="services-title">Roof Inspection Services in {esc(n)}</h2>
          <p>Our most-requested inspections in {esc(n)} — plus drone, leak detection, attic and new-roof inspections. <a href="/services/">See all inspection services</a>.</p>
        </div>
        <div class="grid-3">{services}
        </div>
      </div>
    </section>
{process_section(n)}{faq_section(faqs, f'Roof Inspection {n} FAQ')}
    <section class="section alt" aria-labelledby="nearby-title">
      <div class="container">
        <div class="section-head">
          <h2 id="nearby-title">Roof Inspections Near {esc(n)}</h2>
          <p>We also serve nearby communities across the Denver metro. <a href="/service-areas/">See all service areas</a>.</p>
        </div>
        <ul class="areas areas-links">
{city_link_list(nearby, "Roof Inspection ")}
        </ul>
      </div>
    </section>
{cta_band(n)}"""
    return head(title, meta, url, graph) + header() + body + page_end()


# ---------------------------------------------------------------- hub pages

def services_hub():
    url = "/services/"
    trail = [("Home", "/"), ("Inspections", url)]
    graph = [business_node(), breadcrumbs_ld(trail), {
        "@type": "ItemList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{s['slug']}/", "name": s["name"]}
                            for i, s in enumerate(SERVICES)],
    }]
    cards = "".join(f"""
          <a class="card card-link" href="/{s['slug']}/">
            <div class="icon" aria-hidden="true">{s['icon']}</div>
            <h3>{esc(s['name'])}</h3>
            <p>{esc(s['short'])}</p>
          </a>""" for s in SERVICES)
    body = hero(trail, "Roof Inspection Services", "Roof Inspection Services in Denver",
                "From hail damage and real estate inspections to roof certifications, drone imaging and leak detection — every type of roof inspection for homes and businesses across the Denver metro.") + f"""
    <section class="section" aria-labelledby="all-title">
      <div class="container">
        <div class="section-head">
          <h2 id="all-title">Choose Your Roof Inspection</h2>
          <p>Not sure which inspection you need? Call <a href="tel:{TEL}">{PHONE}</a> and we'll point you in the right direction.</p>
        </div>
        <div class="grid-3">{cards}
        </div>
      </div>
    </section>
{process_section()}{cta_band()}"""
    return head("Roof Inspection Services Denver | Hail, Real Estate & More",
                "Every type of roof inspection in the Denver metro: residential, hail damage, storm, real estate, roof certification, insurance, commercial, drone and leak detection. 4.9★ from 370 reviews.",
                url, graph) + header() + body + page_end()


def areas_hub():
    url = "/service-areas/"
    trail = [("Home", "/"), ("Service Areas", url)]
    graph = [business_node(), breadcrumbs_ld(trail), {
        "@type": "ItemList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + city_url(c), "name": f"Roof Inspection {c['name']}, CO"}
                            for i, c in enumerate(CITIES)],
    }]
    cards = "".join(f"""
          <a class="card card-link" href="{city_url(c)}">
            <h3>Roof Inspection {esc(c['name'])}</h3>
            <p>{esc(c['county'])}</p>
          </a>""" for c in sorted(CITIES, key=lambda c: c["name"]))
    body = hero(trail, "Service Areas", "Roof Inspections Across the Greater Denver Metro",
                "Based in Denver, we inspect roofs in every city and community across Denver, Adams, Arapahoe, Jefferson, Douglas, Broomfield and Boulder counties.") + f"""
    <section class="section" aria-labelledby="cities-title">
      <div class="container">
        <div class="section-head">
          <h2 id="cities-title">Cities We Serve</h2>
          <p>Select your city for local roofing conditions, neighborhoods and FAQs. If you're anywhere in the Denver metro and don't see your community, <a href="#book">just ask</a> — we serve it.</p>
        </div>
        <div class="grid-4">{cards}
        </div>
      </div>
    </section>
{cta_band()}"""
    return head("Roof Inspection Service Areas | Denver Metro Cities We Serve",
                "Roof Inspection Denver serves 30+ cities across the Denver metro, including Aurora, Lakewood, Arvada, Westminster, Centennial, Highlands Ranch, Boulder and more. 4.9★ from 370 reviews.",
                url, graph) + header() + body + page_end()


# ---------------------------------------------------------------- homepage + sitemap

def update_homepage():
    p = os.path.join(ROOT, "index.html")
    s = open(p).read()
    s = re.sub(r"<!-- HEADER:START -->.*?<!-- HEADER:END -->", lambda m: header(), s, flags=re.S)
    s = re.sub(r"<!-- FOOTER:START -->.*?<!-- FOOTER:END -->", lambda m: footer(), s, flags=re.S)
    # homepage nav anchors stay on-page for sections that live here
    s = s.replace('<a href="/#reviews">', '<a href="#reviews">').replace('<a href="/#faq">', '<a href="#faq">')
    # link service cards: <h3>Name</h3> inside cards -> linked heading
    names = {
        "Residential Roof Inspections": "residential-roof-inspection",
        "Hail Damage Roof Inspections": "hail-damage-roof-inspection",
        "Storm &amp; Wind Damage Inspections": "storm-damage-roof-inspection",
        "Real Estate Roof Inspections": "real-estate-roof-inspection",
        "Roof Certifications": "roof-certification",
        "Insurance Claim Inspections": "insurance-claim-roof-inspection",
        "Commercial Roof Inspections": "commercial-roof-inspection",
        "Drone Roof Inspections": "drone-roof-inspection",
        "Infrared &amp; Leak Detection": "infrared-roof-inspection",
        "Annual Maintenance Inspections": "annual-roof-maintenance-inspection",
        "New Roof &amp; Warranty Inspections": "new-roof-warranty-inspection",
        "Attic &amp; Ventilation Inspections": "attic-ventilation-inspection",
    }
    for label, slug in names.items():
        s = s.replace(f"<h3>{label}</h3>", f'<h3><a href="/{slug}/">{label}</a></h3>')
    # link service-area list items
    for c in PAGE_CITIES:
        s = s.replace(f"<li>{c['name']}</li>", f'<li><a href="{city_url(c)}">{c["name"]}</a></li>')
    s = s.replace('<ul class="areas">', '<ul class="areas areas-links">')
    open(p, "w").write(s)


def sitemap(urls):
    body = "\n".join(f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n  </url>" for u in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')


def main():
    urls = ["/", "/services/", "/service-areas/"]
    write("services", services_hub())
    write("service-areas", areas_hub())
    for s in SERVICES:
        write(s["slug"], service_page(s))
        urls.append(f"/{s['slug']}/")
    for c in PAGE_CITIES:
        write(c["slug"], city_page(c))
        urls.append(f"/{c['slug']}/")
    update_homepage()
    sitemap(urls)
    print(f"Generated {len(SERVICES)} service pages, {len(PAGE_CITIES)} city pages, 2 hubs; sitemap has {len(urls)} URLs.")


if __name__ == "__main__":
    main()
