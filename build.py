#!/usr/bin/env python3
"""Generates the portfolio's HTML pages. Edit copy here, run `python3 build.py`."""
import html, os, json, re

OUT = os.path.dirname(os.path.abspath(__file__))
EMAIL = "jbuenvi@stanford.edu"
LINKEDIN = "https://www.linkedin.com/in/jbuenviaje"
RESUME = "https://drive.google.com/file/d/1j6kaJTfAUeaCM25LnBCSx-hFJtdSB7Q1/view?usp=sharing"

def esc(s): return html.escape(s, quote=True)

# Everything lives in ONE document (index.html) so the music player is never reloaded.
VIEWS = {}   # route -> {"title","desc","html"}
FILE_ROUTE = {"case-study-serendipi-tea.html":"serendipi-tea","case-study-simone.html":"simone","case-study-node.html":"node",
              "captured-moments.html":"moments","community.html":"community","graphic-design.html":"graphic-design"}
LINK_MAP = {"index.html":"#/","index.html#work":"#work","index.html#side-quests":"#side-quests","index.html#about":"#about",
            "case-study-serendipi-tea.html":"#/serendipi-tea","case-study-simone.html":"#/simone","case-study-node.html":"#/node",
            "captured-moments.html":"#/moments","community.html":"#/community","graphic-design.html":"#/graphic-design"}
def rewrite_links(h):
    return re.sub(r'href="([^"]+)"', lambda m: f'href="{LINK_MAP.get(m.group(1), m.group(1))}"', h)

# Hand-drawn line icons (64x64). f = soft fill, a = tinted accent fill. A shared "rough" filter wobbles the lines.
ICONS = {
"wave": '''<path class="f" d="M18 38C12 34 10 30 14 27C17 25 20 28 23 33V14C23 10 29 10 29 14V30V9C29 5 35 5 35 9V30V12C35 8 41 8 41 12V32V19C41 15 47 15 47 19V38C47 50 40 58 31 58C24 58 19 52 18 44Z"/>
<path d="M23 33V30M29 30V26M35 30V26M41 32V28" opacity=".0"/><path d="M52 12q5 4 3 10M56 6q6 6 4 15"/>''',
"book": '''<path class="f" d="M32 16C24 12 14 12 8 15V50C14 47 24 47 32 51C40 47 50 47 56 50V15C50 12 40 12 32 16Z"/>
<path d="M32 16V51"/><path d="M15 24Q21 22 26 24M15 31Q21 29 26 31M15 38Q21 36 26 38M38 24Q43 22 49 24M38 31Q43 29 49 31"/>
<path class="a" d="M44 13V29L48 25L52 29V14"/>''',
"songs": '''<path d="M24 44V17L48 11V38"/><path d="M24 25L48 19"/>
<ellipse class="a" cx="17.5" cy="45" rx="8" ry="6"/><ellipse class="a" cx="41.5" cy="39" rx="8" ry="6"/>''',
"mic": '''<rect class="a" x="23" y="8" width="18" height="30" rx="9"/><path d="M23 20H41M23 27H41"/>
<path d="M15 30C15 46 49 46 49 30"/><path d="M32 45V56M22 57H42"/>''',
"room": '''<path class="f" d="M12 31V54H52V31"/><path class="a" d="M7 32L32 9L57 32Z"/>
<rect class="f" x="26" y="38" width="12" height="16" rx="2"/><circle cx="35" cy="47" r="1.2"/><rect class="f" x="15" y="36" width="8" height="8" rx="1.5"/><rect class="f" x="41" y="36" width="8" height="8" rx="1.5"/>''',
"pokemon": '''<circle class="f" cx="32" cy="32" r="23"/><path class="a" d="M9 32A23 23 0 0 1 55 32Z"/><path d="M9 32H55"/>
<circle class="f" cx="32" cy="32" r="8"/><circle cx="32" cy="32" r="3.2"/>''',
"misc": '''<path class="a" d="M30 6C32 22 36 28 54 30C36 32 32 38 30 56C28 38 24 32 6 30C24 28 28 22 30 6Z"/>
<path class="f" d="M51 6C51.6 11 53 12.5 58 13C53 13.5 51.6 15 51 20C50.4 15 49 13.5 44 13C49 12.5 50.4 11 51 6Z"/><path class="f" d="M50 44C50.5 48 51.5 49 55.5 49.5C51.5 50 50.5 51 50 55C49.5 51 48.5 50 44.5 49.5C48.5 49 49.5 48 50 44Z"/>''',
"camera": '''<path class="f" d="M8 22H20L24 14H40L44 22H56V52H8Z"/><circle class="a" cx="32" cy="36" r="12"/><circle cx="32" cy="36" r="5"/>
<circle cx="49" cy="28" r="1.6"/><path d="M13 22V19"/>''',
"lamp": '''<path class="a" d="M20 14H44L52 32H12Z"/><path d="M32 32V50"/><path class="f" d="M20 54Q32 48 44 54Q32 59 20 54Z"/><path d="M42 32V40"/><circle cx="42" cy="42" r="2"/>
<path d="M32 4V8M10 12L13 15M54 12L51 15M4 26L8 26M60 26L56 26"/>''',
"car": '''<path class="a" d="M5 43V36Q5 32 9 31L16 21Q18 18 22 18H41Q45 18 48 21L55 31Q59 32 59 36V43Z"/>
<path class="f" d="M18 31L23 22H31V31ZM35 31V22H40L46 31Z"/><circle class="f" cx="18" cy="45" r="7"/><circle class="f" cx="46" cy="45" r="7"/><circle cx="18" cy="45" r="1.8"/><circle cx="46" cy="45" r="1.8"/>''',
"shirt": '''<path class="a" d="M22 9L7 18L13 31L20 27V55H44V27L51 31L57 18L42 9Q32 19 22 9Z"/><path d="M22 9Q32 19 42 9"/><path d="M20 45H44" opacity=".5"/>''',
"pencil": '''<g transform="rotate(40 32 32)"><rect class="a" x="24" y="5" width="16" height="38" rx="2"/><path class="f" d="M24 43L32 58L40 43Z"/><path d="M24 14H40"/><path d="M24 11V8" opacity="0"/><path d="M29 52L32 58L35 52"/></g>
<path d="M8 56Q14 52 20 56T32 56" opacity=".0"/>''',
}
FILTER = '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><filter id="rough" x="-8%" y="-8%" width="116%" height="116%"><feTurbulence type="fractalNoise" baseFrequency="0.034" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.4"/></filter></svg>'
def icon(name, cls=""):
    return f'<svg class="ico {cls}" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><g filter="url(#rough)">{ICONS[name]}</g></svg>'

# ---------------------------------------------------------------- icons
LOGO = '''<svg width="38" height="44" viewBox="0 0 44 50" fill="none" aria-hidden="true"><circle cx="13" cy="11" r="3.6" fill="currentColor"/><circle cx="30" cy="11" r="3.6" fill="currentColor"/><path d="M30 21 V35 C30 43 21 45.5 13.5 40" stroke="currentColor" stroke-width="4.6" stroke-linecap="round" fill="none"/></svg>'''
ARROW = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
MAIL = '<svg class="big mail-mark" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="12" width="52" height="40" rx="9"/><path d="m10 19 22 18 22-18"/></svg>'
DOC = '<svg class="big" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="color:var(--stamp)"><path d="M16 6h22l14 14v36a2 2 0 0 1-2 2H16a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2Z"/><path d="M38 6v14h14M22 34h20M22 44h20"/></svg>'
SUN = '<svg class="sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
MOON = '<svg class="moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5Z"/></svg>'
EXPAND = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>'
HEADPHONES = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 15V9a8 8 0 0116 0v6M4 15a2 2 0 002 2h1a1 1 0 001-1v-4a1 1 0 00-1-1H5a1 1 0 00-1 1v3zM20 15a2 2 0 01-2 2h-1a1 1 0 01-1-1v-4a1 1 0 011-1h1a1 1 0 011 1v3z"/></svg>'

# ---------------------------------------------------------------- shared chrome
HEAD_SCRIPT = """<script>(function(){var d=document.documentElement;try{var t=localStorage.getItem('jb_theme');if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';d.setAttribute('data-theme',t);d.setAttribute('data-view',localStorage.getItem('jb_view')||'tldr')}catch(e){d.setAttribute('data-theme','light');d.setAttribute('data-view','tldr')}})()</script>"""

def head(title, desc):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{HEAD_SCRIPT}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div id="page">
'''

THEME_BTN = f'<button class="chip-btn theme-btn" aria-pressed="false" data-tip="Switch between light and dark">{SUN}{MOON}<span class="txt">Light</span></button>'

AUDIO = f'''
<div class="audio" id="audioGuide">
  <div class="audio-panel" id="agPanel">
    <div class="audio-head">
      <div class="audio-tabs">
        <button class="audio-tab active" data-uri="spotify:playlist:53VFJnUIcrfUlIhhLTmUji">Josh's Top 10</button>
        <button class="audio-tab" data-uri="spotify:playlist:1d93rfrg8ZQheUn2gqzK49">Browsing</button>
      </div>
      <button class="audio-close" id="agClose" aria-label="Close player">✕</button>
    </div>
    <div class="audio-frame"><div id="agFrame"></div></div>
  </div>
  <button class="audio-toggle" id="agToggle" data-tip="Music keeps playing as you move between pages">
    <span class="dot"></span>{HEADPHONES}<span class="txt">Listen to a tune</span>
  </button>
</div>
'''

MAIL_SM = '<svg width="22" height="22" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="12" width="52" height="40" rx="9"/><path d="m10 19 22 18 22-18"/></svg>'

def site_footer():
    return f'''
