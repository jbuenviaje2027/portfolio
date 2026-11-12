# Josh Buenviaje portfolio (bento redesign)

Static site. Open `index.html`, or push the folder to GitHub Pages as-is.

## Files
- `index.html` : the entire site (home bento, three case studies with a TL;DR / Detailed toggle, Captured Moments, Weaver of community, and Graphic design). Add events to the `EVENTS` list in `build.py`.
- `about.html`, `case-study-template.html` : redirects, so old links keep working
- `styles.css`, `app.js` : shared styling and behavior
- `img/`, `videos/` : your original assets
- `build.py` : generates every HTML page. All copy lives in here.

## Editing
Change text or add tiles in `build.py`, then run `python3 build.py`.
- A tile's hover tidbit is its `tip` argument.
- `data-in="all work"` controls which tabs a tile appears in.
- On case study pages, `data-v="tldr"` shows only in TL;DR, `data-v="detail"` only in Detailed, and no attribute means both.

## Favorites lists
The ranked lists behind the About tiles live in the `LISTS` dict in `build.py`. Items marked `todo` show as dashed placeholders.

## Music keeps playing between pages
The whole site is one document (`index.html`). Pages are `<div class="view">` blocks that show and hide, with addresses like `index.html#/simone`, so the browser never reloads and the Spotify player is never interrupted. This works on GitHub Pages and when opened straight from disk. The old file names (`case-study-simone.html`, `about.html`, etc.) are tiny redirect pages so existing links still work.

Note: `build.py` generates `index.html`, so always edit copy in `build.py` and re-run it rather than editing `index.html` by hand.

## Adding graphic design pieces
Put the image in `img/graphic-design/` (JPG, about 1800px on the long side), then add one line to the `GRAPHICS` list in `build.py` with its `file`, `title`, and `note`, and run `python3 build.py`. The order of the list is the order on the page, and the first four pieces appear in the home tile.

## Road trip photos
The road trip photos are in `img/roadtrip/` and listed, in route order, in the `ROADTRIP` list in `build.py` (file, caption, description). To add or reorder photos, put the JPG in that folder, edit the list, and run `python3 build.py`.
The shirt gallery photos are `img/about/shirt-little.jpg` and `img/about/shirt-now.jpg`.
