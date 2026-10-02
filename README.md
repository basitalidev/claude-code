# roofinspectiondenver.com

Static website for **Roof Inspection Denver**, a roof inspection company serving the greater Denver metro area. It has no build step and no dependencies. Upload the folder to any static host (Netlify, Cloudflare Pages, Vercel, GitHub Pages, or shared hosting).

## Files
| Path | Purpose |
|---|---|
| `index.html`, `services/`, `service-areas/`, `<service-slug>/`, `roof-inspection-<city>/`, `thank-you.html`, `privacy.html`, `404.html` | **Generated** pages; don't edit by hand |
| `assets/styles.css` | Design system (self-hosted Inter + Plus Jakarta Sans fonts in `assets/fonts/`) |
| `assets/img/` | Photos as responsive WebP (`<slot>-800.webp`, `<slot>-1600.webp`) |
| `build/generate.py` | Templates; builds every page and `sitemap.xml` |
| `build/services_data.py`, `build/cities_data.py`, `build/home_data.py` | Page copy and FAQs |
| `build/site_images.py` | Image slots: alt text and what each photo should show |
| `build/images.py` | Image pipeline: placeholders and photo import |
| `build/icons/` | Lucide SVG icons (ISC license) |

## Editing the site
1. Edit copy in `build/*_data.py`, or layout in `build/generate.py`.
2. Run `python3 build/generate.py` from the repo root. It rebuilds every page and the sitemap.

## Photos
Every image slot is listed in `build/site_images.py`. Slots without a photo show a navy placeholder. To add a photo (requires `pip install pillow`):

```
python3 build/images.py add hero ~/Downloads/inspector-on-roof.jpg
python3 build/generate.py
```

The script crops the photo to 3:2 and writes optimized 800px and 1600px WebP files. Use photos you own (your own job photos are best for trust and local SEO) or ones licensed for commercial use, such as Unsplash.

There is intentionally **no** `/roof-inspection-denver/` page. The homepage targets "roof inspection Denver", and a second Denver page would compete with it. Denver links point to `/`.

## SEO built in
- Primary keyword "roof inspection Denver" appears in the title, H1, meta description, first paragraph, H2s, and FAQ title.
- Semantic/NLP coverage: hail damage, storm/wind, real estate, roof certification, insurance claim, Class 4 shingles, ice dams, Front Range, Hail Alley, metro cities, counties, and Denver neighborhoods.
- One H1 per page, H2 per section, H3 for sub-topics. FAQ questions are H3, or H4 under the homepage's H3 FAQ groups.
- Every image has descriptive alt text. Images are responsive WebP with explicit dimensions and lazy loading below the fold, and the hero image is preloaded for fast LCP.
- JSON-LD: `RoofingContractor`/`LocalBusiness` (areaServed, hours, services, aggregateRating), `WebSite`, `FAQPage` (generated from the on-page FAQ, so they match), and `BreadcrumbList`.
- Canonical, Open Graph, geo meta tags, robots.txt, and sitemap.xml.

## ⚠️ Before launch: replace placeholders
1. **Phone number.** `(303) 555-0142` is a placeholder. Change `PHONE`, `TEL` and the `telephone` field in `business_node()` at the top of `build/generate.py`, then regenerate.
2. **Email.** Confirm `EMAIL` in `build/generate.py`.
3. **Address and hours.** If you have a public office, add the street address and ZIP to `footer()` and to `business_node()` in `build/generate.py`. NAP (name, address, phone) must match your Google Business Profile exactly. Confirm the business hours.
4. **Testimonials.** The three review cards (`SAMPLE_REVIEWS` in `build/generate.py`) are **samples**. Replace them with real excerpts from your Google reviews, and point the "Read all reviews on Google" button at your Google Business Profile reviews URL.
5. **Form.** The form uses Netlify Forms (`data-netlify="true"`). On another host, point `action` at your form handler (Formspree, CRM webhook, etc.).
6. **Photos.** Replace the navy placeholder images (see **Photos** above).
7. Verify any claims you add (licenses, insurance, certifications, guarantees) before publishing.

## After launch
- Submit `sitemap.xml` in Google Search Console and validate schema with the Rich Results Test.
- Link the site from your Google Business Profile. Reviews and GBP signals drive most local "roof inspection Denver" map-pack rankings.
- Note: Google does not show review stars for a business's own `aggregateRating` markup on its site. The markup is still valid, but the stars come from your GBP.
- Strengthen city pages over time with genuinely local content: real reviews from customers in that city (with permission), photos of inspections you've done there, and notes on notable local storms. That content can't be faked, and it's what makes location pages rank.