<section class="closing" aria-labelledby="closingTitle-{{id}}">
  <div class="closing-card">
    <h2 id="closingTitle-{{id}}">Let's create something together!</h2>
    <div class="closing-links">
      <a class="cbtn" href="mailto:{EMAIL}" data-tip="Send me an email">{MAIL_SM}<span>{EMAIL}</span></a>
      <a class="cbtn" href="{LINKEDIN}" target="_blank" rel="noopener" data-tip="Let's connect on LinkedIn"><b class="in" aria-hidden="true">in</b><span>LinkedIn</span></a>
    </div>
  </div>
</section>
<footer class="site-foot"><span>© 2026 Josh Buenviaje</span></footer>
'''

# ---------------------------------------------------------------- home tiles
def srtip(tip): return f'<span class="sr-only">{esc(tip)}</span>'

def tile(cls, inn, body, tip, tag="article", href=None, extra=""):
    attrs = f'class="tile {cls}" data-in="{inn}" data-tip="{esc(tip)}"'
    if href:
        tg = "a"; attrs += f' href="{href}"' + (' target="_blank" rel="noopener"' if href.startswith("http") else "")
    elif tag == "button":
        tg = "button"; attrs += ' type="button"'
    else:
        tg = "article"; attrs += ' tabindex="0"'
    return f'  <{tg} {attrs} {extra}>{body}{srtip(tip)}</{tg}>\n'

def img_tile(cls, inn, href, src, alt, tag, title, desc, tip, pos="center"):
    body = f"""<img class="bg" src="{src}" alt="{esc(alt)}" style="object-position:{pos}">
    <span class="go">{ARROW}</span>
    <div class="tile-cap"><span class="tag">{tag}</span><h3>{title}</h3><p>{desc}</p></div>"""
    return tile("tile-img " + cls, inn, body, tip, href=href)

PLUS = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>'

# ---- Favorites, as ranked lists. Edit these freely: {"t": title, "n": note}.
# Items with "todo": True render as dashed placeholders until you fill them in.
def todo(n): return {"t": f"Your #{n} pick goes here", "todo": True}
LISTS = {
  "books": {"icon": icon("book"), "title": "Favorite books", "sub": "My top picks, ranked.", "items": [
    {"t": "The Little Prince", "n": "A book I reread every year. The meaning changes each time."},
    {"t": "All About Love", "n": "A great reminder from bell hooks to love intentionally, deeply, and in many different ways."},
    {"t": "A Pattern Language", "n": "Design is everywhere. From big systemic issues to the smallest of details, all of it matters."}]},
  "songs": {"icon": icon("songs"), "title": "Favorite songs", "sub": "My top picks, ranked.", "action": "Play my Top 10", "items": [
    {"t": "Dancing Queen, ABBA", "n": "My karaoke song since I was three. Some of my closest friends still call it “The Josh Song.”"},
    {"t": "Nocturne, Chopin", "n": "My favorite piece I've ever played on piano, and still one of my biggest sources of inspiration."},
    {"t": "When Fortune Smiles, Kitty Craft", "n": "A song that always brings me back to one of my best friends."}]},
  "musicians": {"icon": icon("mic"), "title": "Favorite musicians", "sub": "My top picks, ranked.", "items": [
    {"t": "Ariana Grande", "n": "Favorite song: POV"},
    {"t": "Lady Gaga", "n": "Favorite song: Just Dance"},
    {"t": "Bruno Mars", "n": "Favorite song: Skate"}]},
  "room": {"icon": icon("room"), "title": "Favorite things in my room", "sub": "My top picks, ranked.", "items": [
    {"t": "Wall of Pokémon cards", "n": "I've loved Pokémon since I was nine, and I'm glad the collection finally found a use."},
    {"t": "Crochet from my sister", "n": "A shoutout to my incredibly talented sister and best friend."},
    {"t": "Lots and lots of photos", "n": "Capturing moments is one of my favorite pastimes. I love getting to look back."}]},
  "pokemon": {"icon": icon("pokemon"), "title": "Favorite Pokémon", "sub": "I've loved Pokémon since I was nine.", "items": [
    {"t": "Oshawott", "n": "My first ever starter. Named him “Joshawott.”"},
    {"t": "Leavanny", "n": "While I'm not a big fan of bug types… I have a special place in my heart for this weaver."},
    {"t": "Gengar", "n": "Just a cool guy."}]},
  "misc": {"icon": icon("misc"), "title": "Miscellaneous favorites", "sub": "Everything else that earned a spot on the shelf.", "items": [
    {"t": "Studio Ghibli", "n": "Some of the most beautiful animation I've ever seen. Whisper of the Heart is my favorite."},
    {"t": "Spotify Playlist Curation", "n": "I have a playlist for almost every given situation; it’s also such an incredible gift to give to a friend."},
    {"t": "Thrifting", "n": "It’s hard to find a piece in my closet that isn’t thrifted anymore."}]},
}

def list_tile(inn, tint, key, tip):
    d = LISTS[key]
    return tile(f"tile-list {tint}", inn, f'<span class="lt-icon" aria-hidden="true">{d["icon"]}</span><h3>{d["title"]}</h3><span class="lt-plus">{PLUS}</span>',
                tip, tag="button", extra=f'data-list="{key}"')

def fact(tint, icon, title, text, tip, cls="", gallery=None):
    plus = f'<span class="lt-plus">{PLUS}</span>' if gallery else ""
    body = f'<span class="lt-icon" aria-hidden="true">{icon}</span><div><h3>{title}</h3><p>{text}</p></div>{plus}'
    if gallery:
        return tile(f"tile-fact {tint} {cls}", "about", body, tip, tag="button", extra=f'data-gallery="{gallery}"')
    return tile(f"tile-fact {tint} {cls}", "about", body, tip)

# ---- Photo galleries that open from the About fact tiles.
# Road trip photos, in route order. Add a line per photo (file lives in img/roadtrip/).
ROADTRIP = [
  ("maryland.jpg", "Maryland", "A harbor in Maryland with boats, a dock, and two ducks in the water"),
  ("washington-dc.jpg", "Washington, DC", "The U.S. Capitol dome seen through bare trees"),
  ("bristol.jpg", "Bristol", "The glowing Bristol, VA and TENN sign arching over the street"),
  ("nashville.jpg", "Nashville", "Two pairs of cowboy boots on a Buy One Pair Get Two Pair Free boot shop rug"),
  ("arizona.jpg", "Arizona", "A narrow aisle of bright red bookshelves in a bookstore"),
  ("grand-canyon.jpg", "Grand Canyon", "Layers of canyon cliffs under a wide blue sky"),
  ("las-vegas.jpg", "Las Vegas", "The Bellagio fountains in the sunset glow beside the Cosmopolitan"),
  ("santa-cruz.jpg", "Santa Cruz", "A backyard pool with a pink inflatable balloon dog and colorful towels drying"),
]
def roadtrip_items():
    d = os.path.join(OUT, "img", "roadtrip")
    return [{"src": "img/roadtrip/" + f, "alt": alt, "cap": cap} for f, cap, alt in ROADTRIP if os.path.exists(os.path.join(d, f))]

GALLERIES = {
  "shirt": {"title": "My favorite shirt", "sub": "A gift from my mom to my dad. They let me take it to college with me.", "items": [
    {"src": "img/about/shirt-little.jpg", "alt": "Josh as a little kid at the beach, wearing an oversized gray t-shirt with a cartoon cart on it", "cap": "Little me"},
    {"src": "img/about/shirt-now.jpg", "alt": "Josh standing in the ocean waves wearing the same gray t-shirt", "cap": "Me, wearing it now"}]},
  "roadtrip": {"title": "Maryland to Stanford", "sub": "A few of my favorite pictures from the drive.", "items": roadtrip_items()},
}

# ---- Graphic design pieces. Add one dict per piece (file lives in img/graphic-design/). Order here = order on the page.
GRAPHICS = [
  {"file": "west-flo-postcard.jpg", "title": "Greetings from West Flo"},
  {"file": "newly-declared.jpg", "title": "Newly d.clared"},
  {"file": "toulouvre-ra.jpg", "title": "TouLouvre RA"},
  {"file": "pumpkin-carving.jpg", "title": "Pumpkin Carving"},
  {"file": "trick-or-treating.jpg", "title": "Trick or Treating"},
  {"file": "aasib-2024-25.jpg", "title": "AASib 2024-25"},
]
def graphics():
    return [g for g in GRAPHICS if os.path.exists(os.path.join(OUT, "img", "graphic-design", g["file"]))]

# ---- Community: add events here. {"title", "when", "desc", "img" (optional, e.g. "img/community/x.jpg")}
EVENTS = []

GALLERY_DIALOG = """
<dialog class="sheet gallery" id="gallery" aria-labelledby="galTitle">
  <div class="sheet-in">
    <button class="sheet-x" type="button" aria-label="Close" id="galX">✕</button>
    <h2 id="galTitle"></h2>
    <p class="sheet-sub" id="galSub"></p>
    <div class="g-grid" id="galGrid"></div>
  </div>
</dialog>
"""

SHEET = """
<dialog class="sheet" id="sheet" aria-labelledby="sheetTitle">
  <div class="sheet-in">
    <button class="sheet-x" type="button" aria-label="Close" id="sheetX">✕</button>
    <div class="sheet-icon" id="sheetIcon" aria-hidden="true"></div>
    <h2 id="sheetTitle"></h2>
    <p class="sheet-sub" id="sheetSub"></p>
    <ol class="rank" id="sheetList"></ol>
    <button class="sheet-act" type="button" id="sheetAct" hidden></button>
  </div>
</dialog>
"""

HOME_TITLE = "Josh Buenviaje | Design portfolio"
HOME_DESC = "Josh Buenviaje is a senior at Stanford studying Design. Case studies in research-led product and experience design, plus side quests."

def build_home():
    t = []
    gfx = graphics()
    t.append(tile("intro w3 h2", "all about", f"""
    <div class="portrait"><img src="img/about/josh-about.jpg" alt="Josh Buenviaje"></div>
    <div class="intro-copy">
      <h1 class="hello-big">Hey, I'm Josh</h1>
      <p class="hello-sub">A senior at Stanford studying Design, creating experiences around community, culture, and connection.</p>
      <p class="where">Originally from San Diego, CA</p>
      <span class="more">Learn more about me {ARROW}</span>
    </div>""",
      "Learn more about me", href="#about"))
    t.append(tile("tile-img h2 grew", "about", """<img class="bg" src="img/photography/frame-09.jpg" alt="Balboa Park, San Diego" style="object-position:center 40%">
    <div class="tile-cap"><span class="tag">Where I grew up</span><h3>San Diego, CA</h3><p>About twenty minutes from the Mexico border.</p></div>""",
      "Free Museum Tuesdays at Balboa Park were a childhood staple."))
    t.append(tile("tile-icon", "all", f'{MAIL}<span class="label">Email</span><span class="go">{ARROW}</span>',
      f"{EMAIL}. I'd love to hear from you.", href=f"mailto:{EMAIL}"))
    t.append(tile("tile-icon", "all", f'<span class="linkedin-mark" aria-hidden="true">in</span><span class="label">LinkedIn</span><span class="go">{ARROW}</span>',
      "linkedin.com/in/jbuenviaje", href=LINKEDIN))

    # work
    t.append(img_tile("w2 h2", "all work", "case-study-serendipi-tea.html", "img/serendipi-tea/cover.jpg", "Serendipi-Tea conversation cards on a table",
      "Experiential design", "Serendipi-Tea", "A card game that gets startup founders talking.",
      "A card game that got startup founders to stop pitching and start talking."))
    t.append(img_tile("h2", "all work", "case-study-simone.html", "img/simone/cover.jpg", "Green quilted handbag from Simone Acc. Collection",
      "Product design", "Simone Acc. Collection", "Handbag concepts in South Korea.",
      "Eight weeks in Ui-Wang, South Korea designing handbags, then making samples for a Tory Burch sales team.", pos="center 30%"))
    t.append(img_tile("", "all work", "case-study-node.html", "img/node/cover.jpg", "Visitors viewing a wall of digital art at Node Foundation",
      "Guest experience", "Node Foundation", "",
      "I help people feel at home with digital and on-chain art, often for the first time."))
    t.append(tile("tile-icon", "all work", f'{DOC}<span class="label">Résumé</span><span class="go">{ARROW}</span>',
      "Check out my résumé!", href=RESUME))

    # side quests
    frames = ["frame-01", "frame-04", "frame-03", "frame-09"]
    ph = "".join(f'<div class="ph"><img src="img/photography/{f}.jpg" alt="" loading="lazy"></div>' for f in frames)
    t.append(tile("tile-collage w2 h2", "all side", f'{ph}<div class="cap"><h3>Captured Moments</h3><p>12 frames, 12 stories</p></div><span class="go">{ARROW}</span>',
      "12 photos from a Kodak PixPro, each with the story on the back. Click one to flip it.", href="captured-moments.html"))
    t.append(tile("tile-play", "all side", """<div class="eq" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
    <div><h3>Press play</h3><p>Two playlists, curated by me</p></div>""",
      "The music keeps going as you click around the site.", tag="button", extra='id="playTile"'))
    if gfx:
        pick = [g["file"] for g in gfx[:4]]
        mos = "".join(f'<div class="ph"><img src="img/graphic-design/{f}" alt="" loading="lazy"></div>' for f in pick)
        t.append(tile("tile-collage sm", "all side", f'{mos}<div class="cap"><h3>Graphic design</h3></div><span class="go">{ARROW}</span>',
          "Posters and graphics I've made for events and communities at Stanford.", href="graphic-design.html"))
    else:
        t.append(tile("tile-type gfx", "all side", '<h3>Graphic design</h3>', "A few of my graphic design pieces."))
    t.append(img_tile("w2", "all side", "community.html", "img/community/nso-checkin.jpg",
      "Josh and a team of RAs dressed as airline pilots, smiling behind a red check-in table", "Side quest", "Weaver of community",
      "I attempt to create communities and spaces where people feel comfortable and seen.",
      "Community is my favorite thing to design. Click to see how.", pos="center 64%"))

    # about: favorites as ranked lists (first four also show on All)
    t.append(list_tile("all about", "tint-a", "books", "Click for my favorite books, ranked"))
    t.append(list_tile("all about", "tint-e", "songs", "Click for my favorite songs, ranked"))
    t.append(list_tile("all about", "tint-c", "pokemon", "Click for my favorite Pokémon, ranked"))
    t.append(tile("tile-list tint-f", "all about", f'<span class="lt-icon" aria-hidden="true">{icon("camera")}</span><h3>Favorite photos</h3><span class="lt-plus">{ARROW}</span>',
      "My favorites live in my digicam archive. Each one has a story.", href="captured-moments.html"))
    t.append(list_tile("about", "tint-d", "musicians", "Click for my favorite musicians, ranked"))
    t.append(list_tile("about", "tint-b", "room", "Click for my favorite things in my room, ranked"))
    t.append(list_tile("about", "tint-a", "misc", "Click for everything else I love"))
    t.append(fact("tint-e", icon("lamp"), "I love warm lighting", "I have 4 lamps in my room.",
      "All four are incredibly different."))
    rt = bool(GALLERIES["roadtrip"]["items"])
    t.append(fact("tint-d", icon("car"), "Maryland to Stanford, by road", "For Spring Break 2026, I drove cross-country to get back to campus.",
      "My last stop before campus was Santa Cruz, to visit my best friend." + (" Click for some of my favorite pictures." if rt else ""), "w2", gallery="roadtrip" if rt else None))
    t.append(fact("tint-c", icon("shirt"), "My favorite shirt", "It's a gift from my father.",
      "The shirt was actually a gift from my mom to my dad... but they ultimately let me take it to college with me! Click to see it then and now.", gallery="shirt"))
    t.append(fact("tint-b", icon("pencil"), "Project-based kid", "I went to a project-based learning school.",
      "Shoutout High Tech High. It changed how I think."))

    page = f'''
