"""Image slots used across the site.

Each key maps to /assets/img/<key>-{800,1600}.webp. `alt` is the alt text
(keep it descriptive — it helps accessibility and image SEO). `query` is the
search used to source a photo (see build/images.py). `src` is filled in with
the chosen source photo URL once one has been picked and verified.
"""

IMAGES = {
    # page-level / shared
    "hero":        {"alt": "Roof inspector examining asphalt shingles on a Denver-area home", "query": "roofer inspecting roof shingles"},
    "inspector":   {"alt": "Roof inspector documenting roof condition with a tablet", "query": "roof inspection worker"},
    "shingles":    {"alt": "Close-up of architectural asphalt roof shingles", "query": "asphalt shingles close up"},
    "skyline":     {"alt": "Denver skyline with the Rocky Mountains in the background", "query": "denver skyline mountains"},
    "suburb":      {"alt": "Suburban neighborhood rooftops in the Denver metro area", "query": "suburban neighborhood rooftops aerial"},
    "mountains":   {"alt": "Colorado homes along the Front Range foothills", "query": "colorado houses mountains"},
    "house-dusk":  {"alt": "Modern home exterior and roofline at dusk", "query": "house exterior roof dusk"},
    # one per service (key = service slug)
    "residential-roof-inspection":        {"alt": "Single-family home with a pitched shingle roof", "query": "house pitched roof"},
    "hail-damage-roof-inspection":        {"alt": "Hailstones after a severe Colorado hailstorm", "query": "hail stones"},
    "storm-damage-roof-inspection":       {"alt": "Severe storm clouds building over homes", "query": "storm clouds over houses"},
    "real-estate-roof-inspection":        {"alt": "Home for sale with a well-maintained roof", "query": "house for sale"},
    "roof-certification":                 {"alt": "Inspector signing a roof certification document", "query": "signing document clipboard"},
    "insurance-claim-roof-inspection":    {"alt": "Homeowner reviewing insurance claim paperwork", "query": "insurance paperwork"},
    "commercial-roof-inspection":         {"alt": "Flat commercial roof with rooftop HVAC units", "query": "flat commercial roof"},
    "drone-roof-inspection":              {"alt": "Drone flying over a residential roof for an aerial inspection", "query": "drone flying"},
    "infrared-roof-inspection":           {"alt": "Infrared thermal imaging used to detect roof moisture", "query": "thermal camera"},
    "annual-roof-maintenance-inspection": {"alt": "Roof gutters and shingles during a maintenance inspection", "query": "roof gutter"},
    "new-roof-warranty-inspection":       {"alt": "Roofers installing new asphalt shingles", "query": "roofers installing shingles"},
    "attic-ventilation-inspection":       {"alt": "Attic framing, insulation and roof ventilation", "query": "attic insulation"},
}

# Hero images rotated across city pages
CITY_HEROES = ["suburb", "mountains", "skyline", "house-dusk", "residential-roof-inspection"]