<header class="topbar">
  <a class="logo" href="index.html" aria-label="Josh Buenviaje, back to the top of the home page">{LOGO}</a>
  <div class="pill-group" role="tablist" aria-label="Filter the portfolio">
    <button class="pill-btn" role="tab" data-tab="all" aria-selected="true" aria-controls="bento">All</button>
    <button class="pill-btn" role="tab" data-tab="about" aria-selected="false" aria-controls="bento">About</button>
    <button class="pill-btn" role="tab" data-tab="work" aria-selected="false" aria-controls="bento">Work</button>
    <button class="pill-btn" role="tab" data-tab="side-quests" aria-selected="false" aria-controls="bento">Side Quests</button>
  </div>
  <div class="topbar-right">
    <a class="chip-btn resume" href="{RESUME}" target="_blank" rel="noopener" data-tip="Check out my résumé!">Résumé</a>
    {THEME_BTN}
  </div>
</header>
<main class="bento-wrap">
<div class="bento" id="bento" role="tabpanel">
{"".join(t)}</div>
</main>
{SHEET}{GALLERY_DIALOG}<script type="application/json" id="listData">{json.dumps(LISTS, ensure_ascii=False)}</script>
<script type="application/json" id="galleryData">{json.dumps(GALLERIES, ensure_ascii=False)}</script>
'''
    VIEWS["home"] = {"title": HOME_TITLE, "desc": HOME_DESC, "html": page + site_footer()}

def build_community():
    C = "img/community/"
    stats = '<div class="grid g3">' + "".join(
        f'<div class="stat"><b>{n}</b><span>{t}</span></div>' for n, t in [
            ("100+", "freshmen paired by shared interests"),
            ("2", "freshmen I got to mentor in the sibling program I piloted"),
            ("1", "new d.school tradition, Newly d.Clared")]) + '</div>'

    hero = fig(C + "nso-checkin.jpg", "Josh and a team of RAs dressed as airline pilots, with sunglasses and pilot hats, smiling behind a red check-in table with balloons", "hero-fig", "Welcoming new students at check-in").replace("<img ", '<img style="object-position:center 38%" ', 1)
    intro = panel("Woven, not accidental", f"""<p class="lead">Community isn't something that just happens. It gets woven, one small invitation at a time.</p>
<p class="muted" style="margin-top:18px">I attempt to create communities and spaces where people feel comfortable and seen. Here's how that's played out in the dorms and at the d.school.</p>
<div style="margin-top:28px">{stats}</div>""")

    ra = panel("In the dorms", f"""<div class="split top"><div class="stack">
<span class="kicker">Resident Assistant, Florence Moore Hall and Toussaint Louverture House</span>
<p>As an RA, I spearheaded multiple dorm programming events to bring people together. Two of my favorites:</p>
{sc("Frosh Plates", "I paired over 100 freshmen based on shared interests to spark meaningful connections within our community.")}
{sc("A sibling mentorship program", "I piloted a sibling mentorship program, and I got to be a mentor myself to two incredible freshmen!")}
{fig(C + "lounge.jpg", "A packed residence hall lounge, with students gathered on couches and chairs around a TV", "", "A packed lounge", "aspect-ratio:4/3;margin-top:6px")}
</div><div class="photo-stack">
{fig(C + "big-signs.jpg", "Three students holding playful big-sibling signs in a hallway", "", "Big sibling signs", "aspect-ratio:3/4")}
</div></div>""", step="1")

    ds = panel("At the d.school", f"""<div class="split top"><div class="stack">
<span class="kicker">Peer Advisor and Community Lead, Stanford d.school</span>
<p>I created a new declaration event called <b>Newly d.Clared</b> to celebrate the milestone of declaring the design major. The d.school now uses it as a tradition.</p>
<p>I also help with class exhibitions and design programming, so students' work has a place to be seen and gathered around.</p>
{fig(C + "exhibition.jpg", "Students and faculty gathered around project posters at a d.school class exhibition", "", "A class exhibition at the d.school", "aspect-ratio:4/3;margin-top:6px")}
</div><div class="photo-stack">
{fig("img/graphic-design/newly-declared.jpg", "The Newly d.Clared poster for the UG Design declaration event at the d.school atrium", "", "The poster I designed for Newly d.Clared", "aspect-ratio:1390/1800")}
<div class="callout" style="margin-top:6px">Every community has moments worth marking. I like building the room for them.</div>
</div></div>""", step="2")

    rules = '<div class="grid g2">' + "".join(sc(h, p) for h, p in [
        ("Start from what people already love", "Frosh Plates worked because it began with interests. People connect faster when there is already something to talk about."),
        ("Pair people across experience", "A sibling program gives new students someone a step ahead, and gives mentors the chance to grow too."),
        ("Celebrate the milestones", "Declaring a major is a big moment. Newly d.Clared makes sure nobody passes through it alone."),
        ("Make the work visible, then gather around it", "Exhibitions turn a quarter of private effort into something a whole community can stand around and talk about.")]) + '</div>'
    weave = panel("How I weave", rules, step="3")

    why = panel("Why design around community?", """<p class="lead">If we want people to feel seen, we have to design for it on purpose.</p>
<p style="margin-top:20px">Almost everything we design lands in a group of people: a dorm, a classroom, an accelerator, a gallery. Nobody uses those spaces alone. They use them with and through each other.</p>
<p>Left to chance, spaces quietly teach us how to behave. At StartX, I watched a room teach founders to pitch instead of connect. In the dorms and at the d.school, I've seen the opposite: one small, intentional invitation can teach people that they belong.</p>
<p>That's why I design for community first. The best products, programs, and places aren't just usable. They make room for people to meet each other.</p>""", cls="accent")

    ev = ""
    if EVENTS:
        items = ""
        for e in EVENTS:
            im = f'<img src="{e["img"]}" alt="{esc(e["title"])}" loading="lazy" style="aspect-ratio:4/3;width:100%;object-fit:cover;border-radius:16px;margin-bottom:14px">' if e.get("img") else ""
            items += f'<div class="sub-card">{im}<span class="kicker">{esc(e.get("when",""))}</span><h4>{esc(e["title"])}</h4><p>{esc(e.get("desc",""))}</p></div>'
        ev = panel("More events I've hosted", f'<div class="grid g2">{items}</div>')
    body = intro + ra + ds + weave + ev + why
    cs_page("community.html", "Weaver of community",
      "As an RA, a Design Program peer advisor, and a lover of people, I attempt to create communities and spaces where people feel comfortable and seen.",
      [], hero, body, ("index.html#side-quests", "Back to the side quests"),
      "How Josh Buenviaje builds community as an RA and a peer advisor and community lead at the d.school.", show_toggle=False, back=("index.html#side-quests", "Side quests"))

def build_graphics():
    gfx = graphics()
    if not gfx: return
    cards = ""
    for g in gfx:
        src = "img/graphic-design/" + g["file"]
        cards += f'''<button type="button" class="gfx-card" data-zoom="{src}" data-alt="{esc(g["title"])}" data-tip="Click to view full size">
<span class="im"><img src="{src}" alt="{esc(g["title"])}" loading="lazy"></span>
<span class="cap"><h3>{esc(g["title"])}</h3></span></button>'''
    body = f'<div class="gfx">{cards}</div>'
    cs_page("graphic-design.html", "Graphic design", "Posters and graphics I've made for events and communities at Stanford.", [], "", body,
      ("index.html#side-quests", "Back to the side quests"), "Graphic design pieces by Josh Buenviaje: posters, postcards, and event graphics.",
      show_toggle=False, back=("index.html#side-quests", "Side quests"))


# ---------------------------------------------------------------- case study helpers
def car(imgs, ar="4/3", cls="", alt="Slide", contain=False):
    """imgs: list of (src, alt) tuples."""
    cc = " contain" if contain else ""
    im = "".join(f'<img class="{"on" if i == 0 else ""}{cc}" src="{s}" alt="{esc(a)}" loading="lazy">' for i, (s, a) in enumerate(imgs))
    return f'''<div class="car {cls}" tabindex="0" aria-label="Image carousel, use arrow keys"><div class="frame" style="--ar:{ar}">{im}</div>
<div class="ctrl"><button data-prev aria-label="Previous image">←</button><span class="n"><span data-cur>01</span> / <span data-tot>{len(imgs):02d}</span></span><button data-next aria-label="Next image">→</button></div></div>'''

def fig(src, alt, cls="", cap=None, style=""):
    c = f"<figcaption>{cap}</figcaption>" if cap else ""
    return f'<figure class="fig {cls}" style="{style}"><img src="{src}" alt="{esc(alt)}" loading="lazy">{c}</figure>'

def panel(title, body, step=None, cls="", pid=None, v=None):
    st = f'<span class="step">{step}</span>' if step else ""
    idattr = f' id="{pid}"' if pid else ""
    vattr = f' data-v="{v}"' if v else ""
    return f'<section class="panel {cls}"{idattr}{vattr}><div class="panel-head">{st}<h2>{title}</h2></div>{body}</section>\n'

def sc(h, p, kicker=None):
    k = f'<span class="kicker">{kicker}</span>' if kicker else ""
    return f'<div class="sub-card">{k}<h4>{h}</h4><p>{p}</p></div>'

def tldr_cards(cards):
    out = ""
    for kicker, text, hl in cards:
        out += f'<div class="tldr-card{" hl" if hl else ""}"><span class="kicker">{kicker}</span><p>{text}</p></div>'
    return f'<div class="tldr-grid" data-v="tldr">{out}</div>\n'

def more_btn():
    return '<div class="more-hint" data-v="tldr"><button type="button" data-go-detail data-tip="Switches to the full process, with every photo">Read the full case study</button></div>\n'

def cs_page(fname, title, sub, meta, hero, body, nxt, desc, show_toggle=True, back=("index.html#work", "Work")):
    m = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in meta)
    toggle = ''
    if show_toggle:
        toggle = '''<div class="pill-group" role="group" aria-label="Case study length">
    <button class="pill-btn" data-view-btn="tldr" aria-pressed="true" data-tip="The 30-second version">TL;DR</button>
    <button class="pill-btn" data-view-btn="detail" aria-pressed="false" data-tip="The full process, with every photo">Detailed</button>
  </div>'''
    else:
        toggle = '<span></span>'
    page = f'''
<header class="topbar">
  <div style="display:flex;align-items:center;gap:14px">
    <a class="logo" href="index.html" aria-label="Josh Buenviaje, back to the top of the home page">{LOGO}</a>
    <a class="chip-btn" href="{back[0]}" data-tip="Back to the home page"><span aria-hidden="true">←</span><span class="txt">{back[1]}</span></a>
  </div>
  {toggle}
  <div class="topbar-right">{THEME_BTN}</div>
</header>
<main class="cs">
<section class="cs-title">
  <h1>{title}</h1>
  <p class="sub">{sub}</p>
  {f'<dl class="meta">{m}</dl>' if meta else ''}
</section>
{hero}
{body}
<a class="next" href="{nxt[0]}"><div><small>Up next</small><h3>{nxt[1]}</h3></div><span class="go">{ARROW}</span></a>
</main>
'''
    VIEWS[FILE_ROUTE[fname]] = {"title": f"{title} | Josh Buenviaje", "desc": desc, "html": page + site_footer()}

# ---------------------------------------------------------------- Serendipi-Tea
# ---------------------------------------------------------------- research helpers
def glance(stats, chips):
    st = "".join(f'<div class="stat"><b>{n}</b><span>{t}</span></div>' for n, t in stats)
    ch = "".join(f'<span class="chip">{c}</span>' for c in chips)
    return panel("Research at a glance", f'<div class="glance-stats">{st}</div><div class="chips">{ch}</div>')

def trace(title, head, rows, intro=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    p = f'<p class="muted" style="margin-bottom:20px">{intro}</p>' if intro else ""
    return panel(title, f'{p}<div class="trace-wrap"><table class="trace"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>', v="detail")

def ifagain(items):
    cards = "".join(sc(h, p, k) for k, h, p in items)
    return panel("If I ran this again", f'<p class="muted" style="margin-bottom:22px">Looking back, here is how I would make the research more measurable.</p><div class="grid g2">{cards}</div>', v="detail")

def build_serendipi():
    S = "img/serendipi-tea/"
    hero = fig(S + "hero.jpg", "Serendipi-Tea conversation cards spread across a table", "hero-fig")
    b = ""
    # TL;DR
    b += glance([("17", "people reached"), ("6", "needfinding interviews"), ("4", "founder segments"), ("3", "prototypes tested"), ("35–45", "min playtest sessions")],
      ["Needfinding interviews", "Segmentation", "POV synthesis", "Rapid prototyping", "Concept testing", "Observational playtests"])
    b += tldr_cards([
        ("The problem", "At StartX, nearly every conversation between founders feels like a pitch. Real, lasting connection gets pushed to the back burner.", False),
        ("What I did", "As Head User Researcher on a team of three, I led needfinding (17 people reached, 6 interviews), and we prototyped three ideas before choosing one.", False),
        ("What we built", "A cozy third space at StartX with a connection wall, snacks, and a card game called We're All Humans.", True),
        ("What happened", "Playtimes ran 35 to 45 minutes. Founders talked about love, death, politics, and insecurities, and laughed, reflected, and surprised each other.", False),
    ])
    b += '<div data-v="tldr">' + fig(S + "final-solution.jpg", "Final Serendipi-Tea installation at StartX", "hero-fig") + '</div>\n'
    b += '''<section class="panel accent" data-v="tldr"><p class="lead">Founders don't necessarily need more networking spaces. They need spaces that are explicitly not that.</p></section>\n'''
    b += '''<div class="video-card" data-v="tldr"><video controls preload="none" poster="img/serendipi-tea/final-solution.jpg"><source src="videos/serendipi-tea-recap.mp4" type="video/mp4">Your browser doesn't support embedded video. <a href="videos/serendipi-tea-recap.mp4">Download the recap.</a></video></div>\n'''
    b += more_btn()

    # Detailed
    b += panel("Project overview", '''<p class="lead">A card-based conversation tool built through a human-centered design process, prototyped and tested with founders across the StartX accelerator community.</p>
<p class="muted" style="margin-top:18px">Built with Team Jello (a team of 3) as part of Design 121 at Stanford's d.school, in partnership with StartX. I led the project as Head User Researcher.</p>''', v="detail")
    b += panel("The challenge", '''<p class="lead">How might we use the human-centered design process to design an innovation hub for the next generation of startup founders at Stanford Research Park?</p>''', cls="accent", v="detail")

    b += panel("Needfinding", '''<div class="grid g3">
<div class="stat"><b>17</b><span>People reached</span></div>
<div class="stat"><b>6</b><span>Interviews conducted</span></div>
<div class="stat"><b>4</b><span>Founder segments</span></div></div>
<div class="callout">Key takeaway: lots of diversity, in tenure, background, and what “connection” even means to a founder.</div>''', step="1", v="detail")

    b += panel("Synthesis", '''<div class="grid g3">''' +
      sc("Seasoned founders", "Keeps up with the latest tech trends and is always looking for ways to boost productivity, typically moving between spaces to work, talk, and present his newest slide deck.", "Segment A") +
      sc("Brand new founders", "Wants more genuine talks with other founders beyond concise business chat and tool-sharing, but feels an invisible gap that keeps those conversations from happening.", "Segment B") +
      sc("Underrepresented founders", "Feels like funding is her largest barrier to entry, largely due to how she's perceived as a minority founder, but remains resilient and channels that feeling to keep pushing.", "Segment C") +
      '''</div>
<div class="panel dark" style="margin-top:20px;border-radius:var(--r-inner);padding:30px"><div class="ug"><div><span class="kicker">User group: StartX</span><h3>Brand new founders</h3><p class="hmw">How might we promote serendipitous conversations between founders?</p></div>
<p>New StartX founders who lack an environment conducive to organic, serendipitous connection with one another, making the average conversation feel transactional.</p></div></div>
<div class="quote"><div class="av">JB</div><div><small>POV statement</small><p>New members of the StartX community <b>crave</b> an environment free of artificial, network-based connection, to ensure the relationships they form through StartX programming <b>have a lasting impact.</b></p></div></div>''', step="2", v="detail")

    proto = lambda img, n, name, d: f'<div class="proto"><img src="{S}{img}" alt="{name} prototype" loading="lazy"><span class="kicker">Prototype {n}</span><h4 style="font-family:var(--font-display);font-size:1.2rem">{name}</h4><p class="muted" style="font-size:.96rem">{d}</p></div>'
    b += panel("Prototyping", f'''
<div class="block"><h3 class="sub-h">Problem framing</h3>
<div class="vs"><div class="sub-card"><p>In environments where every conversation feels like a <b>pitch</b>, genuine and authentic connection always feels like it's placed on the back burner.</p></div><div class="badge">VS</div>
<div class="sub-card"><p>StartX founders feel <b>naturally authentic</b> with each other, seamlessly connecting with other members of the community as if they were family.</p></div></div>
<div class="callout">In short: we want founders to create deeper, lasting connections.</div></div>

<div class="block"><h3 class="sub-h">Three prototypes</h3>
<div class="flow"><span class="s">Enter</span><span class="a">→</span><span class="s">Look around</span><span class="a">→</span><span class="s">Snacks</span><span class="a">→</span><span class="s">We're All Humans card game</span><span class="a">→</span><span class="s">Photo</span><span class="a">→</span><span class="s">Exit</span></div>
<div class="grid g3">{proto("prototype-quilt.jpg","01","Founder Quilt (X)","Elevates underrepresented voices by displaying local founders.")}{proto("prototype-humans.jpg","02","We're All Humans","Humanizes founders by creating space for personal discussion.")}{proto("prototype-thirdspace.jpg","03","Third Space","Creates a cozy environment inside a typically busy startup ecosystem.")}</div></div>

<div class="block"><div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><h3 class="sub-h">Insights</h3><div class="grid g2">
{sc("Third spaces deepen connection","People were willing to interact with our prototype, typically in pre-existing groups.")}
{sc("We need a wide variety of topics","When the focus is on getting personal, people get deep.")}
{sc("Smaller and cozier means intimacy","Conversations feel deeper with smaller groups of people (2 to 3).")}
{sc("Food is a way to invite people","Food transitions to being less important than an intrinsic desire to connect.")}
</div></div></div>

<div class="block"><h3 class="sub-h">Creating the cards</h3><div class="split top"><div class="stack">
<p>Our cards were heavily inspired by the game <b>We're Not Really Strangers</b>, ranging from light reflection (Seed level) to deeper conversation (Bloom level), plus questions written directly from the experiences of startup founders.</p>
<p>Cards were designed in Figma, printed on cardstock, corner-cut for a rounded feel, then sprayed with lacquer for a refined finish. We also built a custom box with a “How to Play” card.</p>
<p><a class="chip" style="display:inline-block" href="https://www.figma.com/design/it91COfADt2hqakFp3oiHu/Serendipi-tea-Print-and-Play?node-id=2284-2&amp;p=f" target="_blank" rel="noopener">View the card deck on Figma</a></p></div>
<div class="levels"><div><b><i></i>Seed</b><span>“Who was your biggest role model growing up?”</span></div><div><b><i></i>Sprout</b><span>“Who was your childhood best friend?”</span></div><div><b><i></i>Bloom</b><span>“What's something you're grieving, even if it's not obvious loss?”</span></div></div></div></div>

<div class="block"><h3 class="sub-h">Creating the experience</h3>
{car([(S+"experience-1.jpg","Cards laid out on the table"),(S+"experience-2.jpg","Founders playing the card game"),(S+"experience-3.jpg","Founders playing the card game"),(S+"experience-4.jpg","Digital camera photo from the experience")], "1/1", "mid")}
<p class="muted" style="margin:16px auto 0;text-align:center">Cards were placed at a campus cafe space with signage, and left to let the experience run on its own. A digital camera was placed within the set-up so users could document their own experience.</p></div>
''', step="3", v="detail")

    b += trace("From insight to design", ["Insight from testing", "What we saw", "How it showed up in the final"], [
      ["Third spaces deepen connection", "People engaged with our prototype, typically in pre-existing groups.", "A cozy third space at StartX with seating, lamps, and signage."],
      ["Food is a way to invite people", "Food drew people in, then faded behind the desire to connect.", "Snacks and drinks as an early step in the experience flow, before the card game."],
      ["A wide variety of topics; personal focus gets people deep", "When the prompts got personal, conversations did too.", "Three card levels, from light reflection (Seed) to deeper conversation (Bloom)."]],
      "Each design choice traces back to something we observed in testing.")
    b += panel("Final solution at StartX", f'''{fig(S+"final-solution.jpg","Final Serendipi-Tea installation at StartX","hero-fig")}
<div class="chips"><span class="chip">Connection wall</span><span class="chip">Food and drinks</span><span class="chip">We're All Humans card game</span></div>''', step="4", v="detail")

    b += '''<div class="video-card" data-v="detail"><video controls preload="none" poster="img/serendipi-tea/final-solution.jpg"><source src="videos/serendipi-tea-recap.mp4" type="video/mp4">Your browser doesn't support embedded video. <a href="videos/serendipi-tea-recap.mp4">Download the recap.</a></video></div>\n'''

    b += panel("Design result", f'''{car([(S+"result-1.jpg","Founders in conversation at the Serendipi-Tea connection wall"),(S+"result-2.jpg","Founders reacting during the game")], "3/2", "mid")}
<div class="lines" style="margin-top:28px"><div><b>Variety of conversation</b><span>Love, death, politics, insecurities, etc.</span></div><div><b>Variety of strong emotion</b><span>Laughter, reflection, surprise</span></div><div><b>Shortest playtime</b><span>35 min</span></div><div><b>Longest playtime</b><span>45 min</span></div></div>
<div class="sub-card" style="margin-top:24px"><p style="max-width:none">One of the more surprising outcomes was how quickly the founders' guards came down. Most of them spend their days pitching, networking, and performing a version of themselves built for a room full of investors or competitors. But once there was a vessel built strictly for connection, with no ask, no agenda, and nothing to prove, that professional mask seemed to just fall away. Conversations that started as polite small talk kept sliding into something more honest: grief, doubt, the parts of running a company nobody really talks about. It made the case that founders don't necessarily need more networking spaces. They need spaces that are explicitly not that.</p></div>''', step="5", v="detail")

    b += panel("Takeaways", '<div class="grid g3">' +
      sc("Rooting my work in user needs", "My group and I were unfamiliar with the experience of startup founders. This project stemmed directly from the conversations we had with them, and the pain points we noticed.") +
      sc("Designing for emotional impact", "This project taught me that meaningful design goes beyond solving logistical problems. It can create space for vulnerability, connection, and authentic human interaction.") +
      sc("Conversation as a designed experience", "This project reframed dialogue itself as something that can be intentionally crafted through prompts, pacing, environment, and material interaction.") + '</div>', step="6", v="detail")

    b += ifagain([
      ("Quantitative", "Define success metrics first", "Set them before testing: session length, cards played per session, and a 1 to 5 “I felt connected” rating after each game."),
      ("Experiment design", "Add a control", "Run a no-cards version of the same space to see whether the game, and not just the room, drove deeper conversation."),
      ("Qualitative rigor", "Code conversations with a rubric", "Tag topics on a simple depth scale (surface, personal, vulnerable) and have a teammate code a subset to check agreement."),
      ("Longitudinal", "Follow up a week later", "The goal was lasting connection, so I would check whether founders kept talking after the session.")])
    cs_page("case-study-serendipi-tea.html", "Serendipi-Tea",
      "Designing an innovation hub experience to foster authentic connection among startup founders in accelerator spaces.",
      [("Client", "StartX, Stanford"), ("Role", "Head User Researcher"), ("Timeline", "Apr – Jun 2025"), ("Team", "Team Jello (3 designers)")],
      hero, b, ("case-study-simone.html", "Simone Acc. Collection"),
      "Case study: a card-based conversation tool that helps startup founders at StartX build authentic connection.")

# ---------------------------------------------------------------- Simone
def build_simone():
    S = "img/simone/"
    P = lambda n: S + f"photo-{n}.jpg"
    hero = fig(S + "hero.jpg", "Green quilted handbag, Simone Acc. Collection", "hero-fig", style="aspect-ratio:16/9")
    hero = hero.replace('<img ', '<img style="object-position:center 38%" ')
    b = ""
    b += glance([("8", "weeks in Ui-Wang, South Korea"), ("2", "user groups profiled"), ("3", "concepts pitched to 0914"), ("4", "weeks of weekly physical samples")],
      ["Trend research (FW 26/27)", "Style guide", "User-group profiling", "Retail fieldwork", "Mood boarding", "Concept sketching", "Physical prototyping"])
    b += tldr_cards([
        ("The setup", "An 8-week internship in Ui-Wang, South Korea at Simone Acc. Collection, a luxury leather goods manufacturer, split between its in-house 0914 design team and a Tory Burch global sales team.", False),
        ("What I did", "I researched FW 26/27 trends, built mood boards, sketched, and pitched three concepts to the 0914 team. Then I made a physical sample every week for Tory Burch's sub-teams.", False),
        ("What I made", "Two of the pitched concepts: Interwoven, a design built around hand-woven construction, and Canvas, a silhouette with a custom-dyeable canvas panel.", True),
        ("What I took away", "Sketching isn't scary. It's just another way to convey ideas, however rough. It was the most I've ever sketched in my life.", False),
    ])
    b += f'<div class="grid g2" data-v="tldr">{fig(S+"final-pitch.jpg","Final concept pitch boards with sketches, mood boards, and leather samples","", style="aspect-ratio:4/3")}{fig(P("35"),"Final sample, week 1","", style="aspect-ratio:4/3").replace("<img ", "<img style=\"object-position:center 40%\" ")}</div>\n'
    b += more_btn()

    b += panel("Project overview", '<p class="lead">During an 8-week internship partnered with Stanford\'s Global Studies Program, I joined Simone Acc. Collection, a leather goods manufacturer based in Ui-Wang, South Korea, working across both their in-house design team (0914) and their Global Sales team (Tory Burch).</p>', v="detail")

    b += panel("Initial goals", '<div class="grid g4">' +
      sc("Develop a clearer design POV", "Refine my personal aesthetic by sketching, prototyping, and iterating on original samples.", "Goal 1") +
      sc("Expand market understanding", "Gain insight into Korean fashion trends and global consumer preferences to design for diverse markets.", "Goal 2") +
      sc("Strengthen design visualization", "Communicate ideas clearly through concept sketching and design pitch decks, moving efficiently from concept to sample.", "Goal 3") +
      sc("Experience Korea", "Make the most of my first time working and traveling abroad.", "Goal 4") + f'''</div>
<div class="block"><h3 class="sub-h">Understanding Simone</h3><div class="split top"><div class="stack"><span class="kicker">What is Simone?</span><p>Simone Acc. Collection is a leading Korean luxury handbag and accessories manufacturer, known for producing high-quality leather goods for global designer brands.</p>
<div class="grid g2">{fig(S+"photo-01.jpg","Simone Acc. Collection process photo","",style="aspect-ratio:1/1")}{fig(S+"photo-01b.jpg","0914 tag detail","",style="aspect-ratio:1/1")}</div></div>
<div class="stack"><span class="kicker">What is 0914?</span><p>0914 is Simone's own premium leather-goods brand, built to showcase the company's craftsmanship, material quality, and design expertise. The brand focuses on timeless, human-centered, small-batch design.</p></div></div></div>''', step="1", v="detail")

    b += '<section class="wing" data-v="detail"><span class="tag">Part 1</span><h2>0914: the design team</h2><p>Working within Simone\'s in-house design team on individual projects, translating seasonal trends into 0914\'s next collection.</p></section>\n'

    trends = [(S+f"trend-{i:02d}.jpg", f"FW 26/27 trend research slide {i}") for i in range(1, 13)]
    b += panel("Research and needfinding", f'''<div class="block"><h3 class="sub-h">Understanding trends</h3><div class="split">{car(trends, "16/9", contain=True)}
<div class="stack"><p>Using resources from Simone's design team, I researched proposed trends for the FW 26/27 season and built a style guide for the team to reference, thinking through general themes, color palettes, and silhouettes.</p><p><b>Common threads:</b> ornamentalism, functionality, pockets, and playful looks balanced with earth tones.</p></div></div></div>
<div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><div class="ug"><div><span class="kicker">User group: 0914</span><h3>0914 customers</h3><p class="hmw">How might we meld current fashion trends with 0914's brand?</p></div>
<p>0914 customers value artisan-level craftsmanship and high-quality materials. They struggle to find leather goods on the market that feel uniquely human, rather than designed for the mass market.</p></div></div>''', step="2", v="detail")

    mood = [(P(n), a) for n, a in [("08","Mood board: vintage handcrafted handbag"),("09","Mood board: Venice canal painting"),("10","Mood board: tooled leather bag with floral detail"),("11","Mood board: woven textile handbag"),("12","Mood board: woven leather strip swatch"),("13","Mood board: embossed floral leather bag")]]
    b += panel("Ideation", f'''<div class="block"><h3 class="sub-h">Mood boarding</h3><div class="split"><div class="stack"><p>Pulling from both FW 26/27 trends and elements of 0914's brand identity:</p>
<ul class="ticks"><li><b>Handcrafted</b> design</li><li><b>Geologic:</b> earth-tones and metallic elements</li><li><b>Intentional</b> design</li><li><b>Artistic</b> and vintage styling</li></ul>
<p>This board reflects a direction rooted in tactility, slow craftsmanship, and objects that carry a sense of history.</p></div>{car(mood, "4/5", "mid", contain=True)}</div></div>
<div class="block"><div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><h3 class="sub-h">Materials</h3><div class="split">{car([(P("16"),"Leather and material samples"),(P("17"),"Leather and material samples, detail")], "3/4", "narrow")}
<p>There was a plethora of fabrics at our disposal, ranging from cow, sheep, goat, and vegetable leather, as well as suedes and linings. The wide variety let us explore different textures, structures, and finishes while conceptualizing designs.</p></div></div></div>
<div class="block"><h3 class="sub-h">Sketching</h3><div class="split">{car([(P("18"),"Sketch of a woven handbag concept"),(P("19"),"Sketch of a canvas handbag concept")], "1/1", "mid")}
<div class="stack"><p>Based on the mood boards and materials I'd gathered, I began sketching ideas, leaning into “handcrafted design” through woven materials and canvas that could be custom-dyed to create unique patterns.</p><p>Contrast between materials mattered a lot to me here. It plays well into the resurgence of vintage fashion, and it's something I genuinely enjoy as a designer.</p></div></div></div>''', step="3", v="detail")

    b += trace("From research to design", ["Research", "What I learned", "Design response"], [
      ["FW 26/27 trend research", "Common threads: ornamentalism, functionality, pockets, and playful looks balanced with earth tones.", "A mood board built on handcrafted, geologic, intentional, and artistic cues."],
      ["0914 customer profile", "Customers value artisan-level craftsmanship and materials, and want pieces that feel human rather than mass-market.", "Interwoven, a hand-woven construction, and Canvas, a custom-dyeable panel."]],
      "How the research shaped the concepts I pitched.")
    b += panel("Final designs: 0914", f'''<div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><h3 class="sub-h">Final concepts</h3><div class="grid g2">{fig(P("20"),"Leather samples and sketches","",style="aspect-ratio:536/546")}{fig(S+"final-pitch.jpg","Final concept pitch boards","",style="aspect-ratio:4/3;align-self:center")}</div>
<p style="margin-top:20px">I created 3 sketches I felt could realistically be implemented in 0914's next seasonal collection, including <b>Interwoven</b>, a design highlighting hand-crafted construction through woven materials, and <b>Canvas</b>, a silhouette featuring a custom-dyeable canvas panel that gives each piece its own pattern-driven identity.</p></div>
<p style="margin-top:20px">At my final concept pitch, I presented my designs to 0914's design team: sketches, a digital mockup, mood boards, and leather samples of my proposed materials.</p>''', step="4", v="detail")

    b += '<section class="wing" data-v="detail"><span class="tag">Part 2</span><h2>Global Sales: Tory Burch</h2><p>Midway through the internship, I transitioned to Simone\'s Global Sales team, placed with Tory Burch for the remaining 4 weeks.</p></section>\n'

    b += panel("The transition", '''<div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><h3 class="sub-h">Global Sales at Simone</h3>
<p>Simone manufactures for multiple high-end brands, including Tory Burch, Michael Kors, Coach, and Kate Spade, translating each brand's design concepts into products built with Simone's materials, machinery, and technical expertise. I was placed with Tory Burch's Global Sales team for the remaining 4 weeks.</p>
<div class="chips"><span class="chip">Tory Burch</span><span class="chip">Michael Kors</span><span class="chip">Coach</span><span class="chip">Kate Spade</span></div></div>''', step="5", v="detail")

    b += panel("Needfinding", f'''<div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><div class="ug"><div><span class="kicker">User group: Tory Burch</span><h3>Young women (20s to 30s)</h3><p class="hmw">How can I create pieces that feel unique to me as a designer, while also satisfying our target audience?</p></div>
<p>Tory Burch customers are young, ambitious women stepping into their professional lives, looking for pieces polished yet versatile enough to carry them from the office to evening plans.</p></div></div>
<div class="block"><h3 class="sub-h">Market research</h3><div class="split"><div class="stack"><p>Visited a luxury department store and several galleries to get a sense of popular trends in the high-end leather accessory industry.</p>
<ul class="ticks"><li>Lots of hanging charms</li><li>Heavy usage of chains</li><li>High barrier to entry: pricing not very accessible for younger buyers</li></ul></div>
{car([(P("24"),"Market research in Seoul"),(P("25"),"Market research in Seoul")], "3/4", "narrow")}</div></div>''', step="6", v="detail")

    b += panel("Ideation and prototyping", f'''<div class="block"><h3 class="sub-h">Sketching and ideation</h3><div class="split">{car([(P("27"),"Sketch for a sub-team"),(P("28"),"Sketch for a sub-team")], "4/3", "mid", contain=True)}
<p>Each week, my task was to create one physical sample tailored to the sub-team I was assigned, while still bringing my own point of view as a designer, sketching broadly and experimenting with materials popular for that sub-team.</p></div></div>
<div class="block"><div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><h3 class="sub-h">Materials</h3><div class="split">{car([(P("29"),"Materials for Tory Burch samples"),(P("30"),"Materials for Tory Burch samples")], "3/4", "narrow")}
<p>As with 0914, there was a wide range of fabrics available: cow, sheep, goat, and vegetable leather, plus suedes and linings. The biggest difference: each Tory Burch sub-team used very specific, distinct materials, which I had to factor into every prototype.</p></div></div></div>
<div class="block"><h3 class="sub-h">Protos and patterns</h3><div class="grid g2">
<div class="sub-card"><span class="kicker">10-minute prototypes</span><p>One of my supervisors challenged me to grab a few scrap pieces of leather and construct a bag prototype from a sketch, in 10 minutes.</p><div style="margin-top:14px">{fig(P("31"),"10-minute leather prototype","",style="aspect-ratio:3/4")}</div></div>
<div class="sub-card"><span class="kicker">From sketches to digital models</span><p>Once sketches were finalized, they were passed to the Patterns team, who built digital models of the designs, ultimately sent to the Sample Room to be physically prototyped by the Stitch Masters.</p><div style="margin-top:14px">{fig(P("32"),"Digital pattern model","",style="aspect-ratio:3/4")}</div></div></div></div>
<div class="block"><div class="panel dark" style="border-radius:var(--r-inner);padding:30px"><h3 class="sub-h">Sampling</h3><div class="split">{car([(P("33"),"Sample in progress"),(P("34"),"Sample in progress")], "3/4", "narrow")}
<p>I checked in with the Stitch Masters as they worked from printed versions of the digital model, following up regularly to make sure things were on track, with occasional conversations about hand-feel, hardware choices, and general construction.</p></div></div></div>''', step="7", v="detail")

    b += panel("Final design: Global Sales", f'''<div class="grid g3">
<div>{fig(P("35"),"Week 1 sample","",style="aspect-ratio:3/4")}<p class="muted" style="margin-top:8px;font-weight:600">Week 1</p></div>
<div>{fig(P("37"),"Week 3 sample","",style="aspect-ratio:3/4")}<p class="muted" style="margin-top:8px;font-weight:600">Week 3</p></div>
<div>{fig(P("38"),"Week 4 sample","",style="aspect-ratio:3/4")}<p class="muted" style="margin-top:8px;font-weight:600">Week 4</p></div></div>''', step="8", v="detail")

    def refl(goal, title, imgs, text):
        ph = "".join(f'<img src="{s}" alt="{esc(a)}" loading="lazy">' for s, a in imgs)
        return f'<div class="sub-card reflect"><span class="kicker">Revisiting goal {goal}</span><h4>{title}</h4><div class="pair">{ph}</div><p>{text}</p></div>'
    b += panel("Reflections", '<div class="grid g2">' +
      refl("1", "A clearer design POV", [(P("39"),"Fashion show"),(P("40"),"Fashion show")], "Working alongside incredibly creative designers pushed me to trust my own instincts and articulate ideas with more clarity. I also got to attend a fashion show for the first time, a lifelong dream that expanded my creative perspective and shaped the direction of my own design voice.") +
      refl("2", "Cultural and market understanding", [(P("41"),"Seoul market research"),(P("42"),"Seoul market research")], "Conducting market research in Seoul, one of the trendiest fashion hubs in the world, let me observe emerging street styles and consumer behavior firsthand, strengthening my ability to spot broader global design trends.") +
      refl("3", "Design visualization skills", [(P("43"),"Sketching"),(P("44"),"Sketching")], "I learned that sketching isn't scary. It's just another way to convey ideas, however rough. This was the most I've ever sketched in my life, and I'm grateful I pushed myself further into that side of design.") +
      refl("4", "Experience Korea!", [(P("45"),"Seoul"),("img/photography/frame-07.jpg","Sea Temple, Sokcho, South Korea")], "Truly one of the most incredible experiences of my life. I explored Seoul, Anyang, Suwon, Sokcho, and Goryeong. Two months full of incredible people, food, and memories made.") + '</div>', step="9", v="detail")

    b += ifagain([
      ("Quantitative", "Rank trends by frequency", "Tally how often each trend appears across sources, so the style guide ranks themes instead of just listing them."),
      ("Preference testing", "Test concepts with the target user", "Use a short paired-comparison survey with young professionals to rank the sketches, rather than relying on my own read."),
      ("Fieldwork rigor", "Standardize store visits", "Use a simple observation sheet (product counts, price points, hardware) so findings can be compared across stores."),
      ("Process metrics", "Track iteration speed", "Log revisions and turnaround time for each sample to show how quickly every round improved.")])
    cs_page("case-study-simone.html", "Simone Acc. Collection",
      "Contributed to the design and development of luxury handbags and leather goods through concept ideation and prototyping.",
      [("Client", "Simone Acc. Collection"), ("Role", "Design and market research intern"), ("Timeline", "8 weeks, 2025"), ("Team", "Individual projects")],
      hero, b, ("case-study-node.html", "Node Foundation"),
      "Case study: an 8-week design internship at a luxury leather goods manufacturer in Ui-Wang, South Korea.")

# ---------------------------------------------------------------- Node
def build_node():
    N = "img/node/"
    hero = fig(N + "hero.jpg", "Visitors viewing a wall of digital art at Node Foundation", "hero-fig")
    hero = hero.replace('<img ', '<img style="object-position:center 25%" ')
    b = ""
    b += glance([("2", "exhibitions I helped install")],
      ["Visitor observation", "Guest-facing facilitation", "Exhibition install support", "Feedback loop to the team", "Spatial and experience analysis"])
    b += tldr_cards([
        ("What it is", "Node Foundation is a gallery dedicated to digital and on-chain art. I'm a Guest Experience Associate there, from June 2026 to now.", False),
        ("What I do", "I guide guests through new exhibitions, explain the art, and keep the gallery running: setup, guest assistance, and front desk coverage.", False),
        ("Beyond the floor", "I helped install two exhibitions, PXL by Kim Asendorf and Make Out by Maya Man and Luke Shannon, and supported marketing around each opening.", True),
        ("What I took away", "Guest experience turned out to be spatial design as much as hosting. Sightlines, lighting, and where I stood shaped whether someone felt comfortable getting curious.", False),
    ])
    b += more_btn()

    b += panel("Project overview", '<p class="lead">Node Foundation is a gallery dedicated to digital and on-chain art. As a Guest Experience Associate, I help visitors, many encountering this kind of art for the first time, actually understand and connect with what they\'re looking at.</p>', v="detail")
    b += panel("Guest experience", '''<h3 class="sub-h">Role at a glance</h3><ul class="ticks">
<li><span>Serve as the <b>primary point of contact</b> for guests navigating new exhibitions.</span></li>
<li><span>Explain artworks and help visitors engage with <b>digital and on-chain art</b>, often a genuinely new format for them.</span></li>
<li><span>Support day-to-day gallery operations, including <b>setup, guest assistance, and front desk coverage</b>.</span></li></ul>''', step="1", v="detail")
    b += panel("Exhibition support", f'''<p class="muted" style="margin-bottom:24px">Beyond hosting, I supported the installation process for two exhibitions during my time at Node.</p>
<div class="grid g2">
<div class="sub-card">{fig(N+"exhibit-pxl.jpg","PXL by Kim Asendorf","",style="aspect-ratio:1146/390;margin-bottom:16px;border-radius:16px")}<span class="kicker">Exhibition 1</span><h4>PXL by Kim Asendorf</h4><p>Helped with installation setup and was on the floor to guide guests through the piece once it opened to the public.</p></div>
<div class="sub-card">{fig(N+"exhibit-makeout.png","Make Out by Maya Man and Luke Shannon","",style="aspect-ratio:956/382;margin-bottom:16px;border-radius:16px")}<span class="kicker">Exhibition 2</span><h4>Make Out by Maya Man and Luke Shannon</h4><p>Supported installation logistics and served as a guide for visitors experiencing the piece for the first time.</p></div></div>''', step="2", v="detail")
    b += panel("Marketing support", '<div class="grid g3">' +
      sc("Exhibit promotion", "Assisted the team with marketing efforts around each exhibition opening.") +
      sc("On-the-ground content", "Helped capture moments from the gallery floor to support Node's social presence.") +
      sc("Guest feedback loop", "Passed along recurring visitor questions and reactions back to the team.") + '</div>', step="3", v="detail")
    b += trace("From observation to practice", ["What I observed", "How I responded"], [
      ["Many guests arrive without context for digital or on-chain art.", "Explain it clearly without over-explaining, meeting people where they are."],
      ["Layout shaped comfort: sightlines, lighting, and where I stood.", "Treated guest experience as spatial design as much as hosting."],
      ["Digital and on-chain art can feel intimidating on paper.", "Paced conversations and kept explanations light, so a visit felt digestible instead of like a lecture."]],
      "Small observations from the floor that changed how I host.")
    b += panel("Takeaways", '<div class="grid g2">' +
      sc("Translating new art forms", "A lot of guests walk in without much context for digital or on-chain art. Learning how to explain it clearly, without over-explaining, pulled directly from the same instincts I use as a Peer Advisor and TA: meeting someone where they are.") +
      sc("Seeing the full exhibition lifecycle", "Being on the install side and the guest-facing side of the same exhibitions gave me a much better sense of everything that happens between an artist's concept and a visitor's first reaction to it.") +
      sc("Designing for learning and connection", "Guest experience turned out to be spatial design as much as it was hosting. How a room is laid out (sightlines, lighting, where I stood relative to a piece) shaped whether someone felt comfortable getting curious or just walked past.") +
      sc("Making it enjoyable, not just educational", "Digital and on-chain art can feel intimidating on paper. Part of the job was translating that seriousness into something people could actually enjoy: pacing conversations and keeping explanations light so a visit felt digestible, not like a lecture.") + '</div>', step="4", v="detail")

    b += ifagain([
      ("Quantitative", "Add a two-question exit survey", "Ask “How comfortable did you feel with the art, 1 to 5?” and “What do you wish you had known?” to track change over time."),
      ("Qualitative", "Log recurring questions", "Tally the questions guests ask most, turn the top ones into a short wall guide, and see whether the same questions fade."),
      ("Observation", "Use a simple protocol", "Record dwell time at each work and where guests hesitate, to test how layout and my positioning affect engagement."),
      ("Comparison", "Compare guided and unguided visits", "A small side-by-side would show whether a short welcome changes how long and how deeply people engage.")])
    cs_page("case-study-node.html", "Node Foundation",
      "Supporting visitor experience and exhibition operations at a gallery for digital and on-chain art.",
      [("Client", "Node Foundation"), ("Role", "Guest Experience Associate"), ("Timeline", "Jun 2026 to present"), ("Focus", "Visitor engagement")],
      hero, b, ("captured-moments.html", "Captured Moments"),
      "Case study: guest experience and exhibition support at Node Foundation, a gallery for digital and on-chain art.")

# ---------------------------------------------------------------- Captured moments
FRAMES = [
 ("01","Sunset at Sunset Cliffs","The very first photo I took on my camera. I was with my 3 best friends from home having a picnic at our favorite spot, Sunset Cliffs. It was the first time we had seen each other since our first years at college. There was so much warmth and laughter.","San Diego, CA","July 2024"),
 ("02","An Asian grocery store","A grocery store in National City. I was overwhelmed with a feeling of nostalgia as soon as I walked through the door.","San Diego, CA","August 2024"),
 ("03","Rubber duck","A little rubber duck I saw on a hike in Santa Cruz. It called my name, so I made it my muse.","Santa Cruz, CA","March 2025"),
 ("04","Starfield Library","This was one of my “must see” spots when I visited Korea. It definitely didn’t disappoint. I brought my copy of The Little Prince and did a quick read before taking the train back to my apartment.","Suwon, South Korea","August 2025"),
 ("05","The palace guard","Gyeongbokgung Palace was truly a surreal experience. I took this photo at the “Changing of the Guards Ceremony” and I can still feel the drum beat pounding in my ear.","Seoul, South Korea","June 2025"),
 ("06","Bridge with Kimsoo","Every Friday during my internship at Simone, I’d be sent on K-Culture excursions. The one photographed here wouldn’t have been possible without our fantastic guide, Kimsoo. He picked us up at 7AM and we didn’t get back until 9PM. He recommended this bridge, and it was an incredible sight.","Paju, South Korea","July 2025"),
 ("07","Sea temple","A little weekend trip to one of my favorite spots in South Korea, Sokcho. Beautiful beaches, mountains, and seafood. I was surrounded by incredible friends who weren’t afraid of a little cliffside.","Sokcho, South Korea","July 2025"),
 ("08","Botanical garden","I truly was just moved by these 5 empty chairs. All differently colored, but facing the same sights. I sat down in the middle chair, and imagined my 4 best friends next to me.","Seoul, South Korea","August 2025"),
 ("09","Balboa Park","Growing up, my parents would take me to Free Museum Tuesdays at Balboa Park. I continue to revisit whenever I’m home because I have so many fond memories. The architecture is always breathtaking any direction you look.","San Diego, CA","September 2025"),
 ("10","Singing man","For a little bit of context: before I had visited Korea, I had just watched the movie Past Lives with one of my best friends. I decided to go on a hike after getting off at a random station on Line 4. It was a beautiful path leading to a museum, and at that museum the statues from Past Lives were being exhibited.","Gwacheon, South Korea","July 2025"),
 ("11","Fisherman","On a hike for two of my friends’ birthdays, we stumbled upon these fishermen in the distance. As we watched from the cliffs I was mesmerized by the sight. I have such fond memories of that day.","Big Sur, CA","February 2026"),
 ("12","Two phones","For Spring Break 2026, I road-tripped from Maryland to Stanford. My last stop before campus was Santa Cruz, to visit my best friend. This is a photo of both of our phones and my wired earbuds at the beach.","Santa Cruz, CA","March 2026"),
]

def build_photos():
    cards = ""
    for n, title, story, place, when in FRAMES:
        cards += f'''<div class="frame-card" tabindex="0" role="button" aria-pressed="false" aria-label="Frame {n}: {esc(title)}. Press to flip and read the story." data-tip="Click to flip and read the story">
<div class="frame-in">
<div class="face front"><img src="img/photography/frame-{n}.jpg" alt="{esc(title)}, {esc(place)}" loading="lazy"><span class="num">Frame {n}</span><button class="exp" type="button" aria-label="View full image">{EXPAND}</button><span class="flip">Flip for the story</span></div>
<div class="face back"><span class="kicker">The story</span><h3>{esc(title)}</h3><p>{esc(story)}</p><div class="where"><span>{esc(place)}</span><span>{esc(when)}</span></div></div>
</div></div>
'''
    body = f'''<section class="panel"><p class="lead">Capturing moments is one of my favorite pastimes. I love getting to reflect on memories later. This isn't really a project, it's more of a running archive. Every frame below has a story on the back of it.</p></section>
<div class="frames">{cards}</div>
'''
    cs_page("captured-moments.html", "Captured Moments",
      "Selected frames from a Kodak PixPro FZ55, each one filed away with the story behind it.",
      [("Camera", "Kodak PixPro FZ55"), ("Format", "Digital camera"), ("Practice", "Ongoing"), ("Frames", "12 selected")],
      "", body, ("index.html#side-quests", "Back to the side quests"),
      "A running archive of digital camera photos, each with the story behind it.", show_toggle=False, back=("index.html#side-quests", "Side quests"))

# ---------------------------------------------------------------- redirects for old URLs
def redirect(fname, to):
    open(os.path.join(OUT, fname), "w").write(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Redirecting…</title><meta http-equiv="refresh" content="0; url={to}"><link rel="canonical" href="{to}"><script>location.replace("{to}")</script></head><body><a href="{to}">Continue</a></body></html>')

LIGHTBOX = '<div class="lightbox" id="lightbox" role="dialog" aria-label="Full image"><button type="button" aria-label="Close">✕</button><img alt=""></div>'

def write_index():
    out = head(HOME_TITLE, HOME_DESC) + FILTER + "\n"
    for route, v in VIEWS.items():
        v["html"] = v["html"].replace("{id}", route)
        out += f'<div class="view" data-route="{route}" data-title="{esc(v["title"])}" data-desc="{esc(v["desc"])}"{"" if route == "home" else " hidden"}>{rewrite_links(v["html"])}</div>\n'
    out += f"</div>\n{LIGHTBOX}\n{AUDIO}\n<script src=\"app.js\"></script>\n</body>\n</html>\n"
    open(os.path.join(OUT, "index.html"), "w").write(out)

if __name__ == "__main__":
    build_home(); build_serendipi(); build_simone(); build_node(); build_photos(); build_community(); build_graphics()
    write_index()
    # Old URLs keep working: they forward into the single-page site.
    redirect("about.html", "index.html#about")
    redirect("case-study-template.html", "index.html#/serendipi-tea")
    for fname, route in FILE_ROUTE.items():
        if route in VIEWS: redirect(fname, f"index.html#/{route}")
    print("built", ", ".join(VIEWS))
